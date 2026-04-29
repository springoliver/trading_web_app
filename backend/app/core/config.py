import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    RH_USERNAME = os.getenv("RH_USERNAME")
    RH_PASSWORD = os.getenv("RH_PASSWORD")
    RH_TOTP_SECRET = os.getenv("RH_TOTP_SECRET")
    APP_USERNAME = os.getenv("APP_USERNAME", "admin")
    APP_PASSWORD = os.getenv("APP_PASSWORD", "admin")
    APP_2FA_SECRET = os.getenv("APP_2FA_SECRET", "YOUR_APP_2FA_SECRET")
    SECRET_KEY = os.getenv("SECRET_KEY")

settings = Settings()