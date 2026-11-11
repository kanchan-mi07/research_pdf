import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.document_routes import router as document_router
from app.routes.chat_routes import router as chat_router
from app.routes.auth_routes import router as auth_router
from app.database.connection import engine, Base
from app.database import models  # Ensures models are registered with SQLAlchemy

# Debug check to confirm environment variable is loaded correctly in logs
print("DB URL being used:", os.getenv("DATABASE_URL"))

app = FastAPI(
    title="AI Research Assistant",
    description="An AI application for asking questions from PDF documents",
    version="1.0"
)

# Configure CORS for your React Frontend
# (Add your production Vercel URL here once deployed)
origins = [
    "http://localhost:5173",
    "https://your-frontend-app.vercel.app",  # <-- Update this with your actual Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "AI Research Assistant Backend is Running!"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# Include App Routers
app.include_router(
    document_router,
    prefix="/documents",
    tags=["Documents"]
)

app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"]
)

app.include_router(
    auth_router, 
    prefix="/auth", 
    tags=["auth"]
)

# Create database tables on startup using the secure connection engine
Base.metadata.create_all(bind=engine)