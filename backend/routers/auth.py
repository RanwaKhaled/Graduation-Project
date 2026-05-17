from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import supabase
from database import supabase_auth, supabase_admin
import asyncio
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Pydantic Models ---
class AuthRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str
class UpdatePasswordRequest(BaseModel):
    password: str
# --- Endpoints ---

@router.post("/register")
async def register(body: RegisterRequest):
    print("--- NEW REGISTRATION INITIATED ---")
    print(f"1. FRONTEND SENT: {body.first_name} {body.last_name}")
    
    try:
        combined_full_name = f"{body.first_name.strip()} {body.last_name.strip()}"
        print(f"2. STITCHED NAME: {combined_full_name}")

        # Use the public client for creating the account
        response = supabase_auth.auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {
                "data": {
                    "full_name": combined_full_name
                }
            }
        })
        
        if not response.user:
            print("3. WARNING: Supabase Auth succeeded, but returned NO user data!")
        else:
            print(f"3. AUTH SUCCESS! User ID created: {response.user.id}")
            
            print("4. Waiting 1 second for database triggers...")
            await asyncio.sleep(1) 
            
            print("5. Firing Master Admin Upsert...")
            # Use the MASTER ADMIN client to force the name into the table
            db_response = supabase_admin.table("profiles").upsert({
                "id": response.user.id,
                "full_name": combined_full_name
            }).execute()
            
            print(f"6. DATABASE FINAL RESULT: {db_response.data}")

        return {
            "message": "Registration successful!", 
            "user_id": response.user.id if response.user else None
        }
        
    except Exception as e:
        print(f"!!! BACKEND ERROR CAUGHT: {str(e)} !!!")
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/login")
async def login(body: AuthRequest):
    try:
        # Supabase verifies the credentials and returns a secure JWT token
        response = supabase_auth.auth.sign_in_with_password({
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
        supabase_auth.auth.reset_password_for_email(
            request.email,
            {"redirect_to": "http://localhost:8000/auth/reset-password"} 
        )
        
        # We always return success even if the email isn't in the DB to prevent "User Enumeration" hacking
        return {"status": "success", "message": "If that email exists, a reset link has been sent."}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to trigger reset: {str(e)}")

# --- Google OAuth ---

@router.get("/google/url")
async def get_google_auth_url():
    try:
       
        response = supabase_auth.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "http://localhost:8000/auth/callback"
            }
        })
        
     
        print("SUPABASE OAUTH RESPONSE:", response)
        

        if hasattr(response, "url") and response.url:
            return {"url": response.url}
        else:
            raise ValueError("No URL returned in the Supabase OAuth response.")
            
    except Exception as e:
        print(f"OAUTH URL ERROR: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to generate Google URL: {str(e)}")




@router.post("/update-password")
async def update_password(request: UpdatePasswordRequest):
    try:
    
        response = supabase_auth.auth.update_user({
            "password": request.password
        })
        
        return {"message": "Password updated successfully!"}
        
    except Exception as e:
  
        raise HTTPException(status_code=400, detail=str(e))
class SecureResetRequest(BaseModel):
    access_token: str
    refresh_token: str
    password: str

# 2. The Webpage Endpoint 
@router.get("/reset-password")
async def reset_password_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reset Password - Yosr</title>
        <style>
            body { font-family: sans-serif; background: linear-gradient(180deg, #F4E6FF 0%, #450A75 100%); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: white; padding: 40px; border-radius: 20px; width: 350px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
            input { width: 90%; padding: 12px; margin: 15px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; background: #EBEBEB; }
            button { width: 100%; padding: 12px; background: #2D2D2D; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
            button:hover { background: #450A75; }
            p { color: #450A75; font-weight: bold; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="color: #2D2D2D; margin-top: 0;">New Password</h2>
            <p style="color: #7D7D7D; font-weight: normal; font-size: 14px; margin-bottom: 20px;">Type your new password below to secure your Yosr account.</p>
            <input type="password" id="pass" placeholder="Enter new password">
            <button onclick="updatePassword()">Update Password</button>
            <p id="msg"></p>
        </div>
        
        <script>
            async function updatePassword() {
                const msg = document.getElementById("msg");
                const password = document.getElementById("pass").value;

                // Supabase puts the security tokens in the URL hash (after the # sign)
                const hash = window.location.hash.substring(1);
                const params = new URLSearchParams(hash);
                const access = params.get("access_token");
                const refresh = params.get("refresh_token");

                if(!access || !refresh) {
                    msg.style.color = "red";
                    msg.innerText = "Error: Invalid or expired link.";
                    return;
                }

                if(password.length < 6) {
                    msg.style.color = "red";
                    msg.innerText = "Password must be at least 6 characters.";
                    return;
                }

                msg.style.color = "#450A75";
                msg.innerText = "Updating...";

                // Send the tokens and new password to our FastAPI backend
                const response = await fetch("/auth/update-password-secure", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ access_token: access, refresh_token: refresh, password: password })
                });

                if(response.ok) {
                    msg.style.color = "green";
                    msg.innerText = "Success! You can close this window and log in on the desktop app.";
                } else {
                    msg.style.color = "red";
                    msg.innerText = "Failed to update password. Link may have expired.";
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post("/update-password-secure")
async def update_password_secure(request: SecureResetRequest):
    try:
        # Tell Supabase who is resetting the password using the browser's tokens
        supabase_auth.auth.set_session(request.access_token, request.refresh_token)
        
        # Overwrite the password
        supabase_auth.auth.update_user({"password": request.password})
        
        # Log them out of the backend immediately to clear the temporary session
        supabase_auth.auth.sign_out()
        return {"message": "Password updated successfully!"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))