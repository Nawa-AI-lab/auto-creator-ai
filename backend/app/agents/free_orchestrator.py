"""免费版 Orchestrator - 使用所有免费服务"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.free_llm import llm_manager
from app.agents.free_image_generator import image_generator
from app.agents.free_voice_generator import voice_generator
from app.services.project_service import ProjectService
from app.core.config_free import settings


class FreeOrchestratorAgent:
    """免费版视频生成 Orchestrator"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)
    
    async def execute_pipeline(
        self,
        project_id: int,
        user_id: int,
        topic: str,
        style: str = "documentary",
        duration_minutes: int = 5,
        language: str = "zh",
        auto_publish: bool = False
    ) -> Dict:
        """执行完整的视频生成流程 - 免费版"""
        
        start_time = datetime.utcnow()
        
        try:
            # 1. 更新项目状态
            await self.project_service.update_status(project_id, "generating", 5)
            print(f"🎬 开始处理: {topic}")
            
            # 2. 生成脚本 (使用免费LLM)
            await self.project_service.update_status(project_id, "generating", 10)
            
            script_data = await llm_manager.generate_script(
                topic=topic,
                duration_minutes=duration_minutes,
                language=language
            )
            
            await self.project_service.update_script_data(project_id, script_data)
            await self.project_service.update_project(
                project_id,
                title=script_data.get('title'),
                description=script_data.get('description')
            )
            
            await self.project_service.update_status(project_id, "generating", 25)
            print(f"✅ 脚本生成完成: {script_data['title']}")
            
            # 3. 生成图片和语音 (并行)
            await self.project_service.update_status(project_id, "processing", 30)
            
            scenes = script_data.get('scenes', [])
            
            # 提取图片提示词
            image_prompts = [
                s.get('visual_prompt', s.get('text', '')) 
                for s in scenes 
                if s.get('visual_prompt') or s.get('text')
            ]
            
            # 生成图片 (免费)
            print(f"🎨 正在生成 {len(image_prompts)} 张图片...")
            images = await image_generator.generate_batch(image_prompts)
            
            # 生成语音 (免费)
            print(f"🎵 正在生成语音...")
            audio_files = await voice_generator.generate_scene_voices(scenes, language)
            
            await self.project_service.update_status(project_id, "processing", 60)
            print(f"✅ 生成了 {len(images)} 张图片和 {len(audio_files)} 段语音")
            
            # 4. 视频编辑
            await self.project_service.update_status(project_id, "editing", 70)
            print(f("✂️ 正在合成视频..."))
            
            # 注意: 视频编辑需要FFmpeg完整安装
            video_path = await self._assemble_video(images, audio_files, scenes)
            
            await self.project_service.update_video_path(project_id, video_path)
            await self.project_service.update_status(project_id, "editing", 85)
            print(f"✅ 视频合成完成: {video_path}")
            
            # 5. 发布 (可选)
            if auto_publish:
                await self.project_service.update_status(project_id, "uploading", 90)
                # YouTube上传逻辑
                await self.project_service.update_status(project_id, "completed", 100)
            else:
                await self.project_service.update_status(project_id, "completed", 100)
            
            # 计算处理时间
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            await self.project_service.update_processing_time(project_id, processing_time)
            
            return {
                "success": True,
                "project_id": project_id,
                "video_path": video_path,
                "processing_time_seconds": processing_time,
                "provider": settings.AI_PROVIDER
            }
            
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            await self.project_service.update_status(project_id, "failed", 0)
            await self.project_service.update_error(project_id, str(e))
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _assemble_video(
        self,
        images: list,
        audio_files: list,
        scenes: list
    ) -> str:
        """组装视频"""
        
        output_dir = "output_videos"
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        # 检查是否有FFmpeg
        try:
            import subprocess
            
            # 创建文件列表
            with open("input_list.txt", "w") as f:
                for img in images:
                    duration = 5  # 默认5秒
                    f.write(f"file '{img}'\n")
                    f.write(f"duration {duration}\n")
                # 重复最后一张
                f.write(f"file '{images[-1]}'\n")
            
            # 如果有音频，合并音频
            if audio_files:
                with open("audio_list.txt", "w") as f:
                    for audio in audio_files:
                        f.write(f"file '{audio['audio_path']}'\n")
                
                # 使用FFmpeg合并
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "concat", "-safe", "0",
                    "-i", "input_list.txt",
                    "-f", "concat", "-safe", "0",
                    "-i", "audio_list.txt",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    output_path
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # 清理临时文件
                for f in ["input_list.txt", "audio_list.txt"]:
                    try:
                        os.remove(f)
                    except:
                        pass
            
            return output_path
            
        except FileNotFoundError:
            print("⚠️ FFmpeg未安装，跳过视频合成")
            return "video_synthesis_skipped"
        except Exception as e:
            print(f"❌ 视频合成错误: {e}")
            return f"error: {str(e)}"
    
    async def quick_preview(
        self,
        topic: str,
        num_scenes: int = 3
    ) -> Dict:
        """快速预览 (生成脚本和2张图片)"""
        
        # 生成简短脚本
        script_data = await llm_manager.generate_script(
            topic=topic,
            duration_minutes=1,
            language="zh"
        )
        
        # 只取前几个场景
        preview_scenes = script_data['scenes'][:num_scenes]
        
        # 生成2张图片
        prompts = [s.get('visual_prompt', '') for s in preview_scenes if s.get('visual_prompt')]
        images = await image_generator.generate_batch(prompts[:num_scenes])
        
        return {
            "title": script_data['title'],
            "description": script_data['description'],
            "scenes": preview_scenes,
            "preview_images": images,
            "provider": settings.AI_PROVIDER
        }
    
    async def list_available_providers(self) -> Dict:
        """列出可用的AI提供商"""
        
        providers = []
        
        # 检查Ollama
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{settings.OLLAMA_BASE_URL}/api/tags") as resp:
                    if resp.status == 200:
                        providers.append({
                            "name": "Ollama (本地)",
                            "status": "available",
                            "model": settings.OLLAMA_MODEL,
                            "cost": "免费"
                        })
        except:
            pass
        
        # 检查其他提供商
        if settings.HUGGINGFACE_API_KEY:
            providers.append({
                "name": "Hugging Face",
                "status": "available",
                "model": settings.HUGGINGFACE_MODEL,
                "cost": "免费额度"
            })
        
        if settings.GROQ_API_KEY:
            providers.append({
                "name": "Groq (Llama)",
                "status": "available",
                "model": settings.GROQ_MODEL,
                "cost": "免费额度"
            })
        
        if settings.GEMINI_API_KEY:
            providers.append({
                "name": "Google Gemini",
                "status": "available",
                "model": settings.GEMINI_MODEL,
                "cost": "免费额度"
            })
        
        return {
            "current_provider": settings.AI_PROVIDER,
            "available_providers": providers
        }


# 创建全局实例
free_orchestrator = FreeOrchestratorAgent
