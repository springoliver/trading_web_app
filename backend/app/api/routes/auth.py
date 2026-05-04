from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.auth_service import create_session_token, verify_app_login

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str
    otp: str  # App-level 2FA code (not Robinhood TOTP)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    if not verify_app_login(request.username, request.password, request.otp):
        raise HTTPException(status_code=401, detail="Invalid credentials or OTP")
    token = create_session_token()
    return {"access_token": token, "token_type": "bearer"}