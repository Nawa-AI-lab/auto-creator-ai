"""خدمة إدارة المشاريع"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import Project, Scene, User
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """خدمة إدارة المشاريع"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """الحصول على مشروع"""
        
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def list_projects(
        self,
        skip: int = 0,
        limit: int = 10,
        user_id: int = None,
        status: str = None
    ) -> Tuple[List[Project], int]:
        """قائمة المشاريع"""
        
        query = select(Project)
        
        if user_id:
            query = query.where(Project.user_id == user_id)
        
        if status:
            query = query.where(Project.status == status)
        
        # حساب总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # تطبيق الترتيب والصفحات
        query = query.order_by(Project.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        projects = result.scalars().all()
        
        return list(projects), total
    
    async def create_project(
        self,
        project_data: ProjectCreate,
        user_id: int = 1  # افتراضي للمشروع الأول
    ) -> Project:
        """إنشاء مشروع جديد"""
        
        project = Project(
            user_id=user_id,
            topic=project_data.topic,
            title=project_data.topic,  # عنوان افتراضي
            style=project_data.style,
            duration=project_data.duration,
            language=project_data.language,
            status="pending",
            progress=0
        )
        
        self.db.add(project)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """تحديث مشروع"""
        
        project = await self.get_project(project_id)
        if not project:
            return None
        
        update_data = project_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def update_status(
        self,
        project_id: int,
        status: str,
        progress: int = 0
    ) -> Optional[Project]:
        """تحديث حالة المشروع"""
        
        project = await self.get_project(project_id)
        if not project:
            return None
        
        project.status = status
        project.progress = progress
        
        if status == "completed":
            project.completed_at = func.now()
        
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def update_script_data(
        self,
        project_id: int,
        script_data: dict
    ):
        """تحديث بيانات السكريبت"""
        
        project = await self.get_project(project_id)
        if project:
            project.script_data = script_data
            await self.db.flush()
            await self.db.commit()
    
    async def update_video_path(
        self,
        project_id: int,
        video_path: str
    ):
        """تحديث مسار الفيديو"""
        
        project = await self.get_project(project_id)
        if project:
            project.video_path = video_path
            await self.db.flush()
            await self.db.commit()
    
    async def update_youtube_info(
        self,
        project_id: int,
        video_id: str,
        url: str
    ):
        """تحديث معلومات يوتيوب"""
        
        project = await self.get_project(project_id)
        if project:
            project.youtube_video_id = video_id
            project.video_url = url
            await self.db.flush()
            await self.db.commit()
    
    async def update_processing_time(
        self,
        project_id: int,
        seconds: float
    ):
        """تحديث وقت المعالجة"""
        
        project = await self.get_project(project_id)
        if project:
            project.processing_time_seconds = int(seconds)
            await self.db.flush()
            await self.db.commit()
    
    async def update_error(
        self,
        project_id: int,
        error_message: str
    ):
        """تحديث رسالة الخطأ"""
        
        project = await self.get_project(project_id)
        if project:
            project.status = "failed"
            project.script_data = project.script_data or {}
            project.script_data['error'] = error_message
            await self.db.flush()
            await self.db.commit()
    
    async def delete_project(self, project_id: int) -> bool:
        """حذف مشروع"""
        
        project = await self.get_project(project_id)
        if not project:
            return False
        
        await self.db.delete(project)
        await self.db.commit()
        
        return True
    
    async def get_project_scenes(self, project_id: int) -> List[Scene]:
        """الحصول على مشاهد المشروع"""
        
        result = await self.db.execute(
            select(Scene)
            .where(Scene.project_id == project_id)
            .order_by(Scene.scene_number)
        )
        
        return result.scalars().all()
    
    async def create_scene(
        self,
        project_id: int,
        scene_data: dict
    ) -> Scene:
        """إنشاء مشهد جديد"""
        
        scene = Scene(
            project_id=project_id,
            scene_number=scene_data.get('scene_number'),
            script_text=scene_data.get('text'),
            visual_prompt=scene_data.get('visual_prompt'),
            duration_seconds=scene_data.get('duration_seconds', 5.0)
        )
        
        self.db.add(scene)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(scene)
        
        return scene
