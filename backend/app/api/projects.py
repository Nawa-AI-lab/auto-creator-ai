"""نقاط النهاية للمشاريع"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.database import Project, Scene
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.services.project_service import ProjectService
from app.workers.tasks import generate_video_task


router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """الحصول على قائمة المشاريع"""
    service = ProjectService(db)
    projects, total = await service.list_projects(
        skip=skip,
        limit=limit,
        status=status
    )
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """الحصول على مشروع محدد"""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    return project


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """إنشاء مشروع جديد"""
    service = ProjectService(db)
    project = await service.create_project(project_data)
    
    # بدء مهمة توليد الفيديو في الخلفية
    background_tasks.add_task(
        generate_video_task.delay,
        project_id=project.id
    )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """تحديث مشروع"""
    service = ProjectService(db)
    project = await service.update_project(project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """حذف مشروع"""
    service = ProjectService(db)
    success = await service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    return {"message": "تم حذف المشروع بنجاح"}


@router.post("/{project_id}/generate")
async def start_generation(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """بدء عملية التوليد"""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    # بدء مهمة التوليد
    background_tasks.add_task(
        generate_video_task.delay,
        project_id=project_id
    )
    
    return {"message": "تم بدء عملية التوليد", "project_id": project_id}


@router.get("/{project_id}/scenes")
async def get_project_scenes(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """الحصول على مشاهد المشروع"""
    service = ProjectService(db)
    scenes = await service.get_project_scenes(project_id)
    return {"scenes": scenes}
