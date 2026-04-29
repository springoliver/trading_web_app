import robin_stocks.robinhood as rh

def buy_option(option, quantity=1):
    price = _get_option_order_price(
        symbol=option['chain_symbol'],
        expiration_date=option['expiration_date'],
        strike=option['strike_price'],
        option_type=option['type'],
        side='buy',
    )
    return rh.order_buy_option_limit(
        positionEffect="open",
        creditOrDebit="debit",
        price=price,
        symbol=option['chain_symbol'],
        quantity=quantity,
        expirationDate=option['expiration_date'],
        strike=option['strike_price'],
        optionType=option['type'],
    )

def sell_option_open(option, quantity=1):
    price = _get_option_order_price(
        symbol=option['chain_symbol'],
        expiration_date=option['expiration_date'],
        strike=option['strike_price'],
        option_type=option['type'],
        side='sell',
    )
    return rh.order_sell_option_limit(
        positionEffect="open",
        creditOrDebit="credit",
        price=price,
        symbol=option['chain_symbol'],
        quantity=quantity,
        expirationDate=option['expiration_date'],
        strike=option['strike_price'],
        optionType=option['type'],
    )


def close_option(symbol, option_type, expiration_date, strike, quantity=1, market_price=None, side="long"):
    price = float(market_price) if market_price else None
    if price is None:
        option_data = rh.get_option_market_data(symbol, expiration_date, strike, option_type)
        price = float(option_data.get('mark_price', option_data.get('last_trade_price', 0)))
    quantity = abs(quantity)
    if side == "short":
        return rh.order_buy_option_limit(
            positionEffect="close",
            creditOrDebit="debit",
            price=price,
            symbol=symbol,
            quantity=quantity,
            expirationDate=expiration_date,
            strike=strike,
            optionType=option_type,
        )

    return rh.order_sell_option_limit(
        positionEffect="close",
        creditOrDebit="credit",
        price=price,
        symbol=symbol,
        quantity=quantity,
        expirationDate=expiration_date,
        strike=strike,
        optionType=option_type,
    )


def _get_option_order_price(symbol, expiration_date, strike, option_type, side):
    market_data = rh.get_option_market_data(symbol, expiration_date, strike, option_type)
    if side == 'buy':
        price = market_data.get('ask_price') or market_data.get('mark_price') or market_data.get('last_trade_price')
    else:
        price = market_data.get('bid_price') or market_data.get('mark_price') or market_data.get('last_trade_price')
    if price is None:
        return 0.0
    return float(price)