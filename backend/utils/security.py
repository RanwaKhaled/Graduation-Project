from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase_admin,supabase_auth

# This tells FastAPI to look for the "Authorization: Bearer <token>" header
token_auth_scheme = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    """
    This is the main security dependency. It takes the JWT provided by the user,
    sends it to Supabase for mathematical verification, and returns the User object.
    """
    token = credentials.credentials
    
    try:
        # Supabase does the heavy lifting of verifying the signature and expiration
        user_response = supabase_auth.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # If successful, return the user object so the endpoint knows exactly who called it
        return user_response.user
        
    except Exception as e:
        # Catch any errors (like malformed tokens) and block the request
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )