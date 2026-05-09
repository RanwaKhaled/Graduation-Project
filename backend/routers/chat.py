import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import supabase 
from utils.security import verify_jwt

router = APIRouter(prefix="/chat", tags=["Chat Traffic"])


MOCK_AUDIO_URL = "https://tzxmmiejyyxhlmyxiwhb.supabase.co/storage/v1/object/public/tts-audio/gen_egy1_000.wav"

class MessageRequest(BaseModel):
    # Made conversation_id optional. If the frontend doesn't send one, we know it's a new chat.
    conversation_id: Optional[str] = None
    content: str
    image_url: Optional[str] = None

@router.post("/send")
async def process_chat_message(request: MessageRequest, user = Depends(verify_jwt)):
    try:
        convo_id = request.conversation_id
        
        # 1. Auto-Create Conversation
        if not convo_id:
            # If no ID was sent, this is a brand new chat. We create it in the database first,
            # linking it to the secure user.id from our bouncer.
            new_convo = supabase.table("conversations").insert({
                "user_id": user.id,
                "title": "New Chat" 
            }).execute()
            
            # Extract the newly generated UUID from the database response
            convo_id = new_convo.data[0]["id"]

        # 2. Save the User's Message
        supabase.table("messages").insert({
            "conversation_id": convo_id,
            "role": "user",
            "content": request.content,
            "image_url": request.image_url
        }).execute()

        # 3. Simulate AI Processing Time (Unblocks the frontend UI loading spinners!)
        await asyncio.sleep(2)

        mock_ai_text = "Hello! This is a mock response from the server. The AI models are currently under development."


        supabase.table("messages").insert({
            "conversation_id": convo_id,
            "role": "ai",
            "content": mock_ai_text,
            "audio_url": MOCK_AUDIO_URL
        }).execute()

  
        return {
            "status": "success", 
            "conversation_id": convo_id,
            "ai_response": mock_ai_text,
            "audio_url": MOCK_AUDIO_URL
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")