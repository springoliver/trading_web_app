from datetime import datetime, timedelta
from app.services.auth_service import ensure_broker_session
from app.services import paper_service
from app.services import tasty_service


def _ensure_login():
    """Ensure broker session exists for market/position reads."""
    return ensure_broker_session()


def get_next_expiration(symbol):
    if not _ensure_login():
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return tasty_service._next_expiration_1dte()


def get_closest_option(symbol, option_type):
    if not _ensure_login():
        paper = paper_service.get_option_payload(symbol, option_type)
        return {
            "chain_symbol": paper["symbol"],
            "strike_price": paper["option"]["strike_price"],
            "expiration_date": paper["option"]["expiration_date"],
            "type": option_type,
        }
    try:
        return tasty_service.get_nearest_option(symbol, option_type)
    except Exception:
        paper = paper_service.get_option_payload(symbol, option_type)
        return {
            "chain_symbol": paper["symbol"],
            "strike_price": paper["option"]["strike_price"],
            "expiration_date": paper["option"]["expiration_date"],
            "type": option_type,
        }


def get_option_payload(symbol, option_type):
    if not _ensure_login():
        return paper_service.get_option_payload(symbol, option_type)
    try:
        option = get_closest_option(symbol, option_type)
        underlying_price = tasty_service.get_underlying_price(symbol)
        mark_price = max(0.01, round(abs(underlying_price - float(option["strike_price"])) * 0.1 + 0.2, 2))
        return {
            "symbol": symbol.upper(),
            "underlying_price": underlying_price,
            "option": {
                "strike_price": option["strike_price"],
                "expiration_date": option["expiration_date"],
                "option_type": option_type,
                "mark_price": mark_price,
                "bid_price": round(max(0.01, mark_price - 0.03), 2),
                "ask_price": round(mark_price + 0.03, 2),
            },
        }
    except Exception:
        return paper_service.get_option_payload(symbol, option_type)


def list_open_positions():
    # Until full Tastytrade position mapping is added, keep a reliable
    # paper-position ledger so UI behavior is stable for client demos.
    return paper_service.list_positions()