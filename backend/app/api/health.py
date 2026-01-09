"""فحص صحة النظام"""
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import get_db


router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """فحص صحة النظام"""
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # فحص قاعدة البيانات
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/health/ready")
async def readiness_check():
    """فحص جاهزية النظام"""
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """فحص حياة النظام"""
    return {"alive": True}
