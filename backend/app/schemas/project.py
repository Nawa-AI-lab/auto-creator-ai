"""مخططات Pydantic للمشاريع"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.database import Project, Scene


class ProjectCreate(BaseModel):
    """إنشاء مشروع جديد"""
    topic: str = Field(..., min_length=5, max_length=500, description="موضوع الفيديو")
    style: str = Field(default="documentary", description="أسلوب الفيديو")
    duration: int = Field(default=5, ge=1, le=30, description="المدة بالدقائق")
    language: str = Field(default="ar", description="اللغة")


class ProjectUpdate(BaseModel):
    """تحديث مشروع"""
    title: Optional[str] = None
    description: Optional[str] = None
    style: Optional[str] = None
    duration: Optional[int] = None


class ProjectResponse(BaseModel):
    """استجابة المشروع"""
    id: int
    topic: str
    title: Optional[str]
    description: Optional[str]
    status: str
    progress: int
    language: str
    style: str
    duration: int
    video_path: Optional[str]
    video_url: Optional[str]
    youtube_video_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """قائمة المشاريع"""
    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int


class SceneResponse(BaseModel):
    """استجابة المشهد"""
    id: int
    scene_number: int
    script_text: str
    visual_prompt: Optional[str]
    image_path: Optional[str]
    audio_path: Optional[str]
    duration_seconds: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScriptData(BaseModel):
    """بيانات السكريبت"""
    title: str
    description: str
    scenes: List[dict]
    tags: List[str]
    estimated_duration: int


class VideoGenerationRequest(BaseModel):
    """طلب توليد فيديو"""
    topic: str = Field(..., description="موضوع الفيديو")
    style: str = Field(default="documentary", description="أسلوب الفيديو")
    duration: int = Field(default=5, ge=1, le=30, description="المدة بالدقائق")
    language: str = Field(default="ar", description="اللغة")
    auto_publish: bool = Field(default=False, description="النشر تلقائياً على يوتيوب")
    generate_subtitles: bool = Field(default=True, description="توليد ترجمات")


class VideoGenerationResponse(BaseModel):
    """استجابة توليد الفيديو"""
    project_id: int
    status: str
    message: str
    estimated_time_minutes: int
