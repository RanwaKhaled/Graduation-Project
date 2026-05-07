from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import supabase 
from utils.security import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat Traffic"])

class MessageRequest(BaseModel):
    # 1. Made conversation_id optional. If the frontend doesn't send one, we know it's a new chat.
    conversation_id: Optional[str] = None
    content: str
    image_url: Optional[str] = None

@router.post("/send")
async def process_chat_message(request: MessageRequest, user = Depends(get_current_user)):
    try:
        convo_id = request.conversation_id
        
        # 2. Auto-Create Conversation
        if not convo_id:
            # If no ID was sent, this is a brand new chat. We create it in the database first,
            # linking it to the secure user.id from our bouncer.
            new_convo = supabase.table("conversations").insert({
                "user_id": user.id,
                "title": "New Chat" # You can add an AI title-generator later!
            }).execute()
            
            # Extract the newly generated UUID from the database response
            convo_id = new_convo.data[0]["id"]

        # 3. Save the User's Message
        # Notice we REMOVED user_id here, matching your schema perfectly!
        supabase.table("messages").insert({
            "conversation_id": convo_id,
            "role": "user",
            "content": request.content,
            "image_url": request.image_url
        }).execute()

        # Placeholder for Asmaa's VLM and TTS integrations
        ai_text = "This is a placeholder secure response from the AI."

        # 4. Save the AI's Message
        supabase.table("messages").insert({
            "conversation_id": convo_id,
            "role": "ai",
            "content": ai_text
        }).execute()

        # We return the new convo_id so the frontend knows what ID to use for the next message!
        return {
            "status": "success", 
            "conversation_id": convo_id,
            "ai_response": ai_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")