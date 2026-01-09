"""نماذج قاعدة البيانات"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Project(Base):
    """نموذج المشروع"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # معلومات المشروع
    topic = Column(String(500), nullable=False)
    title = Column(String(500))
    description = Column(Text)
    language = Column(String(10), default="ar")
    
    # إعدادات المشروع
    style = Column(String(100), default="documentary")
    duration = Column(Integer, default=5)  # بالدقائق
    quality = Column(String(50), default="1080p")
    
    # حالة المشروع
    status = Column(String(50), default="pending")  # pending, generating, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    
    # النتائج
    video_path = Column(String(1000))
    video_url = Column(String(1000))
    thumbnail_url = Column(String(1000))
    youtube_video_id = Column(String(100))
    
    # البيانات الوسيطة (JSON)
    script_data = Column(JSON)
    images_data = Column(JSON)
    voice_data = Column(JSON)
    
    # الإحصائيات
    cost_usd = Column(Float, default=0.0)
    processing_time_seconds = Column(Integer, default=0)
    
    # التواريخ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # العلاقات
    user = relationship("User", back_populates="projects")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, topic='{self.topic}', status='{self.status}')>"


class Scene(Base):
    """نموذج المشهد"""
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # محتوى المشهد
    scene_number = Column(Integer)
    script_text = Column(Text, nullable=False)
    visual_prompt = Column(Text)
    
    # الوسائط
    image_url = Column(String(1000))
    image_path = Column(String(1000))
    audio_url = Column(String(1000))
    audio_path = Column(String(1000))
    
    # إعدادات المونتاج
    duration_seconds = Column(Float, default=5.0)
    transition_type = Column(String(50), default="fade")
    
    # الترجمات
    subtitle_text = Column(Text)
    subtitle_start_time = Column(Float)
    subtitle_end_time = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    project = relationship("Project", back_populates="scenes")
    
    def __repr__(self):
        return f"<Scene(id={self.id}, scene_number={self.scene_number})>"


class User(Base):
    """نموذج المستخدم"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # معلومات المستخدم
    name = Column(String(255))
    youtube_channel_id = Column(String(255))
    youtube_channel_name = Column(String(255))
    
    # إعدادات المستخدم
    settings = Column(JSON, default={})
    
    # حالة الحساب
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    # التواريخ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    projects = relationship("Project", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class APILog(Base):
    """نموذج سجل API"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # معلومات الـ API
    endpoint = Column(String(500))
    method = Column(String(10))
    request_data = Column(JSON)
    response_data = Column(JSON)
    
    # حالة الطلب
    status_code = Column(Integer)
    error_message = Column(Text)
    processing_time_ms = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<APILog(id={self.id}, endpoint='{self.endpoint}')>"
