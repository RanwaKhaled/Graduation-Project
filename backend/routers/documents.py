from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
import uuid
from backend.database import supabase_auth, supabase_admin
from backend.utils.security import verify_jwt
import httpx
from fastapi.responses import Response

router = APIRouter(prefix="/documents", tags=["Document Uploads"])

@router.post("/upload")
async def upload_document(
    conversation_id: str = Form(...), 
    file: UploadFile = File(...),
    # 1. UNCOMMENTED: Enforce security and grab the active user
    user = Depends(verify_jwt)
):
    try:
        content_type = file.content_type
        
        # Smart Bucket Routing
        if content_type == "application/pdf":
            bucket_name = "documents"
        elif content_type in ["image/jpeg", "image/png", "image/webp"]:
            bucket_name = "vlm-image"
        elif content_type in ["audio/mpeg", "audio/wav", "audio/mp3"]:
            bucket_name = "tts-audio"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

        # Read the file data
        file_bytes = await file.read()

        # 2. Extract the REAL user ID securely from the JWT token session
        # Note: If your verify_jwt returns a dictionary instead of an object, use user["sub"] or user["id"]
        active_user_id = user.id  

        # 3. Create a unique, secure path: user_id / random_uuid . extension
        file_ext = file.filename.split('.')[-1]
        unique_path = f"{active_user_id}/{uuid.uuid4()}.{file_ext}"  

        # Upload directly to your Supabase Storage bucket
        supabase_admin.storage.from_(bucket_name).upload(
            path=unique_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )

        # Retrieve the public URL
        public_url = supabase_admin.storage.from_(bucket_name).get_public_url(unique_path)

        # --- 4. THE FOREIGN KEY FIX: ENSURE CONVERSATION EXISTS ---
        # Check if this conversation already exists in the database
        conv_check = supabase_admin.table("conversations").select("id").eq("id", conversation_id).execute()
        
        # If it doesn't exist, create it so the document has a parent
        if not conv_check.data:
            supabase_admin.table("conversations").insert({
                "id": conversation_id,
                "user_id": active_user_id,
                "title": file.filename  # <--- THIS FIXES THE ERROR!
            }).execute()
        # ---------------------------------------------------------

        # 5. Save the metadata to your SQL database to map it to the conversation
        doc_record = supabase_admin.table("documents").insert({
            "user_id": active_user_id,
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

@router.get("/proxy")
async def proxy_pdf(url: str):
    """Stripped down proxy to bypass Edge/Chrome iframe blockers"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status() 
            
            # Serve the pure PDF without any restrictive security headers
            return Response(
                content=resp.content, 
                media_type="application/pdf"
            )
            
    except Exception as e:
        print(f"❌ PROXY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))