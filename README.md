# RH Trader

A local Vuexy-based frontend with a FastAPI backend for private Robinhood option trading.

## Project structure

- `frontend/` - Vue 3 + Vuetify (Vuexy) interface
- `backend/` - FastAPI backend handling app login, Robinhood authentication, live price feed, option lookup, buy, sell, and close orders

## Setup

### Backend

1. Install Python dependencies:

```powershell
cd c:\Users\...\rh-trader\backend
pip install -r requirements.txt
```

2. Fill in `backend/.env` with your Robinhood credentials and app auth secrets:

```dotenv
RH_USERNAME=your_robinhood_email
RH_PASSWORD=your_robinhood_password
RH_TOTP_SECRET=your_robinhood_totp_secret
SECRET_KEY=supersecret
APP_USERNAME=admin
APP_PASSWORD=admin
APP_2FA_SECRET=your_app_2fa_secret
```

3. Start the backend locally:

```powershell
cd c:\Users\...\rh-trader\backend
python run.py
```

The backend listens on `http://127.0.0.1:8000`.

### Frontend
 ## develop mode
1. Install dependencies:

```powershell
frontend path (example: cd c:\Users\...\rh-trader\frontend)
npm install
```

2. Start the frontend dev server:

```powershell
npm run dev
```

3. Open the local URL shown in the terminal, typically `http://localhost:5173`.

## production mode
1. Start the frontend pro server:
```powershell
frontend path (example: cd c:\Users\...\rh-trader\frontend\dist)
php -S 127.0.0.1:5173
```

2. Open the local URL shown in the terminal, typically `http://localhost:5173`.

## Usage

- Login with your app credentials and 2FA code.
- The trading page uses a WebSocket price feed from the backend.
- `Buy` and `Sell` submit orders for the nearest 1 DTE strike in the selected option type.
- `❌ Close` exits both long and short positions.
- Open positions are listed with a close button.

## Notes

- This app is intentionally local-only and uses an app-level Bearer token to protect routes.
- The backend performs Robinhood login on startup using `.env` credentials and TOTP.
- If you want to change the frontend API endpoint, edit `frontend/src/services/api.js`.

## Important

- Keep your `.env` file private.
- Do not expose this app to the public internet without additional security.
