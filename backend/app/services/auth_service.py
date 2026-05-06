import robin_stocks.robinhood as rh
import secrets
import time
import pyotp
from threading import Lock
from app.core.config import settings

session_tokens = {}
rh_login_status = False
_login_lock = Lock()
_last_login_attempt_at = 0.0
_last_login_error = ""
_LOGIN_COOLDOWN_SECONDS = 30

def login():
    """Login to Robinhood using username/password.
    Robinhood deprecated TOTP in favor of app/device-based authentication.
    """
    global rh_login_status, _last_login_attempt_at, _last_login_error
    with _login_lock:
        try:
            if rh.get_auth_token():
                rh_login_status = True
                return True
        except Exception:
            pass

        now = time.time()
        if now - _last_login_attempt_at < _LOGIN_COOLDOWN_SECONDS:
            rh_login_status = False
            return False
        _last_login_attempt_at = now

        if not settings.RH_USERNAME or not settings.RH_PASSWORD:
            _last_login_error = "RH_USERNAME / RH_PASSWORD missing"
            rh_login_status = False
            return False

        try:
            result = rh.login(settings.RH_USERNAME, settings.RH_PASSWORD)
            if isinstance(result, dict) and result.get("access_token"):
                rh_login_status = True
                _last_login_error = ""
                return True
            _last_login_error = f"Unexpected login response: {result}"
        except Exception as e:
            _last_login_error = str(e)

        rh_login_status = False
        print(f"Robinhood login error: {_last_login_error}")
        return False


def ensure_rh_session() -> bool:
    try:
        if rh.get_auth_token():
            return True
    except Exception:
        pass
    return login()


def get_last_login_error() -> str:
    return _last_login_error

def verify_app_login(username: str, password: str, otp: str) -> bool:
    if username != settings.APP_USERNAME or password != settings.APP_PASSWORD:
        return False
    secret = settings.APP_2FA_SECRET or ""
    try:
        if len(secret) >= 16:
            return pyotp.TOTP(secret).verify(str(otp), valid_window=1)
    except Exception:
        pass
    return str(otp) == secret

def create_session_token() -> str:
    token = secrets.token_urlsafe(32)
    session_tokens[token] = time.time() + settings.APP_TOKEN_TTL_SECONDS
    return token

def validate_session_token(token: str) -> bool:
    expires_at = session_tokens.get(token)
    if not expires_at:
        return False
    if time.time() > expires_at:
        session_tokens.pop(token, None)
        return False
    return True