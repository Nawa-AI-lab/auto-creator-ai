"""ملف استيراد نقاط النهاية"""
from app.api.projects import router as projects_router
from app.api.health import router as health_router
from app.api.users import router as users_router


__all__ = ["projects_router", "health_router", "users_router"]
