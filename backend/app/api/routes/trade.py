from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from time import perf_counter
from app.core.security import extract_bearer_token
from app.services.auth_service import validate_session_token
from app.services.options_service import get_closest_option, get_option_payload, list_open_positions
from app.services.order_service import buy_option, sell_option_open, close_option

router = APIRouter()


def get_current_user(authorization: str | None = Header(None)):
    token = extract_bearer_token(authorization)
    if not validate_session_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token


class BuyRequest(BaseModel):
    symbol: str
    option_type: str
    quantity: int = 1


class CloseRequest(BaseModel):
    symbol: str
    option_type: str
    strike: str
    expiration_date: str
    quantity: int = 1
    market_price: float | None = None
    side: str = "long"

@router.get('/price')
def price(symbol: str, option_type: str, user: str = Depends(get_current_user)):
    try:
        return get_option_payload(symbol, option_type)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to load option data from broker: {str(exc)}",
        ) from exc


@router.get('/speed-test')
def speed_test(symbol: str, option_type: str, user: str = Depends(get_current_user)):
    try:
        start = perf_counter()
        payload = get_option_payload(symbol, option_type)
        elapsed_ms = (perf_counter() - start) * 1000
        return {
            "symbol": payload["symbol"],
            "server_latency_ms": round(elapsed_ms, 2),
            "target_ms": 250,
            "pass": elapsed_ms < 250,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Speed test unavailable while broker auth is down: {str(exc)}",
        ) from exc


@router.post("/buy")
def buy(request: BuyRequest, user: str = Depends(get_current_user)):
    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be >= 1")
    option = get_closest_option(request.symbol, request.option_type)
    order = buy_option(option, quantity=request.quantity)
    return {"order": order}


class SellRequest(BaseModel):
    symbol: str
    option_type: str
    quantity: int = 1


@router.post("/sell")
def sell(request: SellRequest, user: str = Depends(get_current_user)):
    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be >= 1")
    option = get_closest_option(request.symbol, request.option_type)
    order = sell_option_open(option, quantity=request.quantity)
    return {"order": order}


@router.post("/close")
def close(request: CloseRequest, user: str = Depends(get_current_user)):
    order = close_option(
        symbol=request.symbol,
        option_type=request.option_type,
        expiration_date=request.expiration_date,
        strike=request.strike,
        quantity=request.quantity,
        side=request.side,
        market_price=request.market_price,
    )
    return {"order": order}


@router.get('/positions')
def positions(user: str = Depends(get_current_user)):
    try:
        return {"positions": list_open_positions()}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to load positions from broker: {str(exc)}",
        ) from exc