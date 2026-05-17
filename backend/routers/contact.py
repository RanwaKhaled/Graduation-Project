from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import supabase_admin

router = APIRouter(prefix="/contact", tags=["Contact Us"])

# 1. The Pydantic Model to catch the frontend data
class ContactRequest(BaseModel):
    name: str
    email: str
    message: str

# 2. The POST endpoint
@router.post("/send")
async def send_contact_message(request: ContactRequest):
    try:
        # Insert the data into the Supabase table using the Admin client
        db_response = supabase_admin.table("contact_messages").insert({
            "name": request.name,
            "email": request.email,
            "message": request.message
        }).execute()
        
        return {"status": "success", "message": "Message saved successfully!"}
        
    except Exception as e:
        # Catch any database errors
        raise HTTPException(status_code=400, detail=f"Failed to send message: {str(e)}")