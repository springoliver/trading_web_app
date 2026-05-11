import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BROKER = os.getenv("BROKER", "tastytrade")
    TASTY_USERNAME = os.getenv("TASTY_USERNAME")
    TASTY_PASSWORD = os.getenv("TASTY_PASSWORD")
    TASTY_ACCOUNT_NUMBER = os.getenv("TASTY_ACCOUNT_NUMBER")
    TASTY_SANDBOX = os.getenv("TASTY_SANDBOX", "true").lower() == "true"
    TASTY_API_BASE = os.getenv(
        "TASTY_API_BASE",
        "https://api.cert.tastyworks.com" if TASTY_SANDBOX else "https://api.tastyworks.com",
    )
    APP_USERNAME = os.getenv("APP_USERNAME", "admin")
    APP_PASSWORD = os.getenv("APP_PASSWORD", "admin")
    APP_2FA_SECRET = os.getenv("APP_2FA_SECRET", "123456")  # TOTP seed or static fallback code
    APP_TOKEN_TTL_SECONDS = int(os.getenv("APP_TOKEN_TTL_SECONDS", "28800"))
    SECRET_KEY = os.getenv("SECRET_KEY")

settings = Settings()