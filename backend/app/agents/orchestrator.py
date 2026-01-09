"""ال Orchestrator - المنسق الرئيسي"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .agents.script_writer import ScriptWriterAgent
from .agents.image_generator import ImageGeneratorAgent
from .agents.voice_generator import VoiceGeneratorAgent
from .agents.video_editor import VideoEditorAgent
from .services.youtube_service import YouTubeService
from .services.project_service import ProjectService
from .core.config import settings


class OrchestratorAgent:
    """المنسق الرئيسي لخط إنتاج الفيديو"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.script_writer = ScriptWriterAgent()
        self.image_generator = ImageGeneratorAgent()
        self.voice_generator = VoiceGeneratorAgent()
        self.video_editor = VideoEditorAgent()
        self.youtube_service = YouTubeService()
        self.project_service = ProjectService(db)
    
    async def execute_pipeline(
        self,
        project_id: int,
        user_id: int,
        topic: str,
        style: str = "documentary",
        duration_minutes: int = 5,
        language: str = "ar",
        auto_publish: bool = False
    ) -> Dict:
        """تنفيذ خط الإنتاج الكامل"""
        
        start_time = datetime.utcnow()
        
        try:
            # 1. تحديث حالة المشروع
            await self.project_service.update_status(project_id, "generating", 5)
            
            # 2. توليد السكريبت
            print(f"🎬 بدء العمل على: {topic}")
            await self.project_service.update_status(project_id, "generating", 10)
            
            script_data = await self.script_writer.generate_script(
                topic=topic,
                duration_minutes=duration_minutes,
                style=style,
                language=language
            )
            
            # حفظ بيانات السكريبت
            await self.project_service.update_script_data(project_id, script_data)
            await self.project_service.update_project(
                project_id,
                title=script_data.get('title'),
                description=script_data.get('description')
            )
            
            await self.project_service.update_status(project_id, "generating", 25)
            print(f"✅ تم توليد السكريبت: {script_data['title']}")
            
            # 3. توليد الصور والأصوات بالتوازي
            await self.project_service.update_status(project_id, "processing", 30)
            
            scenes = script_data.get('scenes', [])
            image_prompts = [s['visual_prompt'] for s in scenes if 'visual_prompt' in s]
            
            # توليد الصور
            images = await self.image_generator.generate_batch(image_prompts)
            
            # توليد الأصوات
            audio_files = await self.voice_generator.generate_scene_voices(scenes, language)
            
            # ربط الصور بالأصوات
            await self._link_media_to_scenes(project_id, scenes, images, audio_files)
            
            await self.project_service.update_status(project_id, "processing", 60)
            print(f"✅ تم توليد {len(images)} صورة و {len(audio_files)} مقطع صوتي")
            
            # 4. المونتاج
            await self.project_service.update_status(project_id, "editing", 70)
            
            video_path = await self.video_editor.assemble_video(
                images=images,
                audio_files=[a['audio_path'] for a in audio_files],
                subtitles=scenes
            )
            
            await self.project_service.update_video_path(project_id, video_path)
            await self.project_service.update_status(project_id, "editing", 85)
            print(f"✅ تم تركيب الفيديو: {video_path}")
            
            # 5. النشر (اختياري)
            if auto_publish:
                await self.project_service.update_status(project_id, "uploading", 90)
                
                youtube_result = await self.youtube_service.upload_video(
                    video_path=video_path,
                    title=script_data['title'],
                    description=script_data['description'],
                    tags=script_data.get('tags', []),
                    channel_id=user_id
                )
                
                await self.project_service.update_youtube_info(
                    project_id,
                    youtube_result['video_id'],
                    youtube_result['url']
                )
                
                await self.project_service.update_status(project_id, "completed", 100)
                print(f"✅ تم النشر على يوتيوب: {youtube_result['url']}")
            else:
                await self.project_service.update_status(project_id, "completed", 100)
            
            # حساب الوقت والتكلفة
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            await self.project_service.update_processing_time(project_id, processing_time)
            
            return {
                "success": True,
                "project_id": project_id,
                "video_path": video_path,
                "processing_time_seconds": processing_time
            }
            
        except Exception as e:
            print(f"❌ خطأ في خط الإنتاج: {str(e)}")
            await self.project_service.update_status(project_id, "failed", 0)
            await self.project_service.update_error(project_id, str(e))
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _link_media_to_scenes(
        self,
        project_id: int,
        scenes: list,
        images: list,
        audio_files: list
    ):
        """ربط الوسائط بالمشاهد"""
        
        for i, scene in enumerate(scenes):
            scene_data = {
                'image_path': images[i] if i < len(images) else None,
                'audio_path': audio_files[i]['audio_path'] if i < len(audio_files) else None,
                'audio_duration': audio_files[i].get('duration', 5) if i < len(audio_files) else 5
            }
            
            # يمكن حفظ هذا في قاعدة البيانات
        
        return True
    
    async def quick_preview(
        self,
        topic: str,
        num_scenes: int = 3
    ) -> Dict:
        """معاينة سريعة (توليد سكريبت وصورتين فقط)"""
        
        # توليد سكريبت مختصر
        script_data = await self.script_writer.generate_script(
            topic=topic,
            duration_minutes=1,
            language="ar"
        )
        
        # أخذ مشهدين فقط
        preview_scenes = script_data['scenes'][:num_scenes]
        
        # توليد صورتين
        prompts = [s['visual_prompt'] for s in preview_scenes if 'visual_prompt' in s]
        images = await self.image_generator.generate_batch(prompts[:num_scenes])
        
        return {
            "title": script_data['title'],
            "description": script_data['description'],
            "scenes": preview_scenes,
            "preview_images": images
        }
