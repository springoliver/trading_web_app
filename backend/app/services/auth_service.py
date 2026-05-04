import robin_stocks.robinhood as rh
import secrets
from app.core.config import settings

session_tokens = {}
rh_login_status = False

def login():
    """Login to Robinhood using username/password.
    Robinhood deprecated TOTP in favor of app/device-based authentication.
    """
    global rh_login_status
    try:
        # Simple username/password login
        result = rh.login(
            settings.RH_USERNAME,
            settings.RH_PASSWORD
        )
        # Successfully logged in
        rh_login_status = True
        return result
    except Exception as e:
        # Login failed but don't crash the app
        rh_login_status = False
        error_msg = str(e)
        print(f"Robinhood login error: {error_msg}")
        return None

def verify_app_login(username: str, password: str, otp: str) -> bool:
    if username != settings.APP_USERNAME or password != settings.APP_PASSWORD:
        return False
    return otp == settings.APP_2FA_SECRET

def create_session_token() -> str:
    token = secrets.token_urlsafe(32)
    session_tokens[token] = True
    return token

def validate_session_token(token: str) -> bool:
    return token in session_tokens