"""AutoCreator AI Backend - Minimal Version (بدون Pydantic)"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sqlite3
import asyncio
from typing import List, Optional
import json
from datetime import datetime
from pathlib import Path


# === إعدادات بسيطة ===
DATABASE_FILE = "autocreator.db"


# === قاعدة البيانات ===
def init_db():
    """تهيئة قاعدة البيانات SQLite"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            title TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            language TEXT DEFAULT 'ar',
            style TEXT DEFAULT 'documentary',
            duration INTEGER DEFAULT 5,
            script_data TEXT,
            video_path TEXT,
            video_url TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def get_db():
    """الحصول على اتصال قاعدة البيانات"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# === نموذج المشروع البسيط ===
class ProjectModel:
    """نموذج المشروع بدون Pydantic"""
    
    @staticmethod
    def create(data: dict) -> dict:
        conn = get_db()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO projects (topic, title, status, progress, language, style, duration, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('topic', ''),
            data.get('topic', ''),
            'pending',
            0,
            data.get('language', 'ar'),
            data.get('style', 'documentary'),
            data.get('duration', 5),
            now
        ))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ProjectModel.get_by_id(project_id)
    
    @staticmethod
    def get_by_id(project_id: int) -> Optional[dict]:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    @staticmethod
    def get_all(skip: int = 0, limit: int = 10) -> List[dict]:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    @staticmethod
    def update_status(project_id: int, status: str, progress: int = 0):
        conn = get_db()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            UPDATE projects SET status = ?, progress = ?, updated_at = ? WHERE id = ?
        """, (status, progress, now, project_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def update_script_data(project_id: int, script_data: dict):
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE projects SET script_data = ?, updated_at = ? WHERE id = ?
        """, (json.dumps(script_data), datetime.utcnow().isoformat(), project_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(project_id: int) -> bool:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted


# === إعداد التطبيق ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    print("🚀 بدء تشغيل AutoCreator AI...")
    init_db()
    print("✅ قاعدة البيانات SQLite جاهزة")
    yield
    print("🛑 إيقاف الخادم...")


app = FastAPI(
    title="AutoCreator AI API",
    description="وكيل ذكاء اصطناعي مجاني لصناعة المحتوى",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs"
)


# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === نقاط النهاية ===

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Welcome to AutoCreator AI",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """فحص صحة النظام"""
    return {
        "status": "healthy",
        "database": "sqlite",
        "python_version": "3.11+"
    }


@app.get("/api/projects")
async def list_projects(skip: int = 0, limit: int = 10):
    """الحصول على قائمة المشاريع"""
    projects = ProjectModel.get_all(skip=skip, limit=limit)
    return {
        "projects": projects,
        "total": len(projects)
    }


@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """الحصول على مشروع محدد"""
    project = ProjectModel.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    return project


@app.post("/api/projects")
async def create_project(request: dict):
    """إنشاء مشروع جديد"""
    try:
        project = ProjectModel.create(request)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, request: dict):
    """تحديث مشروع"""
    project = ProjectModel.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    ProjectModel.update_status(
        project_id,
        status=request.get('status', project['status']),
        progress=request.get('progress', project['progress'])
    )
    
    return ProjectModel.get_by_id(project_id)


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int):
    """حذف مشروع"""
    if not ProjectModel.get_by_id(project_id):
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    ProjectModel.delete(project_id)
    return {"message": "تم حذف المشروع بنجاح"}


@app.post("/api/projects/{project_id}/generate")
async def start_generation(project_id: int):
    """بدء عملية التوليد"""
    project = ProjectModel.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    # تحديث الحالة
    ProjectModel.update_status(project_id, "generating", 10)
    
    # TODO: استدعاء خدمة التوليد
    # في الإصدار الكامل، هنا يتم استدعاء AI agent
    
    return {
        "message": "تم بدء عملية التوليد",
        "project_id": project_id,
        "status": "generating"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
