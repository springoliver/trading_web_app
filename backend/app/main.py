from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth import router as auth_router
from app.api.routes.trade import router as trade_router
from app.websocket.price_ws import price_stream
from app.services.auth_service import ensure_broker_session, validate_session_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    print("Starting application...")
    try:
        if ensure_broker_session():
            print("Tastytrade session established.")
        else:
            print("⚠️  Tastytrade session unavailable at startup.")
        print("ℹ️  Paper mode stays available for demo/testing.")
        print("ℹ️  Check TASTY_USERNAME and TASTY_PASSWORD in .env if live mode fails.")
    except Exception as e:
        print(f"⚠️  Broker startup session failed: {e}")

app.include_router(trade_router, prefix="/trade")
app.include_router(auth_router, prefix="/auth")

@app.websocket("/ws/{symbol}")
async def ws_endpoint(ws: WebSocket, symbol: str):
    token = ws.query_params.get("token")
    option_type = ws.query_params.get("option_type", "call").lower()
    if option_type not in ("call", "put"):
        option_type = "call"

    if not token or not validate_session_token(token):
        await ws.close(code=1008, reason="Unauthorized")
        return

    await price_stream(ws, symbol, option_type)