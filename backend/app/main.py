from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth import router as auth_router
from app.api.routes.trade import router as trade_router
from app.websocket.price_ws import price_stream
from app.services.auth_service import login

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust if frontend port differs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    print("Starting application...")
    try:
        login()
        print("Robinhood login successful.")
    except Exception as e:
        print(f"⚠️  Robinhood login on startup failed: {e}")
        print("ℹ️  The app will attempt to login when you place your first trade.")
        print("ℹ️  Check your RH_USERNAME and RH_PASSWORD in .env if trades fail.")

app.include_router(trade_router, prefix="/trade")
app.include_router(auth_router, prefix="/auth")

@app.websocket("/ws/{symbol}")
async def ws_endpoint(ws: WebSocket, symbol: str):
    await price_stream(ws, symbol)