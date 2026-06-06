# backend/routers/document.py
import io
import os
import httpx
import re
import convertapi
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
import asyncio
import uuid
from backend.database import supabase_auth, supabase_admin
from backend.utils.security import verify_jwt
from fastapi.responses import HTMLResponse, Response
import urllib.parse
from backend.utils.converter import convert_to_pdf
from backend.services.ai_service import get_full_explanation, text_to_speech
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from arabic_reshaper import reshape
from bidi.algorithm import get_display

router = APIRouter(prefix="/documents", tags=["Document Uploads"])

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    conversation_id: str = Form(...), 
    title: str = Form(...),
    file: UploadFile = File(...),
    user = Depends(verify_jwt)
):
    try:
        file_bytes = await file.read()
        original_filename = file.filename
        file_ext = original_filename.split('.')[-1].lower()
        content_type = file.content_type
        
        if file_ext in ["txt", "docx", "doc", "ppt", "pptx"]:
            print(f"🔄 Intercepted {file_ext} file. Sending to ConvertAPI...")
            
            # Hand the bytes to the cloud and get PDF bytes back
            file_bytes = await convert_to_pdf(file_bytes, file_ext) 
            
            # Trick the rest of the backend into thinking it was a PDF all along
            file_ext = "pdf"
            file.filename = original_filename.rsplit('.', 1)[0] + ".pdf"
            content_type = "application/pdf"
            print("✅ Conversion successful. Proceeding with Supabase upload.")

        # Smart Bucket Routing
        if content_type == "application/pdf":
            bucket_name = "documents"
        elif content_type in ["image/jpeg", "image/png", "image/webp"]:
            bucket_name = "vlm-image"
        elif content_type in ["audio/mpeg", "audio/wav", "audio/mp3"]:
            bucket_name = "tts-audio"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

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
                "title": title  # <--- THIS FIXES THE ERROR!
            }).execute()
        # ---------------------------------------------------------

        # 5. Save the metadata to your SQL database to map it to the conversation
        doc_record = supabase_admin.table("documents").insert({
            "user_id": active_user_id,
            "conversation_id": conversation_id,
            "title": title,
            "file_url": public_url,
            "doc_type": "uploaded",
        }).execute()

        # background task to trigger ai pipeline
        if content_type == "application/pdf":
            background_tasks.add_task(
                run_ai_pipeline,
                conversation_id=conversation_id,
                user_id=active_user_id,
                pdf_url=public_url,
            )

        return {
            "status": "success",
            "bucket_used": bucket_name,
            "file_url": public_url,
            "database_id": doc_record.data[0]["id"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")

# Make sure this is still at the bottom of documents.py
@router.get("/proxy")
async def proxy_pdf(url: str):
    import httpx
    from fastapi.responses import Response
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status() 
            return Response(
                content=resp.content, 
                media_type="application/pdf",
                headers={
                    "Access-Control-Allow-Origin": "*", # Allows our Javascript to read it
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/view")
async def view_pdf_html(url: str):
    """
    Serves a custom HTML page that uses PDF.js to render the document.
    This bypasses all browser iframe sandbox restrictions!
    """
    # Safely encode the URL for the javascript variable
    encoded_inner = urllib.parse.quote(url, safe="")
    proxy_url = f"http://127.0.0.1:8000/documents/proxy?url={encoded_inner}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>PDF Viewer</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
        <style>
            body {{ margin: 0; padding: 20px; background-color: #f4eef9; display: flex; flex-direction: column; align-items: center; overflow-y: auto; font-family: sans-serif; }}
            canvas {{ margin-bottom: 20px; max-width: 100%; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); border-radius: 8px; }}
            #loading {{ color: #4A1587; font-weight: bold; margin-top: 50px; font-size: 18px; }}
        </style>
    </head>
    <body>
        <div id="loading">Loading PDF...</div>
        <div id="pdf-container"></div>
        <script>
            const pdfUrl = "{proxy_url}";
            
            // Setup the PDF.js worker
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            
            // Fetch and render the PDF
            const loadingTask = pdfjsLib.getDocument(pdfUrl);
            loadingTask.promise.then(function(pdf) {{
                document.getElementById('loading').style.display = 'none';
                const container = document.getElementById('pdf-container');
                
                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
                    pdf.getPage(pageNum).then(function(page) {{
                        const scale = 1.2;
                        const viewport = page.getViewport({{scale: scale}});
                        const canvas = document.createElement('canvas');
                        const context = canvas.getContext('2d');
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        container.appendChild(canvas);
                        page.render({{ canvasContext: context, viewport: viewport }});
                    }});
                }}
            }}).catch(function(error) {{
                document.getElementById('loading').innerText = "Error loading PDF: " + error.message;
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


async def save_generated_artifact(
    conversation_id: str, 
    user_id: str, 
    file_bytes: bytes, 
    doc_type: str,     # "Explanation", "Transcript", "Quiz", or "Audio"
    file_ext: str,     # "pdf" or "mp3"
    bucket_name: str   # "documents" or "tts-audio"
):
    try:
        # 1. Create a unique path
        unique_path = f"{user_id}/{uuid.uuid4()}.{file_ext}"

        # 2. Upload the raw bytes to the Supabase bucket
        supabase_admin.storage.from_(bucket_name).upload(
            path=unique_path,
            file=file_bytes,
            file_options={"content-type": "application/pdf" if file_ext == "pdf" else "audio/wav" if file_ext == "wav" else "audio/mpeg"}
        )

        # 3. Get the public URL
        public_url = supabase_admin.storage.from_(bucket_name).get_public_url(unique_path)

        # 4. Save to the database WITH THE TAG
        supabase_admin.table("documents").insert({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "title": f"Generated {doc_type}",
            "file_url": public_url,
            "doc_type": doc_type  # 🚀 THIS IS THE MAGIC TAG
        }).execute()

        return public_url

    except Exception as e:
        print(f"Failed to save {doc_type}: {e}")
        return None
    
# use this to test stuff
@router.post("/mock-ai-output")
async def mock_ai_output(
    doc_type: str = Form(...), # Type exactly: "Explanation", "Transcript", "Quiz", or "Audio"
    file: UploadFile = File(...),
    user = Depends(verify_jwt) # Keeps DB constraints happy!
):
    """
    MOCK ENDPOINT: Uploads a file directly into a specific UI slot for testing.
    """
    TARGET_CONVERSATION_ID = "7d756d6a-b261-4a2a-b699-0647205d903f" 
    
    try:
        # 2. Extract file info
        file_bytes = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        # 3. Route to the correct bucket based on extension
        bucket_name = "tts-audio" if file_ext in ["mp3", "wav"] else "documents"
        
        # 4. Save to Supabase using our new helper!
        public_url = await save_generated_artifact( # Ensure you use 'await' if your helper is an async def
            conversation_id=TARGET_CONVERSATION_ID,
            user_id=user.id,
            file_bytes=file_bytes,
            doc_type=doc_type,
            file_ext=file_ext,
            bucket_name=bucket_name
        )
        
        if not public_url:
            raise HTTPException(status_code=500, detail="Supabase upload failed.")
            
        return {
            "status": "success",
            "message": f"Successfully injected {doc_type} into conversation!",
            "file_url": public_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock Upload Error: {str(e)}")
    
# convert pdf pages -> images -> call runpod -> join text -> save doc
async def run_ai_pipeline(conversation_id, user_id, pdf_url):
    """background task (all args are str)"""
    try:
        print(f"[AI pipeline] starting for convo {conversation_id}")

        # step 1: convert PDF pages to images stored in supabase, get back public URLs
        image_urls = await convert_pdf_pages_to_image_urls(pdf_url, user_id)

        if not image_urls:
            print("[AI pipeline] No images extracted from PDF")
            return
        
        print(f"[AI pipeline] Got {len(image_urls)} page images, calling runpod...")

        # step 2: call runpod for each page and combine text
        explanation_text = await get_full_explanation(image_urls)
        explanation_text = clean_ai_transcript(explanation_text)
        
        # save transcript in a text file for debugging
        with open("arabic_text.txt", "w", encoding="utf-8") as file:
            file.write(explanation_text)

        # step 3: convert md txt to pdf bytes
        explanation_pdf_bytes = text_to_pdf_bytes(explanation_text)

        # step 4: save explanation pdf to supabase 
        # with "Transcript" tag
        await save_generated_artifact(
            conversation_id=conversation_id,
            user_id=user_id,
            file_bytes=explanation_pdf_bytes,
            doc_type='Transcript',
            file_ext="pdf",
            bucket_name="documents"
        )

        # adding call for TTS model
        print("[AI pipeline] Transcript saved, starting TTS...")

        # generate audio
        wav_bytes = await text_to_speech(explanation_text)
        if wav_bytes:
            await save_generated_artifact(
                conversation_id=conversation_id,
                user_id=user_id,
                file_bytes=wav_bytes,
                doc_type="Audio",
                file_ext="wav",
                bucket_name="tts-audio"
            )
            print(f"[AI pipeline] Audio saved")
        else:
            print("[AI pipeline] TTS returned empty bytes, skipping audio save.")

    except Exception as e:
        print(f"[AI Pipeline] FAILED for conversation {conversation_id}: {e}")


async def convert_pdf_pages_to_image_urls(pdf_url: str, user_id: str) -> list[str]:
    """download pdf from supabase, split into imgs, upload to vlm-image bucker, return their public urls"""

    convertapi.api_credentials = os.getenv("CONVERT_API_KEY")
    
    # Run the blocking ConvertAPI call in a thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,  # uses default ThreadPoolExecutor
        lambda: convertapi.convert("png", {"File": pdf_url}, from_format="pdf")
    )

    print(f"[AI Pipeline] ConvertAPI returned {len(result.files)} files")
    image_urls = []
    for i, file_obj in enumerate(result.files):
        img_bytes = file_obj.io.read()
        unique_path = f"{user_id}/slides/{uuid.uuid4()}.png"
        supabase_admin.storage.from_("vlm-image").upload(
            path=unique_path,
            file=img_bytes,
            file_options={"content-type": "image/png"}
        )
        public_url = supabase_admin.storage.from_("vlm-image").get_public_url(unique_path)
        image_urls.append(public_url)
    
    return image_urls

# Register font 
pdfmetrics.registerFont(TTFont("Amiri", r"assets\Amiri-Regular.ttf"))

def wrap_and_prepare_arabic(text: str, font_name: str, font_size: int, max_width: float) -> list:
    """
    Splits long Arabic text into lines that fit the margin width safely,
    then applies character shaping and BiDi layout line-by-line.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Test line length using ReportLab's stringWidth checker
        test_line = " ".join(current_line + [word])
        width = pdfmetrics.stringWidth(test_line, font_name, font_size)
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))

    # Shape and apply BiDi to each fitted line completely independent of the next
    prepared_lines = []
    for line in lines:
        reshaped = reshape(line)
        bidi_line = get_display(reshaped, base_dir='R')
        prepared_lines.append(bidi_line)

    return prepared_lines


def clean_ai_transcript(text: str) -> str:
    lines = text.split('\n')
    cleaned = []
    prev = ""
    for line in lines:
        stripped = line.strip()
        if stripped and stripped != prev:
            cleaned.append(line)
            prev = stripped
        elif not stripped:
            cleaned.append("")
            prev = ""
    return '\n'.join(cleaned)


def text_to_pdf_bytes(markdown_text: str) -> bytes:
    markdown_text = clean_ai_transcript(markdown_text)
    
    buffer = io.BytesIO()
    
    # Page setup metrics
    right_m = 2.8 * cm
    left_m = 2.8 * cm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=right_m,
        leftMargin=left_m,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    # Calculate exactly how much horizontal room we have for text wrapping
    page_width, _ = A4
    printable_width = page_width - (left_m + right_m)

    normal_style = ParagraphStyle(
        "Normal",
        fontName="Amiri",
        fontSize=12,
        leading=21,                  
        alignment=2, # Right-aligned
    )

    heading_style = ParagraphStyle(
        "Heading",
        fontName="Amiri",
        fontSize=16,
        leading=26,
        alignment=2,
        spaceAfter=10,
        spaceBefore=12,
    )

    story = []
    blocks = re.split(r'\n\s*\n|\n---\s*\n', markdown_text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if block.startswith("## "):
            # Headings are short, so we process them normally
            heading_text = block[3:].strip()
            reshaped_head = reshape(heading_text)
            bidi_head = get_display(reshaped_head, base_dir='R')
            story.append(Paragraph(bidi_head, heading_style))
        else:
            # Process paragraph block safely using the custom line wrapping algorithm
            prepared_lines = wrap_and_prepare_arabic(
                text=block, 
                font_name="Amiri", 
                font_size=12, 
                max_width=printable_width
            )
            
            # Use HTML break tags to join the pre-arranged lines within one paragraph object
            paragraph_content = "<br/>".join(prepared_lines)
            story.append(Paragraph(paragraph_content, normal_style))
            story.append(Spacer(1, 14))

    doc.build(story)
    return buffer.getvalue()