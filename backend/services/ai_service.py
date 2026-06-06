# backend/services/ai_service.py
import os
import httpx
import re

# Get the explanation from the VLM on runpod
RUNPOD_URL = os.getenv("RUNPOD_URL", "").rstrip("/")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY", "ranwa-gemma-trial")

EXPLAIN_PROMPT = (
    "Explain this slide in **Egyptian Arabic** using **clear** and **simple** sentences.\n"
    "Cover all visible elements in the slides including text, formulas, images and diagrams.\n"
    "Do NOT add new information, examples, definitions, or assumptions "
    "that are not explicitly shown on the slide."
)

async def explain_slide(image_url:str) -> str:
    """Call runpod endpoing with the image URL and returns explanation text"""
    if not RUNPOD_URL:
        raise RuntimeError("RUNPOD_URL is not set in the env vars")
    
    payload = {
        "api_key": RUNPOD_API_KEY,
        "image_url": image_url,
        "max_new_tokens": 125,
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        r = await client.post(f"{RUNPOD_URL}/predict", json=payload)
        r.raise_for_status()
        return r.json()['result']

async def get_full_explanation(image_urls: list[str]) -> str:
    "aggregate all explanations into one document"
    parts = []
    for i, url in enumerate(image_urls, start=1):
        text = await explain_slide(url)
        parts.append(f'## Slide {i}\n\n{text}')
    return "\n\n----\n\n".join(parts)


# Generate Questions and Summary from LLM
async def get_summary(file_content: bytes, filename: str) -> str:
    # STUB — replace with real model call later
    return f"[Summary of {filename} will appear here once model is deployed]"

async def get_mcq_questions(file_content: bytes) -> list:
    # STUB
    return [
        {"question": "Sample Q1?", "options": ["A","B","C","D"], "answer": "A"},
    ]


# Get the audio from the TTS model
TTS_RUNPOD_URL = os.getenv("TTS_RUNPOD_URL", "").rstrip("/")
TTS_API_KEY = os.getenv("TTS_API_KEY", "ranwa-tts-trial")

async def text_to_speech(text: str) -> bytes:
    """Send explanation text to TTS Runpod, get back WAV bytes"""
    if not TTS_RUNPOD_URL:
        raise RuntimeError("TTS_RUNPOD_URL is not set in the env vars")
    

    # split on slide separators (## Slide N or ----)
    slides = re.split("\n\n---\n\n", text)
    slides = [s.strip() for s in slides if s.strip()]

    all_wav_bytes = []

    async with httpx.AsyncClient(timeout=300.0) as client:
        for i, slide_text in enumerate(slides, start=1):
            # Strip the "## Slide N" heading — it's not speakable Arabic
            lines = slide_text.split("\n")
            speakable = "\n".join(l for l in lines if not l.startswith("## Slide")).strip()
            
            if not speakable:
                continue

            print(f"[TTS] Synthesizing slide {i}/{len(slides)}...")
            payload = {
                "api_key": TTS_API_KEY,
                "text": speakable,
                "language": "ar",
                "temperature": 0.7,
                "max_new_tokens": 500,
            }
            r = await client.post(f"{TTS_RUNPOD_URL}/synthesize", json=payload)
            r.raise_for_status()
            all_wav_bytes.append(r.content)
            print(f"[TTS] Slide {i} done ({len(r.content)} bytes)")

    if not all_wav_bytes:
        return b""

    return _concatenate_wav_files(all_wav_bytes)


def _concatenate_wav_files(wav_bytes_list: list[bytes]) -> bytes:
    """Concatenate multiple WAV byte strings into one WAV file."""
    import wave
    import io

    output_buf = io.BytesIO()
    output_wav = None

    for wav_bytes in wav_bytes_list:
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, 'rb') as w:
            params = w.getparams()
            frames = w.readframes(w.getnframes())

        if output_wav is None:
            output_wav = wave.open(output_buf, 'wb')
            output_wav.setparams(params)

        output_wav.writeframes(frames)

    if output_wav:
        output_wav.close()

    output_buf.seek(0)
    return output_buf.read()