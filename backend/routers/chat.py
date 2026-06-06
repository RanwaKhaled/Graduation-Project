# backend/routers/chat.py
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.database import supabase_admin
from backend.utils.security import verify_jwt

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
            new_convo = supabase_admin.table("conversations").insert({
                "user_id": user.id,
                "title": "New Chat" 
            }).execute()
            
            # Extract the newly generated UUID from the database response
            convo_id = new_convo.data[0]["id"]

        # 2. Save the User's Message
        supabase_admin.table("messages").insert({
            "conversation_id": convo_id,
            "role": "user",
            "content": request.content,
            "image_url": request.image_url
        }).execute()

        # 3. Simulate AI Processing Time (Unblocks the frontend UI loading spinners!)
        await asyncio.sleep(2)

        mock_ai_text = "Hello! This is a mock response from the server. The AI models are currently under development."


        supabase_admin.table("messages").insert({
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
    
@router.get("/history")
async def get_chat_history(user = Depends(verify_jwt)):
    try:
        convos_result = supabase_admin.table("conversations").select("id, title, created_at").eq("user_id", user.id).order("created_at", desc=True).execute()
        
        docs_result = supabase_admin.table("documents").select("conversation_id").eq("user_id", user.id).execute()
        
        # Create a blazing-fast lookup set of conversation IDs that actually have files attached
        valid_convo_ids = {doc["conversation_id"] for doc in docs_result.data if doc.get("conversation_id")}
        
        # Filter the history! Keep only conversations that exist in the valid set
        filtered_history = [chat for chat in convos_result.data if chat["id"] in valid_convo_ids]
        
        # 2. Fetch the user's full name from your profiles table
        profile_result = supabase_admin.table("profiles").select("full_name").eq("id", user.id).execute()
        
        # 3. Safely parse out just the first name
        first_name = "User"
        if profile_result.data and profile_result.data[0].get("full_name"):
            first_name = profile_result.data[0]["full_name"].split(" ")[0]

        return {
            "history": filtered_history, 
            "first_name": first_name 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{conversation_id}/documents")
async def get_conversation_documents(conversation_id: str, user = Depends(verify_jwt)):
    try:
        docs_res = supabase_admin.table("documents").select("file_url, doc_type").eq("conversation_id", conversation_id).execute()
        
        urls = {
            "Document": None,
            "Explanation": None,
            "Transcript": None,
            "Quiz": None,
            "Audio": None,
        }

        if docs_res.data:
            for doc in docs_res.data:
                raw_tag = doc.get("doc_type")
                final_tag = "Document" 
                
                if raw_tag:
                    clean_tag = raw_tag.lower().strip()
                    
                    if clean_tag in ["uploaded", "document", "random_doc"]:
                        final_tag = "Document"
                    elif clean_tag in ["explanation"]:
                        final_tag = "Explanation"
                    elif clean_tag in ["transcription", "transcript"]: # Catches both!
                        final_tag = "Transcript"
                    elif clean_tag == "quiz":
                        final_tag = "Quiz"
                    elif clean_tag == "audio":
                        final_tag = "Audio"

                urls[final_tag] = doc["file_url"]

        return urls

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))