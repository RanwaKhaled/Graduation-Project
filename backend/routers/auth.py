# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import bcrypt

from backend.database import get_db
from backend.models.user import User
from backend.utils.jwt_utils import create_jwt
from authlib.integrations.starlette_client import OAuth


router = APIRouter(prefix="/auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Pydantic schemas for request bodies ---
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Endpoints ---
@router.post("/register")
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode("utf-8")
    user = User(email=body.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_jwt(user.id)}

@router.post("/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(401, "Invalid credentials")
    if not bcrypt.checkpw(body.password.encode(), user.hashed_password.encode()):
        raise HTTPException(401, "Invalid credentials")
    return {"token": create_jwt(user.id)}

# --- Google OAuth ---
oauth = OAuth()
oauth.register(
    "google",
    client_id="GOOGLE_CLIENT_ID",       # move to .env
    client_secret="GOOGLE_CLIENT_SECRET", # move to .env
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    user = db.query(User).filter(User.google_id == user_info["sub"]).first()
    if not user:
        # also check by email in case they registered normally before
        user = db.query(User).filter(User.email == user_info["email"]).first()
        if user:
            user.google_id = user_info["sub"]
        else:
            user = User(email=user_info["email"], google_id=user_info["sub"])
            db.add(user)
        db.commit()
        db.refresh(user)

    return {"token": create_jwt(user.id)}