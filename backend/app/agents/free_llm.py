"""免费AI写作代理 - 支持多种免费模型"""
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

from app.core.config_free import settings


class BaseLLM(ABC):
    """LLM基类"""
    
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        pass


class OllamaLLM(BaseLLM):
    """Ollama本地免费模型"""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
    
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用Ollama生成文本"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                result = await response.json()
                return result.get("response", "")


class HuggingFaceLLM(BaseLLM):
    """Hugging Face免费推理API"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.HUGGINGFACE_API_KEY
        self.model = model or settings.HUGGINGFACE_MODEL
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """调用Hugging Face API"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            async with session.post(
                f"https://api-inference.huggingface.co/models/{self.model}",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                
                if isinstance(result, list):
                    return result[0].get("generated_text", "")
                return str(result)


class GroqLLM(BaseLLM):
    """Groq免费Llama模型 (速度快)"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
    
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用Groq API"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                return result["choices"][0]["message"]["content"]


class GeminiLLM(BaseLLM):
    """Google Gemini免费模型"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """调用Gemini API"""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        return response.text


class FreeLLMManager:
    """免费AI管理器 - 自动选择最佳模型"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """初始化可用的提供商"""
        # Ollama (本地)
        if settings.OLLAMA_BASE_URL:
            self.providers["ollama"] = OllamaLLM()
        
        # Hugging Face
        if settings.HUGGINGFACE_API_KEY:
            self.providers["huggingface"] = HuggingFaceLLM()
        
        # Groq
        if settings.GROQ_API_KEY:
            self.providers["groq"] = GroqLLM()
        
        # Gemini
        if settings.GEMINI_API_KEY:
            self.providers["gemini"] = GeminiLLM()
    
    def get_best_provider(self) -> BaseLLM:
        """获取最佳可用的提供商"""
        provider = settings.AI_PROVIDER
        
        if provider in self.providers:
            return self.providers[provider]
        
        # 回退到第一个可用的
        for name, llm in self.providers.items():
            print(f"⚠️ 使用回退提供商: {name}")
            return llm
        
        raise ValueError("没有可用的AI提供商！请配置至少一个免费模型。")
    
    async def generate_script(
        self,
        topic: str,
        duration_minutes: int = 5,
        language: str = "zh"
    ) -> Dict:
        """生成视频脚本"""
        
        llm = self.get_best_provider()
        
        # 根据语言生成提示
        lang_name = "中文" if language == "zh" else "English"
        
        prompt = f"""你是一个专业的视频内容创作者。请为以下主题创建一个视频脚本：

主题: {topic}
时长: {duration_minutes}分钟
语言: {lang_name}

请按以下JSON格式输出:
{{
    "title": "吸引人的标题",
    "description": "视频描述(用于SEO)",
    "scenes": [
        {{
            "scene_number": 1,
            "text": "旁白文字",
            "visual_prompt": "图片描述(用于AI生成图片)",
            "duration_seconds": 5
        }}
    ],
    "tags": ["标签1", "标签2"],
    "estimated_duration": {duration_minutes}
}}

只输出JSON，不要有其他内容。"""
        
        response = await llm.generate(prompt, max_tokens=3000)
        
        # 清理和解析JSON
        response = response.strip()
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        return json.loads(response)
    
    async def generate_ideas(self, niche: str, count: int = 10) -> List[str]:
        """生成内容创意"""
        
        llm = self.get_best_provider()
        
        prompt = f"""为以下领域生成{count}个视频内容创意：

领域: {niche}

要求:
1. 创意要独特且吸引人
2. 适合短视频平台
3. 简短描述每个创意

只输出创意列表，每行一个。"""
        
        response = await llm.generate(prompt, max_tokens=1000)
        
        ideas = [line.strip() for line in response.split('\n') if line.strip()]
        return ideas[:count]


# 全局实例
llm_manager = FreeLLMManager()
