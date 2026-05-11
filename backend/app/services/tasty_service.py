from datetime import datetime, timedelta
import httpx
from app.core.config import settings
from app.services.auth_service import ensure_broker_session, get_broker_session_token, get_last_login_error


def _headers():
    token = get_broker_session_token()
    return {"Authorization": token} if token else {}


def _require_session():
    if not ensure_broker_session():
        raise Exception(get_last_login_error() or "Tastytrade authentication unavailable")


def _next_expiration_1dte() -> str:
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def get_underlying_price(symbol: str) -> float:
    _require_session()
    # Endpoint availability can differ between sandbox/live plans.
    try:
        response = httpx.get(
            f"{settings.TASTY_API_BASE}/market-data/quotes/{symbol.upper()}",
            headers=_headers(),
            timeout=8.0,
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        for key in ("last", "mark", "close", "price"):
            value = data.get(key)
            if value is not None:
                return float(value)
    except Exception as exc:
        raise Exception(f"Failed to fetch underlying quote from Tastytrade: {exc}") from exc
    raise Exception("No usable quote found in Tastytrade response")


def get_nearest_option(symbol: str, option_type: str):
    _require_session()
    expiration = _next_expiration_1dte()
    option_type = option_type.lower()
    # Contract-discovery endpoint structures vary by account permissions.
    response = httpx.get(
        f"{settings.TASTY_API_BASE}/option-chains/{symbol.upper()}",
        headers=_headers(),
        timeout=10.0,
    )
    response.raise_for_status()
    chain = response.json().get("data", {})
    strikes = chain.get("strikes") or []
    if not strikes:
        raise Exception("No option strikes returned by Tastytrade")
    underlying = get_underlying_price(symbol)
    nearest_strike = min(strikes, key=lambda s: abs(float(s) - underlying))
    return {
        "chain_symbol": symbol.upper(),
        "strike_price": str(nearest_strike),
        "expiration_date": expiration,
        "type": option_type,
    }
