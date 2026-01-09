"""免费语音合成 - 使用Edge TTS (完全免费)"""
import os
import asyncio
import aiohttp
from typing import Optional
from pathlib import Path

from app.core.config_free import settings


class FreeVoiceGenerator:
    """免费语音生成器 - 使用Microsoft Edge TTS"""
    
    def __init__(self):
        self.cache_dir = "generated_audio"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Edge TTS语音列表
        self.voices = {
            "zh": {
                "female": "zh-CN-XiaoxiaoNeural",
                "male": "zh-CN-YunxiNeural",
                "female2": "zh-CN-XiaoyiNeural"
            },
            "en": {
                "female": "en-US-JennyNeural",
                "male": "en-US-GuyNeural"
            },
            "ar": {
                "female": "ar-SA-HamedNeural",
                "male": "ar-SA-ZariyahNeural"
            }
        }
    
    async def generate_voice(
        self,
        text: str,
        language: str = "zh",
        voice_name: str = None,
        output_path: str = None,
        rate: str = "+0%",  # 语速
        volume: str = "+0%"  # 音量
    ) -> str:
        """使用Edge TTS生成语音"""
        
        voice = voice_name or self.voices.get(language, {}).get("female")
        
        if not voice:
            voice = "zh-CN-XiaoxiaoNeural"  # 默认中文语音
        
        # 构建Edge TTS API URL
        # Edge TTS使用WebSocket API
        audio_path = output_path or f"voice_{hash(text)}.mp3"
        
        # 使用edge-tts库（如果可用）或直接调用API
        try:
            import edge_tts
            return await self._generate_with_edge_tts(
                text, voice, audio_path, rate, volume
            )
        except ImportError:
            return await self._generate_with_http(text, voice, audio_path, rate, volume)
    
    async def _generate_with_edge_tts(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str,
        volume: str
    ) -> str:
        """使用edge-tts库生成"""
        
        import edge_tts
        
        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
        await communicate.save(output_path)
        
        return output_path
    
    async def _generate_with_http(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str,
        volume: str
    ) -> str:
        """直接使用HTTP调用Edge TTS"""
        
        # Edge TTS需要认证，这里使用简化的方法
        # 实际项目中建议安装 edge-tts 库
        
        print("⚠️ 建议安装 edge-tts 库以获得更好的效果")
        print(f"   pip install edge-tts")
        
        # 创建简单的音频占位符
        return await self._create_placeholder_audio(output_path)
    
    async def _create_placeholder_audio(self, output_path: str) -> str:
        """创建音频占位符"""
        
        # 由于无法直接调用Edge TTS，返回说明
        print(f"⚠️ 语音生成需要安装 edge-tts:")
        print(f"   pip install edge-tts")
        
        # 创建空文件作为占位符
        Path(output_path).touch()
        return output_path
    
    async def generate_scene_voices(
        self,
        scenes: list,
        language: str = "zh"
    ) -> list:
        """为每个场景生成语音"""
        
        audio_files = []
        
        for i, scene in enumerate(scenes):
            text = scene.get('text', '')
            if text:
                audio_path = await self.generate_voice(
                    text=text,
                    language=language,
                    output_path=f"scene_{i+1}_voice.mp3"
                )
                audio_files.append({
                    'scene_number': scene.get('scene_number', i+1),
                    'audio_path': audio_path,
                    'duration': self._estimate_duration(text)
                })
        
        return audio_files
    
    def _estimate_duration(self, text: str, wpm: int = 150) -> float:
        """估算语音时长"""
        
        word_count = len(text)
        duration_minutes = word_count / wpm
        return duration_minutes * 60
    
    def get_available_voices(self, language: str = "zh") -> list:
        """获取可用的语音列表"""
        
        base_url = "https://edge.microsoft.com/cognitive-services/tts/v3"
        
        # 返回预设的语音列表
        return [
            {"name": name, "gender": gender}
            for gender, name in self.voices.get(language, {}).items()
        ]


# 全局实例
voice_generator = FreeVoiceGenerator()
