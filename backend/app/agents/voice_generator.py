"""وكيل توليد الصوت"""
import os
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings


class VoiceGeneratorAgent:
    """وكيل متخصص في تحويل النص إلى صوت"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache_dir = "generated_audio"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def generate_voice(
        self,
        text: str,
        voice_id: str = None,
        language: str = "ar",
        output_path: str = None
    ) -> str:
        """توليد صوت من نص"""
        
        voice_id = voice_id or (
            settings.ARABIC_VOICE_ID if language == "ar" 
            else settings.ELEVENLABS_VOICE_ID
        )
        
        # استخدام ElevenLabs
        try:
            from elevenlabs import AsyncClient
            eleven_client = AsyncClient(api_key=settings.ELEVENLABS_API_KEY)
            
            audio = await eleven_client.generate(
                text=text,
                voice_id=voice_id,
                model_id=settings.ELEVENLABS_MODEL_ID,
                output_format="mp3_44100_128"
            )
            
            # حفظ الملف
            filename = f"voice_{hash(text)}.mp3"
            filepath = os.path.join(self.cache_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(audio)
            
            return filepath
            
        except Exception as e:
            # Fallback to OpenAI TTS
            return await self._generate_with_openai(text, output_path, language)
    
    async def _generate_with_openai(
        self,
        text: str,
        output_path: str = None,
        language: str = "ar"
    ) -> str:
        """توليد الصوت باستخدام OpenAI TTS"""
        
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="mp3"
        )
        
        output_path = output_path or f"speech_{hash(text)}.mp3"
        response.stream_to_file(output_path)
        
        return output_path
    
    async def generate_scene_voices(
        self,
        scenes: list,
        language: str = "ar"
    ) -> list:
        """توليد صوت لكل مشهد"""
        
        audio_files = []
        
        for scene in scenes:
            text = scene.get('text', '')
            if text:
                audio_path = await self.generate_voice(
                    text=text,
                    language=language
                )
                audio_files.append({
                    'scene_number': scene.get('scene_number'),
                    'audio_path': audio_path,
                    'duration': self._estimate_duration(text)
                })
        
        return audio_files
    
    def _estimate_duration(self, text: str, wpm: int = 150) -> float:
        """تقدير مدة الصوت"""
        
        word_count = len(text.split())
        duration_minutes = word_count / wpm
        return duration_minutes * 60  # بالثواني
    
    async def clone_voice(self, audio_file: str, name: str) -> str:
        """استنساخ صوت من عينة صوتية (ElevenLabs API)"""
        
        try:
            from elevenlabs import VoiceCloning
            
            clone_client = VoiceCloning(api_key=settings.ELEVENLABS_API_KEY)
            
            with open(audio_file, 'rb') as f:
                voice = clone_client.clone(
                    name=name,
                    samples=[f]
                )
            
            return voice.voice_id
            
        except Exception as e:
            raise Exception(f"فشل استنساخ الصوت: {str(e)}")
