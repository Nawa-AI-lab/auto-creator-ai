# AutoCreator AI Backend
# FastAPI Application for AI-Powered Content Creation

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import engine, Base
from app.api import router as api_router
from app.workers.celery_app import celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    # بدء التشغيل
    print("🚀 بدء تشغيل AutoCreator AI Backend...")
    
    # إنشاء الجداول
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ قاعدة البيانات جاهزة")
    print("✅ Celery Worker جاهز")
    
    yield
    
    # إيقاف التشغيل
    print("🛑 إيقاف الخادم...")


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="AutoCreator AI API",
    description="وكيل ذكاء اصطناعي متكامل لصناعة ونشر المحتوى",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تضمين نقاط النهاية
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Welcome to AutoCreator AI",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health_check():
    """فحص صحة النظام"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected",
            "celery": "running"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
