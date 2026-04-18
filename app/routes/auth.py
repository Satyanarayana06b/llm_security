from fastapi import APIRouter, HTTPException, status

from app.middleware.auth import (authenticate_user, create_access_token, create_user)
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["authentication"])

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Desired username for registration")
    password: str = Field(..., min_length=6, max_length=100, description="Desired password for registration")

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username for login")
    password: str = Field(..., min_length=6, max_length=100, description="Password for login")

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    try:
        create_user(request.username, request.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))    
    
    access_token = create_access_token(request.username)
    return AuthResponse(access_token=access_token, username=request.username)

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = create_access_token(user["username"])
    return AuthResponse(access_token=access_token, username=request.username)