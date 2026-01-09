"""免费图片生成器 - 使用Hugging Face Diffusers"""
import os
import asyncio
from typing import List, Optional
from PIL import Image
import io
import base64

# 尝试导入，如果不可用则跳过
try:
    from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
    import torch
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print("⚠️ Diffusers未安装，将使用API模式")


class FreeImageGenerator:
    """免费图片生成器"""
    
    def __init__(self):
        self.cache_dir = "generated_images"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.pipe = None
        self._init_pipeline()
    
    def _init_pipeline(self):
        """初始化本地Stable Diffusion XL"""
        if not DIFFUSERS_AVAILABLE:
            return
        
        try:
            print("📦 正在加载Stable Diffusion XL模型...")
            scheduler = EulerAncestralDiscreteScheduler(
                tau_min=0.05,
                tau_max=0.5,
                beta_min=0.00085,
                beta_max=0.012
            )
            
            self.pipe = StableDiffusionXLPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16,
                variant="fp16"
            )
            self.pipe.scheduler = scheduler
            self.pipe.to("cuda" if torch.cuda.is_available() else "cpu")
            print("✅ Stable Diffusion XL加载成功！")
        except Exception as e:
            print(f"⚠️ 无法加载本地模型: {e}")
            self.pipe = None
    
    async def generate_image(
        self,
        prompt: str,
        size: tuple = (1024, 1024),
        save_to_disk: bool = True
    ) -> str:
        """生成单张图片"""
        
        # 增强提示词
        enhanced_prompt = self._enhance_prompt(prompt)
        
        if self.pipe and not DIFFUSERS_AVAILABLE:
            # 本地生成
            return await self._generate_local(enhanced_prompt, size, save_to_disk)
        else:
            # 使用Hugging Face API
            return await self._generate_via_api(enhanced_prompt, size, save_to_disk)
    
    def _enhance_prompt(self, prompt: str) -> str:
        """增强提示词以获得更好的图片"""
        
        enhancements = [
            "masterpiece, best quality",
            "highly detailed",
            "professional photography",
            "cinematic lighting",
            "8k resolution"
        ]
        
        return f"{prompt}, {', '.join(enhancements)}"
    
    async def _generate_local(
        self,
        prompt: str,
        size: tuple,
        save_to_disk: bool
    ) -> str:
        """使用本地模型生成"""
        
        if not self.pipe:
            raise ValueError("本地模型未加载")
        
        # 在线程池中运行以避免阻塞
        loop = asyncio.get_event_loop()
        
        def run_inference():
            result = self.pipe(
                prompt,
                height=size[1],
                width=size[0],
                guidance_scale=7.5,
                num_inference_steps=30
            )
            return result.images[0]
        
        image = await loop.run_in_executor(None, run_inference)
        
        if save_to_disk:
            filename = f"img_{hash(prompt)}.png"
            filepath = os.path.join(self.cache_dir, filename)
            image.save(filepath, "PNG")
            return filepath
        
        # 返回Base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
    
    async def _generate_via_api(
        self,
        prompt: str,
        size: tuple,
        save_to_disk: bool
    ) -> str:
        """使用Hugging Face Inference API"""
        
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # 使用免费的FLUX模型或其他免费模型
            # https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell
            
            headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "width": size[0],
                    "height": size[1],
                    "guidance_scale": 7.5
                }
            }
            
            try:
                async with session.post(
                    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        if save_to_disk:
                            filename = f"img_{hash(prompt)}.png"
                            filepath = os.path.join(self.cache_dir, filename)
                            image.save(filepath, "PNG")
                            return filepath
                        
                        return f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"
                    else:
                        # 如果HF API失败，使用占位图
                        return self._create_placeholder(prompt, save_to_disk)
                        
            except Exception as e:
                print(f"❌ HF API错误: {e}")
                return self._create_placeholder(prompt, save_to_disk)
    
    def _create_placeholder(self, prompt: str, save_to_disk: bool) -> str:
        """创建占位图"""
        
        # 创建简单的占位图片
        img = Image.new('RGB', (1024, 1024), color=(73, 109, 137))
        
        if save_to_disk:
            filename = f"placeholder_{hash(prompt)}.png"
            filepath = os.path.join(self.cache_dir, filename)
            img.save(filepath, "PNG")
            return filepath
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
    
    async def generate_batch(
        self,
        prompts: List[str],
        parallel: bool = True
    ) -> List[str]:
        """批量生成图片"""
        
        if parallel:
            tasks = [self.generate_image(p) for p in prompts]
            results = await asyncio.gather(*tasks)
        else:
            results = []
            for prompt in prompts:
                image = await self.generate_image(prompt)
                results.append(image)
        
        return results


# 创建全局实例
image_generator = FreeImageGenerator()
