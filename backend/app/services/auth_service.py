import pyotp
import robin_stocks.robinhood as rh
import secrets
from app.core.config import settings

session_tokens = {}

def login():
    mfa_code = pyotp.TOTP(settings.RH_TOTP_SECRET).now()
    return rh.login(
        settings.RH_USERNAME,
        settings.RH_PASSWORD,
        mfa_code=mfa_code
    )

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