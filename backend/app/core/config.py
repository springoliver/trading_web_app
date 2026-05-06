import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    RH_USERNAME = os.getenv("RH_USERNAME")
    RH_PASSWORD = os.getenv("RH_PASSWORD")
    RH_DEVICE_TOKEN = os.getenv("RH_DEVICE_TOKEN")  # Optional: Pre-registered device token
    APP_USERNAME = os.getenv("APP_USERNAME", "admin")
    APP_PASSWORD = os.getenv("APP_PASSWORD", "admin")
    APP_2FA_SECRET = os.getenv("APP_2FA_SECRET", "123456")  # TOTP seed or static fallback code
    APP_TOKEN_TTL_SECONDS = int(os.getenv("APP_TOKEN_TTL_SECONDS", "28800"))
    SECRET_KEY = os.getenv("SECRET_KEY")

settings = Settings()