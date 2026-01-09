"""مهام Celery للخلفية"""
import asyncio
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_maker
from app.agents.orchestrator import OrchestratorAgent


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True
)
def generate_video_task(self, project_id: int):
    """مهمة توليد الفيديو"""
    
    async def _execute():
        async with async_session_maker() as session:
            # استرجاع بيانات المشروع
            from app.services.project_service import ProjectService
            
            service = ProjectService(session)
            project = await service.get_project(project_id)
            
            if not project:
                return {"success": False, "error": "المشروع غير موجود"}
            
            # إنشاء Orchestrator وتنفيذ خط الإنتاج
            orchestrator = OrchestratorAgent(session)
            
            result = await orchestrator.execute_pipeline(
                project_id=project_id,
                user_id=project.user_id,
                topic=project.topic,
                style=project.style,
                duration_minutes=project.duration,
                language=project.language,
                auto_publish=False
            )
            
            return result
    
    try:
        result = asyncio.run(_execute())
        return result
    except Exception as e:
        # إعادة المحاولة في حالة الفشل
        raise self.retry(exc=e)


@shared_task
def cleanup_old_files(days: int = 7):
    """تنظيف الملفات القديمة"""
    
    import os
    import time
    from datetime import datetime, timedelta
    
    directories = ["generated_images", "generated_audio", "output_videos"]
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                
                if file_time < cutoff_time:
                    os.remove(filepath)
                    print(f"🗑️ حذف ملف قديم: {filepath}")
    
    return {"cleaned": True}


@shared_task
def send_notification(user_id: int, message: str, project_id: int = None):
    """إرسال إشعار للمستخدم"""
    
    # يمكن دمج هذا مع خدمة الإشعارات
    print(f"📧 إشعار للمستخدم {user_id}: {message}")
    
    return {"sent": True, "user_id": user_id}
