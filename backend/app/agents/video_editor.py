"""وكيل المونتاج والفيديو"""
import os
import subprocess
from typing import List, Dict
from pathlib import Path
from app.core.config import settings


class VideoEditorAgent:
    """وكيل متخصص في تركيب الفيديو"""
    
    def __init__(self):
        self.output_dir = "output_videos"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def assemble_video(
        self,
        images: List[str],
        audio_files: List[str],
        output_filename: str = None,
        subtitles: List[Dict] = None,
        add_ken_burns: bool = True
    ) -> str:
        """تركيب الفيديو النهائي"""
        
        output_filename = output_filename or f"video_{hash(str(images))}.mp4"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # إنشاء قائمة الصور مع المدد
        input_file = await self._create_input_file(images)
        
        # بناء أمر FFmpeg
        cmd = self._build_ffmpeg_command(
            input_file=input_file,
            audio_files=audio_files,
            output_path=output_path,
            subtitles=subtitles,
            add_ken_burns=add_ken_burns
        )
        
        # تنفيذ الأمر
        await self._run_ffmpeg(cmd)
        
        # حذف الملفات المؤقتة
        self._cleanup(input_file)
        
        return output_path
    
    async def _create_input_file(self, images: List[str]) -> str:
        """إنشاء ملف الإدخال لـ FFmpeg"""
        
        lines = []
        for img in images:
            duration = settings.VIDEO_DURATION_PER_IMAGE
            lines.append(f"file '{img}'")
            lines.append(f"duration {duration}")
        
        # تكرار آخر صورة
        lines.append(f"file '{images[-1]}'")
        
        content = '\n'.join(lines)
        input_file = "input_list.txt"
        
        with open(input_file, 'w') as f:
            f.write(content)
        
        return input_file
    
    def _build_ffmpeg_command(
        self,
        input_file: str,
        audio_files: List[str],
        output_path: str,
        subtitles: List[Dict] = None,
        add_ken_burns: bool = True
    ) -> list:
        """بناء أمر FFmpeg"""
        
        cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0']
        
        # ملف الإدخال
        cmd.extend(['-i', input_file])
        
        # دمج ملفات الصوت
        if audio_files:
            # إنشاء ملف concat للصوت
            audio_concat = self._concat_audio_files(audio_files)
            cmd.extend(['-i', audio_concat])
        
        # إعدادات الفيديو
        cmd.extend([
            '-vf', f"scale={settings.VIDEO_WIDTH}:{settings.VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={settings.VIDEO_WIDTH}:{settings.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k'
        ])
        
        # إضافة الترجمات
        if subtitles:
            subtitle_file = self._create_subtitle_file(subtitles)
            cmd.extend(['-vf', f"subtitles={subtitle_file}"])
        
        # ملف الإخراج
        cmd.append(output_path)
        
        return cmd
    
    def _concat_audio_files(self, audio_files: List[str]) -> str:
        """دمج ملفات الصوت"""
        
        concat_file = "audio_concat.txt"
        
        with open(concat_file, 'w') as f:
            for audio in audio_files:
                f.write(f"file '{audio}'\n")
        
        return concat_file
    
    def _create_subtitle_file(self, subtitles: List[Dict]) -> str:
        """إنشاء ملف الترجمات"""
        
        srt_content = ""
        
        for i, sub in enumerate(subtitles, 1):
            start = self._format_time(sub.get('start_time', 0))
            end = self._format_time(sub.get('end_time', sub.get('start_time', 0) + 5))
            text = sub.get('text', '')
            
            srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
        
        subtitle_file = "subtitles.srt"
        
        with open(subtitle_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        return subtitle_file
    
    def _format_time(self, seconds: float) -> str:
        """تنسيق الوقت لـ SRT"""
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    async def _run_ffmpeg(self, cmd: list):
        """تشغيل FFmpeg"""
        
        process = await subprocess.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='ignore')
            raise Exception(f"فشل FFmpeg: {error_msg}")
    
    def _cleanup(self, *files):
        """حذف الملفات المؤقتة"""
        
        for f in files:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    
    async def add_intro(
        self,
        video_path: str,
        intro_path: str,
        output_path: str
    ) -> str:
        """إضافة مقدمة للفيديو"""
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', intro_path,
            '-filter_complex', '[0:v][1:v] concat=n=2:v=1:a=1 [v] [a]',
            '-map', '[v]',
            '-map', '[a]',
            output_path
        ]
        
        await self._run_ffmpeg(cmd)
        
        return output_path
    
    async def add_watermark(
        self,
        video_path: str,
        watermark_path: str,
        output_path: str,
        position: str = "bottomright"
    ) -> str:
        """إضافة علامة مائية"""
        
        position_map = {
            'topleft': '10:10',
            'topright': 'W-w-10:10',
            'bottomleft': '10:H-h-10',
            'bottomright': 'W-w-10:H-h-10'
        }
        
        overlay = position_map.get(position, position_map['bottomright'])
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', watermark_path,
            '-filter_complex', f"[0:v][1:v] overlay={overlay}",
            '-c:a', 'copy',
            output_path
        ]
        
        await self._run_ffmpeg(cmd)
        
        return output_path
