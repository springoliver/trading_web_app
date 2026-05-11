import secrets
import time
import pyotp
from threading import Lock
import httpx
from app.core.config import settings

session_tokens = {}
broker_login_status = False
_login_lock = Lock()
_last_login_attempt_at = 0.0
_last_login_error = ""
_LOGIN_COOLDOWN_SECONDS = 30
_broker_session_token = None

def login():
    """Login to Tastytrade and cache a session token."""
    global broker_login_status, _last_login_attempt_at, _last_login_error, _broker_session_token
    with _login_lock:
        if _broker_session_token:
            broker_login_status = True
            return True

        now = time.time()
        if now - _last_login_attempt_at < _LOGIN_COOLDOWN_SECONDS:
            broker_login_status = False
            return False
        _last_login_attempt_at = now

        if not settings.TASTY_USERNAME or not settings.TASTY_PASSWORD:
            _last_login_error = "TASTY_USERNAME / TASTY_PASSWORD missing"
            broker_login_status = False
            return False

        try:
            response = httpx.post(
                f"{settings.TASTY_API_BASE}/sessions",
                json={
                    "login": settings.TASTY_USERNAME,
                    "password": settings.TASTY_PASSWORD,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            payload = response.json().get("data", {})
            token = payload.get("session-token")
            if token:
                _broker_session_token = token
                broker_login_status = True
                _last_login_error = ""
                return True
            _last_login_error = f"Unexpected login response: {response.text}"
        except Exception as e:
            _last_login_error = str(e)

        _broker_session_token = None
        broker_login_status = False
        print(f"Tastytrade login error: {_last_login_error}")
        return False


def ensure_broker_session() -> bool:
    if _broker_session_token:
        return True
    return login()


def get_last_login_error() -> str:
    return _last_login_error


def get_broker_session_token() -> str | None:
    return _broker_session_token

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