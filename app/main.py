from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routers import (
    boards,
    states,
    syllabus,
    classes,
    subjects,
    chapters,
    key_points,
    questions,
    lesson_plans
)

# Get environment
environment = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="Content Service API",
    description="Microservice for managing educational content across multiple boards, states, and universities",
    version="1.0.0"
)

# CORS configuration - restrict origins in production
if environment == "production":
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        ""
    ).split(",") if os.getenv("ALLOWED_ORIGINS") else []
    # Remove empty strings
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
else:
    # Development: allow all origins
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(boards.router)
app.include_router(states.router)
app.include_router(syllabus.router)
app.include_router(classes.router)
app.include_router(subjects.router)
app.include_router(chapters.router)
app.include_router(key_points.router)
app.include_router(questions.router)
app.include_router(lesson_plans.router)


@app.get("/")
def root():
    return {
        "message": "Content Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

