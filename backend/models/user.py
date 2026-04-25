# backend/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from backend.database import Base
import datetime 
from datetime import UTC

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    google_id = Column(String, nullable=True)  # for Google OAuth
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# backend/models/chat.py
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(String)
    message_type = Column(String)  # "text", "audio", "mcq"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)