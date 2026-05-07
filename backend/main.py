from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, chat,documents

app = FastAPI(
    title="Dyslexia AI Assistant API",
    description="Backend routing for Flet UI, AI Models, and Supabase"
)

# 1. Add CORS so your Flet frontend can communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (good for local testing)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# 2. Include your functional routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
# 3. Simple health check
@app.get("/")
def read_root():
    return {"status": "online", "message": "FastAPI backend is running!"}