"""وكيل كتابة السكريبت"""
import json
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from app.core.config import settings


class ScriptWriterAgent:
    """وكيل متخصص في كتابة السكريبتات"""
    
    SYSTEM_PROMPT = """أنت كاتب محتوى محترف متخصص في كتابة السكريبتات للفيديوهات التعليمية والوثائقية.
مهمتك هي تحويل فكرة عامة إلى سكريبت كامل مع مشاهد واضحة.

التزم بالمتطلبات التالية:
1. اكتب بالعربية الفصحى السلسة
2. قسّم المحتوى إلى مشاهد منطقية
3. لكل مشهد: النص الذي سيُقال + وصف بصري لتوليد صورة مناسبة
4. اجعل السرد جذاباً وسهل المتابعة
5. أضف عنواناً ووصفاً مناسبين ليوتيوب

أخرج النتائج بتنسيق JSON فقط."""

    def __init__(self, client: AsyncOpenAI = None):
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_script(
        self,
        topic: str,
        duration_minutes: int = 5,
        style: str = "documentary",
        language: str = "ar"
    ) -> Dict:
        """توليد سكريبت كامل"""
        
        user_prompt = f"""
الفكرة الرئيسية: {topic}
المدة المطلوبة: {{duration_minutes}} دقائق
أسلوب الفيديو: {style}
اللغة: {"العربية" if language == "ar" else "English"}

أنتج سكريبت كامل مع:
- عنوان جذاب للفيديو
- وصف مناسب للسيو
- تقسيم إلى مشاهد (حوالي {duration_minutes * 2} مشهد)
- لكل مشهد: النص المقروء + وصف الصورة المطلوبة

أخرج بتنسيق JSON:
{{
    "title": "عنوان الفيديو",
    "description": "وصف الفيديو",
    "scenes": [
        {{
            "scene_number": 1,
            "text": "النص المقروء في هذا المشهد",
            "visual_prompt": "وصف دقيق للصورة المطلوبة بالإنجليزية",
            "duration_seconds": 5
        }}
    ],
    "tags": ["tag1", "tag2", "tag3"],
    "estimated_duration": {duration_minutes}
}}
"""
        
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def generate_ideas(
        self,
        niche: str,
        count: int = 10
    ) -> List[str]:
        """توليد أفكار محتوى"""
        
        user_prompt = f"""
أنتج {count} فكرة محتوى لفيديوهات في المجال: {niche}

الصيغة:
- كل فكرة في سطر واحد
- تكون متنوعة وجذابة
- مناسبة لمنصات التواصل

أخرج فقط قائمة أفكار (كل فكرة في سطر جديد).
"""
        
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "أنت مسوق محتوى محترف"},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.9
        )
        
        ideas = response.choices[0].message.content.strip().split('\n')
        return [idea.strip().lstrip('0123456789.- ') for idea in ideas if idea.strip()]
    
    async def improve_seo(
        self,
        title: str,
        description: str,
        keywords: List[str]
    ) -> Dict:
        """تحسين العنوان والوصف للسيو"""
        
        user_prompt = f"""
عنوان الفيديو: {title}
وصف الفيديو: {description}
الكلمات المفتاحية: {', '.join(keywords)}

المطلوب:
1. تحسين العنوان ليكون أكثر جاذبية (60 حرفاً كحد أقصى)
2. تحسين الوصف ليوتيوب (أقل من 5000 حرف)
3. اقتراح tags مناسبة

أخرج JSON:
{{
    "improved_title": "العنوان المحسن",
    "improved_description": "الوصف المحسن",
    "suggested_tags": ["tag1", "tag2", ...]
}}
"""
        
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "أنت خبير سيو ليوتيوب"},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
