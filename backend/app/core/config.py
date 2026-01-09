"""إعدادات التطبيق الأساسية"""
import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """إعدادات التطبيق"""
    
    # إعدادات عامة
    APP_NAME: str = "AutoCreator AI"
    DEBUG: bool = Field(default=False)
    API_V1_STR: str = "/api/v1"
    
    # إعدادات قاعدة البيانات
    DATABASE_URL: str = Field(default="postgresql+asyncpg://user:password@localhost:5432/autocreator")
    
    # إعدادات Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # إعدادات CORS
    CORS_ORIGINS: List[str] = Field(default=[
        "http://localhost:3000",
        "http://localhost:8000",
    ])
    
    # مفاتيح API
    OPENAI_API_KEY: str = Field(default="")
    ELEVENLABS_API_KEY: str = Field(default="")
    YOUTUBE_CLIENT_ID: str = Field(default="")
    YOUTUBE_CLIENT_SECRET: str = Field(default="")
    YOUTUBE_REFRESH_TOKEN: str = Field(default="")
    
    # إعدادات OpenAI
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4000
    
    # إعدادات DALL-E
    DALL_E_MODEL: str = "dall-e-3"
    DALL_E_SIZE: str = "1024x1024"
    DALL_E_QUALITY: str = "standard"
    
    # إعدادات ElevenLabs
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel (English)
    ARABIC_VOICE_ID: str = "AZnzlk1XvdvUeBnJln7z"  # Arabic Voice
    
    # إعدادات الفيديو
    VIDEO_WIDTH: int = 1920
    VIDEO_HEIGHT: int = 1080
    VIDEO_FPS: int = 30
    VIDEO_DURATION_PER_IMAGE: int = 5  # ثوانٍ لكل صورة
    
    # إعدادات YouTube
    YOUTUBE_DEFAULT_CATEGORY: str = "22"  # People & Blogs
    YOUTUBE_DEFAULT_PRIVACY: str = "public"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """الحصول على الإعدادات (cached)"""
    return Settings()


settings = get_settings()
