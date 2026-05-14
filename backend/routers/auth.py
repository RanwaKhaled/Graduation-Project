from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Pydantic Models ---
class AuthRequest(BaseModel):
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

# --- Endpoints ---

@router.post("/register")
async def register(body: AuthRequest):
    try:
        # Supabase automatically hashes the password and creates the user securely
        response = supabase.auth.sign_up({
            "email": body.email,
            "password": body.password
        })
        return {
            "message": "Registration successful!", 
            "user_id": response.user.id
        }
    except Exception as e:
        # Catch errors like "Email already exists" or "Password too weak"
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(body: AuthRequest):
    try:
        # Supabase verifies the credentials and returns a secure JWT token
        response = supabase.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password
        })
        return {
            "token": response.session.access_token, 
            "user_id": response.user.id
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials. Please try again.")

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    try:
        # Tell Supabase to send the recovery email
        supabase.auth.reset_password_for_email(
            request.email,
            {"redirect_to": "http://localhost:8000/reset-password"} # Update this to your actual frontend URL later!
        )
        
        # We always return success even if the email isn't in the DB to prevent "User Enumeration" hacking
        return {"status": "success", "message": "If that email exists, a reset link has been sent."}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to trigger reset: {str(e)}")

# --- Google OAuth ---

@router.get("/google/url")
async def get_google_oauth_url():
    try:
        # Instead of managing the OAuth client manually, we ask Supabase to generate the login link.
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                # This should point to your Flet app's URL or a deep link once deployed
                "redirect_to": "http://localhost:8000/auth/callback" 
            }
        })
        return {"url": response.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    