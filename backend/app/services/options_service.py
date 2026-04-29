import robin_stocks.robinhood as rh
from datetime import datetime, timedelta


def get_next_expiration(symbol):
    dates = rh.get_chains(symbol)['expiration_dates']
    tomorrow = (datetime.now() + timedelta(days=1))
    return min(dates, key=lambda d: abs(
        datetime.strptime(d, "%Y-%m-%d") - tomorrow
    ))


def get_closest_option(symbol, option_type):
    price = float(rh.stocks.get_latest_price(symbol)[0])
    expiration = get_next_expiration(symbol)
    options = rh.find_options_by_expiration(
        symbol,
        expirationDate=expiration,
        optionType=option_type
    )
    return min(options, key=lambda x: abs(
        float(x['strike_price']) - price
    ))


def get_option_payload(symbol, option_type):
    price = float(rh.stocks.get_latest_price(symbol)[0])
    expiration = get_next_expiration(symbol)
    option = get_closest_option(symbol, option_type)
    market_data = rh.get_option_market_data(symbol, expiration, option['strike_price'], option_type)
    mark_price = market_data.get('mark_price') or market_data.get('adjusted_mark_price') or market_data.get('last_trade_price')
    return {
        "symbol": symbol,
        "underlying_price": price,
        "option": {
            "strike_price": option['strike_price'],
            "expiration_date": option['expiration_date'],
            "option_type": option_type,
            "mark_price": float(mark_price) if mark_price is not None else None,
            "bid_price": market_data.get('bid_price'),
            "ask_price": market_data.get('ask_price'),
        },
    }


def list_open_positions():
    raw_positions = rh.get_open_option_positions()
    positions = []
    for position in raw_positions or []:
        try:
            raw_quantity = float(position.get('quantity', 0))
        except (TypeError, ValueError):
            raw_quantity = 0.0
        side = "long" if raw_quantity >= 0 else "short"
        quantity = int(abs(raw_quantity))
        market_price = position.get('mark_price') or position.get('adjusted_mark_price') or position.get('last_trade_price')
        average_price = position.get('average_price')
        current_price = float(market_price) if market_price else 0.0
        avg_price = float(average_price) if average_price else 0.0
        unrealized_pl = None
        if avg_price:
            if side == "long":
                unrealized_pl = (current_price - avg_price) * quantity * 100
            else:
                unrealized_pl = (avg_price - current_price) * quantity * 100
        positions.append({
            "symbol": position.get('chain_symbol'),
            "option_type": position.get('option_type'),
            "strike_price": position.get('strike_price'),
            "expiration_date": position.get('expiration_date'),
            "quantity": quantity,
            "side": side,
            "average_price": avg_price,
            "market_price": current_price,
            "unrealized_pl": unrealized_pl,
        })
    return positions