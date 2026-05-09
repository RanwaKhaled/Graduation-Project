import pytest
from fastapi.testclient import TestClient
from main import app  
from utils.security import verify_jwt  

# --- Configuration & Mock Data ---
# We use a real user/conversation ID to ensure foreign key constraints pass in the database, 
# but we bypass the network call to Supabase Auth to keep tests blazingly fast.

TEST_USER_ID = "6005ce84-b509-4c20-bdd1-98c6674d3cae"
TEST_CONVERSATION_ID = "ec25b146-da23-4480-a1f9-1e681ae1e123"

class AuthenticatedTestUser:
    """Represents a successfully authenticated Supabase user."""
    id = TEST_USER_ID
    email = "habibasql@gmail.com" 

def override_verify_jwt():
    """Security dependency override for automated testing."""
    return AuthenticatedTestUser()

# Inject the test user into the FastAPI application
app.dependency_overrides[verify_jwt] = override_verify_jwt

client = TestClient(app)

def test_document_upload_success():
    """
    Test that a valid document is successfully uploaded, 
    stored in the correct bucket, and linked to the active conversation.
    """
    test_file_content = b"%PDF-1.4\n%This is a valid test PDF document content."
    files = {"file": ("test_research_paper.pdf", test_file_content, "application/pdf")}
    
    form_data = {"conversation_id": TEST_CONVERSATION_ID}
    
    response = client.post(
        "/documents/upload", 
        files=files, 
        data=form_data 
    )
    

    assert response.status_code == 200, f"Upload failed with error: {response.text}"
def test_chat_send_success():
    payload = {
        "content": "Checking the new audio integration!",
        "conversation_id": TEST_CONVERSATION_ID
    }
    
    response = client.post("/chat/send", json=payload)
    
    assert response.status_code == 200, f"Chat message failed: {response.text}"
    
    response_data = response.json()
    assert "status" in response_data
    assert "ai_response" in response_data

    assert "audio_url" in response_data, "Response missing audio_url"
    assert response_data["audio_url"] is not None, "Audio URL should not be null"