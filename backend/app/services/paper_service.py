import time
import random
import uuid
from datetime import datetime, timedelta


_paper_prices = {}
_paper_positions = []


def _next_price(symbol: str) -> float:
    symbol = symbol.upper()
    seed = _paper_prices.get(symbol, 180.0)
    drift = random.uniform(-0.6, 0.6)
    next_value = max(5.0, seed + drift)
    _paper_prices[symbol] = next_value
    return round(next_value, 2)


def _next_expiration_1dte() -> str:
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def get_option_payload(symbol: str, option_type: str):
    symbol = symbol.upper()
    option_type = option_type.lower()
    underlying = _next_price(symbol)
    strike = round(underlying)
    mark = max(0.1, round(abs(underlying - strike) * 0.15 + random.uniform(0.2, 0.8), 2))
    bid = max(0.01, round(mark - 0.03, 2))
    ask = round(mark + 0.03, 2)
    expiration = _next_expiration_1dte()
    return {
        "symbol": symbol,
        "underlying_price": underlying,
        "option": {
            "strike_price": str(strike),
            "expiration_date": expiration,
            "option_type": option_type,
            "mark_price": mark,
            "bid_price": bid,
            "ask_price": ask,
        },
    }


def list_positions():
    updated = []
    for p in _paper_positions:
        payload = get_option_payload(p["symbol"], p["option_type"])
        mark = payload["option"]["mark_price"]
        qty = p["quantity"]
        avg = p["average_price"]
        side = p["side"]
        if side == "long":
            pl = (mark - avg) * qty * 100
        else:
            pl = (avg - mark) * qty * 100
        new_p = dict(p)
        new_p["market_price"] = round(mark, 2)
        new_p["unrealized_pl"] = round(pl, 2)
        updated.append(new_p)
    return updated


def open_position(symbol: str, option_type: str, quantity: int, side: str):
    payload = get_option_payload(symbol, option_type)
    option = payload["option"]
    position = {
        "id": str(uuid.uuid4()),
        "symbol": symbol.upper(),
        "option_type": option_type.lower(),
        "strike_price": option["strike_price"],
        "expiration_date": option["expiration_date"],
        "quantity": int(quantity),
        "side": side,
        "average_price": option["mark_price"],
        "market_price": option["mark_price"],
        "unrealized_pl": 0.0,
        "opened_at": int(time.time()),
    }
    _paper_positions.append(position)
    return {
        "id": f"paper-{uuid.uuid4()}",
        "status": "filled",
        "mode": "paper",
        "position": position,
    }


def close_position(symbol: str, option_type: str, expiration_date: str, strike: str, quantity: int, side: str):
    remaining = []
    closed = False
    for p in _paper_positions:
        same = (
            p["symbol"] == symbol.upper()
            and p["option_type"] == option_type.lower()
            and p["expiration_date"] == expiration_date
            and str(p["strike_price"]) == str(strike)
            and p["side"] == side
        )
        if same and not closed:
            closed = True
            continue
        remaining.append(p)
    _paper_positions.clear()
    _paper_positions.extend(remaining)
    return {
        "id": f"paper-{uuid.uuid4()}",
        "status": "filled",
        "mode": "paper",
        "closed": closed,
        "quantity": int(quantity),
    }
