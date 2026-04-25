# frontend/utils/api_client.py
import httpx

BASE_URL = "http://localhost:8000"

class ApiClient:
    def __init__(self, token: str = None):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    async def login(self, email, password):
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{BASE_URL}/auth/login",
                                  json={"email": email, "password": password})
            r.raise_for_status()
            return r.json()  # {"token": "..."}

    async def upload_file(self, file_bytes, filename):
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{BASE_URL}/chat/upload",
                                  files={"file": (filename, file_bytes)},
                                  headers=self.headers)
            return r.json()

    async def get_summary(self, session_id):
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{BASE_URL}/chat/{session_id}/summary",
                                 headers=self.headers)
            return r.json()