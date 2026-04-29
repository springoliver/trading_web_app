from fastapi import WebSocket
import robin_stocks.robinhood as rh
import asyncio

async def price_stream(ws: WebSocket, symbol: str):
    await ws.accept()
    while True:
        price = rh.stocks.get_latest_price(symbol)[0]
        await ws.send_json({"price": price})
        await asyncio.sleep(0.2)