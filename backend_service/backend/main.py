import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from backend.routes import auth, chat, plans, profile, progress, streaks, tracking, women_health
from backend.services.storage import initialize_database
initialize_database()

app = FastAPI(
    title="Aurora AI Fitness Backend",
    description="AI-powered personalized fitness system",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(plans.router)
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(women_health.router)
app.include_router(streaks.router)
app.include_router(progress.router)
app.include_router(tracking.router)


@app.get("/")
def home():
    return {"message": "Aurora AI Backend Running"}
