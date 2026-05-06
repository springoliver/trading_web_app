# RH Trader

Local-first Robinhood options trader with:
- Fast Vue 3 frontend (`frontend/`)
- FastAPI backend (`backend/`)
- Private login + 2FA gate
- 1 DTE nearest-strike buy/sell
- Live underlying + option mark feed (<250ms target)
- One-click close (`❌`) for open option positions

## Requirement coverage

- Private access: app login + 2FA + bearer-token protected APIs + authenticated WebSocket.
- Speed: backend sends quote updates every 200ms and exposes a speed test endpoint.
- Trading flow: buy/sell opens nearest strike for the selected `call` or `put`, and close removes positions once order is sent.
- No chart dependency: UI focuses on trading ticket + live panel.

## Setup

### 1) Backend install

```powershell
cd C:\Users\Administrator\Videos\trading\rh-trader\backend
pip install -r requirements.txt
```

### 2) Create `.env`

Copy template:

```powershell
cd C:\Users\Administrator\Videos\trading\rh-trader\backend
copy .env.example .env
```

Then edit `backend/.env`.

## How to get each `.env` value

```dotenv
RH_USERNAME=
RH_PASSWORD=
RH_DEVICE_TOKEN=
SECRET_KEY=
APP_USERNAME=
APP_PASSWORD=
APP_2FA_SECRET=
APP_TOKEN_TTL_SECONDS=28800
```

- `RH_USERNAME`: Robinhood account login email.
- `RH_PASSWORD`: Robinhood account password.
- `RH_DEVICE_TOKEN`: optional; keep blank unless Robinhood requires a known device token.
- `SECRET_KEY`: long random application secret (generate via Python: `python -c "import secrets; print(secrets.token_urlsafe(48))"`).
- `APP_USERNAME`: username for this local app login (not Robinhood username).
- `APP_PASSWORD`: strong password for local app login.
- `APP_2FA_SECRET`: **Base32 TOTP seed** used by authenticator apps (Google Authenticator/Authy/1Password).  
  - Generate one: `python -c "import pyotp; print(pyotp.random_base32())"`
  - Add it to authenticator app manually.
  - Use the rotating 6-digit code from that app on login.
  - If you set a short numeric value (example `123456`), backend treats it as static fallback code (not recommended).
- `APP_TOKEN_TTL_SECONDS`: session lifetime in seconds (default 8 hours).

## 3) Run backend

```powershell
cd C:\Users\Administrator\Videos\trading\rh-trader\backend
python run.py
```

Backend URL: `http://127.0.0.1:8000`

## 4) Run frontend

```powershell
cd C:\Users\Administrator\Videos\trading\rh-trader\frontend
npm install
npm run dev
```

Open the local URL shown by Vite (usually `http://127.0.0.1:5173` or `http://localhost:5173`).

## Usage

1. Login with `APP_USERNAME` / `APP_PASSWORD` / current 2FA code.
2. Choose symbol (`SPY`, `AAPL`, etc), option type (`call` / `put`), quantity.
3. Click `BUY` or `SELL` for nearest strike 1 DTE contract.
4. Use `❌ Close` beside a position to close immediately.
5. Watch:
   - Underlying price (live)
   - Option mark (live)
   - Open position P/L (refreshes continuously)
   - Speed test result (`/trade/speed-test`, target <250ms)

## Paper/safe testing recommendation

Robinhood does not offer true options paper trading through official APIs. For safer testing:
- Start with the smallest possible contract quantity.
- Use symbols with tight spreads/liquidity.
- Test in market hours with stable connectivity.
- Validate order payloads and pricing logic before increasing size.

## Security notes

- Keep `.env` local and private; never commit credentials.
- Run only on localhost/private network unless you add TLS, firewall rules, and stronger auth controls.
