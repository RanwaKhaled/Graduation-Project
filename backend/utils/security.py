from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase # Assuming database.py is in the backend root based on our previous fix!

# This tells FastAPI to look for an "Authorization: Bearer <token>" header
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Ask Supabase to cryptographically verify the token
        response = supabase.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
            
        # If valid, return the user object so the chat router knows exactly who is sending the message
        return response.user
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token Error: {str(e)}")