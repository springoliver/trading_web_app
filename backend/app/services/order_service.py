from app.services.auth_service import ensure_broker_session
from app.services import paper_service

def _ensure_login():
    """Ensure broker session is active for order submission."""
    return ensure_broker_session()

def buy_option(option, quantity=1):
    # Phase 1 migration: keep deterministic paper execution while broker
    # auth/session is moved fully to Tastytrade live order routing.
    _ensure_login()
    return paper_service.open_position(
        symbol=option["chain_symbol"],
        option_type=option["type"],
        quantity=quantity,
        side="long",
    )

def sell_option_open(option, quantity=1):
    _ensure_login()
    return paper_service.open_position(
        symbol=option["chain_symbol"],
        option_type=option["type"],
        quantity=quantity,
        side="short",
    )


def close_option(symbol, option_type, expiration_date, strike, quantity=1, market_price=None, side="long"):
    _ensure_login()
    return paper_service.close_position(
        symbol=symbol,
        option_type=option_type,
        expiration_date=expiration_date,
        strike=strike,
        quantity=quantity,
        side=side,
    )