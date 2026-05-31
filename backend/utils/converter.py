import os
import tempfile
import convertapi
import uuid
from fastapi import HTTPException, APIRouter, Depends, UploadFile, File, Form
from dotenv import load_dotenv
from pathlib import Path

current_dir = Path(__file__).resolve().parent

backend_dir = current_dir.parent
env_path = backend_dir / '.env'

# 3. Load the file
load_dotenv(dotenv_path=env_path)

CONVERT_API_KEY = os.environ.get("CONVERT_API_KEY")

if not CONVERT_API_KEY:
    raise ValueError(f"CRITICAL: CONVERT_API_KEY missing! Tried path: {env_path}")

convertapi.api_credentials = CONVERT_API_KEY

async def convert_to_pdf(raw_bytes: bytes, extension: str) -> bytes:
    """Sends the file to ConvertAPI and returns the pristine PDF bytes."""
    
    # 1. Create a temporary file to hold the raw upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as temp_in:
        temp_in.write(raw_bytes)
        temp_in_path = temp_in.name

    temp_out_path = temp_in_path + ".pdf"

    try:
        # 2. The magic 1-liner that handles all Microsoft formatting
        result = convertapi.convert('pdf', {'File': temp_in_path}, from_format=extension)
        
        # 3. Save the result from their cloud to a temporary file
        result.file.save(temp_out_path)
        
        # 4. Read the fresh PDF bytes back into memory
        with open(temp_out_path, "rb") as f:
            pdf_bytes = f.read()
            
        return pdf_bytes
        
    except convertapi.ApiError as e:
        raise Exception(f"ConvertAPI failed: {str(e)}")
    
    finally:
        # 5. Try to clean up, but gracefully ignore Windows file-lock tantrums
        try:
            if os.path.exists(temp_in_path): 
                os.remove(temp_in_path)
            if os.path.exists(temp_out_path): 
                os.remove(temp_out_path)
        except OSError as e:
            print(f"⚠️ Could not delete temp file (Windows lock): {e}")
            # The OS will naturally clean up the Temp folder later, so we can safely pass
            pass