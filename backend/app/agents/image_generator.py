"""وكيل توليد الصور"""
import base64
import os
from typing import List, Optional
from openai import AsyncOpenAI
from app.core.config import settings


class ImageGeneratorAgent:
    """وكيل متخصص في توليد الصور باستخدام DALL-E"""
    
    def __init__(self, client: AsyncOpenAI = None):
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache_dir = "generated_images"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def generate_image(
        self,
        prompt: str,
        size: str = None,
        quality: str = None,
        save_to_disk: bool = True
    ) -> str:
        """توليد صورة واحدة"""
        
        size = size or settings.DALL_E_SIZE
        quality = quality or settings.DALL_E_QUALITY
        
        response = await self.client.images.generate(
            model=settings.DALL_E_MODEL,
            prompt=self._enhance_prompt(prompt),
            size=size,
            quality=quality,
            n=1
        )
        
        image_url = response.data[0].url
        
        if save_to_disk:
            image_path = await self._download_and_save(image_url, prompt)
            return image_path
        
        return image_url
    
    async def generate_batch(
        self,
        prompts: List[str],
        parallel: bool = True
    ) -> List[str]:
        """توليد مجموعة صور"""
        
        if parallel:
            # توليد متوازي
            import asyncio
            tasks = [self.generate_image(p) for p in prompts]
            results = await asyncio.gather(*tasks)
        else:
            # توليد تسلسلي
            results = []
            for prompt in prompts:
                image = await self.generate_image(prompt)
                results.append(image)
        
        return results
    
    def _enhance_prompt(self, prompt: str) -> str:
        """تحسين الوصف للحصول على صورة أفضل"""
        
        enhancements = [
            "high quality",
            "professional photography",
            "cinematic lighting",
            "4K resolution",
            "detailed"
        ]
        
        # إضافة تحسينات حسب نوع المحتوى
        if "documentary" in prompt.lower():
            enhancements.extend([
                "historical accuracy",
                "authentic atmosphere"
            ])
        
        enhanced_prompt = f"{prompt}, {', '.join(enhancements)}"
        return enhanced_prompt
    
    async def _download_and_save(
        self,
        image_url: str,
        prompt: str
    ) -> str:
        """تحميل الصورة وحفظها"""
        
        import httpx
        from pathlib import Path
        
        # إنشاء اسم الملف
        safe_name = "".join(c for c in prompt[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{safe_name}_{hash(prompt)}.png"
        filepath = Path(self.cache_dir) / filename
        
        # تحميل الصورة
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
        
        return str(filepath)
    
    async def generate_variations(
        self,
        original_prompt: str,
        count: int = 3
    ) -> List[str]:
        """توليد تنويعات من صورة واحدة"""
        
        variations = []
        
        for i in range(count):
            variant_prompt = f"{original_prompt}, variation {i+1} with different composition"
            image = await self.generate_image(variant_prompt)
            variations.append(image)
        
        return variations
