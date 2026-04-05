from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth import create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    if body.username != settings.admin_username or body.password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(subject=body.username)
    return TokenResponse(access_token=token)
