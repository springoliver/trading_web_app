from fastapi import WebSocket
import robin_stocks.robinhood as rh
import asyncio
from starlette.websockets import WebSocketDisconnect
from app.services.options_service import get_option_payload

async def price_stream(ws: WebSocket, symbol: str, option_type: str):
    await ws.accept()
    try:
        while True:
            try:
                payload = get_option_payload(symbol, option_type)
                await ws.send_json({
                    "underlying_price": payload["underlying_price"],
                    "option": payload["option"],
                })
            except Exception:
                # Keep sending at least underlying price even if option lookup fails.
                price = rh.stocks.get_latest_price(symbol)[0]
                await ws.send_json({"underlying_price": float(price)})
            await asyncio.sleep(0.2)
    except (asyncio.CancelledError, WebSocketDisconnect):
        # Normal during server shutdown/reload.
        return