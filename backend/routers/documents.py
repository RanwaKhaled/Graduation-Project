from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
import uuid
from database import supabase
from utils.security import get_current_user

router = APIRouter(prefix="/documents", tags=["Document Uploads"])

@router.post("/upload")
async def upload_document(
   
    conversation_id: str = Form(...), 
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    try:
        content_type = file.content_type
        
        # 1. Smart Bucket Routing (Matching your exact dashboard setup)
        if content_type == "application/pdf":
            bucket_name = "documents"
        elif content_type in ["image/jpeg", "image/png", "image/webp"]:
            bucket_name = "vlm-image"
        elif content_type in ["audio/mpeg", "audio/wav", "audio/mp3"]:
            bucket_name = "tts-audio"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

        # 2. Read the file data
        file_bytes = await file.read()

        # 3. Create a unique, secure path: user_id / random_uuid . extension
        file_ext = file.filename.split('.')[-1]
        unique_path = f"{user.id}/{uuid.uuid4()}.{file_ext}"

        # 4. Upload directly to your Supabase Storage bucket
        supabase.storage.from_(bucket_name).upload(
            path=unique_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )

        # 5. Retrieve the public URL so the AI models and frontend can see it
        public_url = supabase.storage.from_(bucket_name).get_public_url(unique_path)

        # 6. Save the metadata to your SQL database to map it to the conversation
        doc_record = supabase.table("documents").insert({
            "user_id": user.id,
            "conversation_id": conversation_id,
            "title": file.filename,
            "file_url": public_url
        }).execute()

        return {
            "status": "success",
            "bucket_used": bucket_name,
            "file_url": public_url,
            "database_id": doc_record.data[0]["id"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")