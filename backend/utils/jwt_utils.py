# backend/utils/jwt_utils.py
from jose import jwt 
import datetime

SECRET_KEY = "change-this-to-a-long-random-string"  # move to .env later
ALGORITHM = "HS256"

def create_jwt(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])