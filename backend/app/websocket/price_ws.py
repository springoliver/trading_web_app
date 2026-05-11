from fastapi import WebSocket
import asyncio
from starlette.websockets import WebSocketDisconnect
from app.services.options_service import get_option_payload

async def price_stream(ws: WebSocket, symbol: str, option_type: str):
    await ws.accept()
    try:
        while True:
            payload = get_option_payload(symbol, option_type)
            await ws.send_json({
                "underlying_price": payload["underlying_price"],
                "option": payload["option"],
            })
            await asyncio.sleep(0.2)
    except (asyncio.CancelledError, WebSocketDisconnect):
        # Normal during server shutdown/reload.
        return