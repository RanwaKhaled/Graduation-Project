# backend/services/ai_service.py

async def get_summary(file_content: bytes, filename: str) -> str:
    # STUB — replace with real model call later
    return f"[Summary of {filename} will appear here once model is deployed]"

async def get_mcq_questions(file_content: bytes) -> list:
    # STUB
    return [
        {"question": "Sample Q1?", "options": ["A","B","C","D"], "answer": "A"},
    ]

async def text_to_speech(text: str) -> bytes:
    # STUB — return empty bytes or a test audio file
    return b""