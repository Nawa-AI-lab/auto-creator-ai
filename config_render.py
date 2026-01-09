"""إعدادات Render المجانية - SQLite + HTTP APIs"""
import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """إعدادات التطبيق لـ Render المجاني"""
    
    APP_NAME: str = "AutoCreator AI (Free)"
    DEBUG: bool = Field(default=False)
    API_V1_STR: str = "/api/v1"
    
    # === قاعدة البيانات (SQLite مجاني) ===
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./autocreator.db",
        description="SQLite for free tier - لا تحتاج PostgreSQL"
    )
    
    # === Redis ===
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # === CORS ===
    CORS_ORIGINS: List[str] = Field(default=[
        "http://localhost:3000",
        "https://*.onrender.com",
    ])
    
    # === AI Provider (HTTP APIs - لا تحتاج Rust) ===
    AI_PROVIDER: str = "groq"  # Groq Llama 2 - مجاني وسريع
    
    # Groq (مجاني - Llama 2 70B)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama2-70b-4096"
    
    # Hugging Face (مجاني)
    HUGGINGFACE_API_KEY: str = ""
    
    # Google Gemini (مجاني)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"
    
    # === 图片生成 (HTTP API) ===
    IMAGE_PROVIDER: str = "huggingface"  # 使用API
    HF_TOKEN: str = ""
    
    # === 语音合成 (HTTP API - Edge TTS) ===
    TTS_PROVIDER: str = "edge"
    EDGE_VOICE: str = "zh-CN-XiaoxiaoNeural"
    
    # === YouTube (اختياري) ===
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REFRESH_TOKEN: str = ""
    
    # === إعدادات الفيديو ===
    VIDEO_WIDTH: int = 1280
    VIDEO_HEIGHT: int = 720
    VIDEO_FPS: int = 24
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
