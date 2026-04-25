# backend/main.py  — ties everything together
from fastapi import FastAPI
from backend.database import Base, engine
from backend.models import user  # import so SQLAlchemy sees the table
from backend.routers import auth
from starlette.middleware.sessions import SessionMiddleware

Base.metadata.create_all(bind=engine)  # creates tables on startup

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="another-secret-key")  # needed for OAuth
app.include_router(auth.router)