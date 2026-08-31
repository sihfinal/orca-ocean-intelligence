"""
Blue Orbit / ORCA Configuration Module
ISRO SIH 2026 - Problem Statement 26176
Centralized runtime and credential configuration.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# LLM Provider API Keys
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# CORS Configuration
DEFAULT_CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "https://sihdeploy.vercel.app",
]

def get_cors_origins() -> List[str]:
    """
    Returns the allow-list of CORS origins.
    Permits extending origins via CORS_ALLOWED_ORIGINS environment variable (comma-separated).
    """
    custom_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    origins = list(DEFAULT_CORS_ORIGINS)
    if custom_origins:
        for origin in custom_origins.split(","):
            cleaned = origin.strip()
            if cleaned and cleaned not in origins:
                origins.append(cleaned)
    return origins
