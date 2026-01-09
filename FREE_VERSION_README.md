# 🚀 AutoCreator AI - 免费版本

**完全免费的AI视频生成器！**

本版本使用100%免费的服务，无需任何API密钥即可开始使用。

---

## 🎯 免费服务对比

| 服务 | 付费版 | 免费版 | 每月免费额度 |
|------|--------|--------|-------------|
| **文本生成** | GPT-4 ($0.03/1K tokens) | Ollama/Llama | 无限本地运行 |
| **图片生成** | DALL-E 3 ($0.04/张) | Stable Diffusion XL | 无限本地运行 |
| **语音合成** | ElevenLabs ($0.30/分钟) | Edge TTS | 无限免费 |
| **托管费用** | $20+/月 | Render免费版 | $0 |

---

## 🛠️ 安装步骤

### 1️⃣ 克隆项目

```bash
git clone https://github.com/Nawa-AI-lab/auto-creator-ai.git
cd auto-creator-ai
```

### 2️⃣ 安装依赖

```bash
cd backend
pip install -r ../requirements-free.txt
```

### 3️⃣ 安装本地模型 (可选，但推荐)

#### 安装 Ollama (免费本地LLM)

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve

# 下载模型 (选择一个)
ollama pull llama2        # 7B参数，英文最佳
ollama pull mistral       # 7B参数，多语言
ollama pull qwen:7b       # 7B参数，中文优化
```

#### 安装 Stable Diffusion (免费本地图片生成)

```bash
# 需要NVIDIA显卡
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install diffusers accelerate

# 或使用CPU版本 (较慢)
pip install diffusers
```

#### 安装 Edge TTS (免费语音)

```bash
pip install edge-tts
```

---

## ⚙️ 配置

### 方式一：完全本地 (推荐)

```bash
cd backend

# 创建 .env 文件
cat > .env << EOF
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

TTS_PROVIDER=edge
EDGE_VOICE=zh-CN-XiaoxiaoNeural
EOF
```

### 方式二：混合模式 (部分本地，部分云端)

```bash
cat > .env << EOF
# 使用Groq的免费Llama (速度快)
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama2-70b-4096

# 使用Hugging Face图片生成
HF_TOKEN=your_hf_token_here

# 语音使用Edge TTS (完全免费)
TTS_PROVIDER=edge
EOF
```

---

## 🚀 启动服务

### 启动后端

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 启动前端 (新终端)

```bash
cd frontend
npm install
npm run dev
```

### 打开浏览器

```
http://localhost:3000
```

---

## 📋 快速测试

### 测试1：检查可用的AI提供商

```bash
curl http://localhost:8000/api/health
```

### 测试2：生成预览

```python
import requests

response = requests.post(
    "http://localhost:8000/api/projects",
    json={
        "topic": "人工智能的历史",
        "duration": 2,
        "language": "zh"
    }
)

print(response.json())
```

---

## 🐛 常见问题

### Q: Ollama连不上？

```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 如果服务未运行
ollama serve
```

### Q: 图片生成很慢？

**解决方案：**
1. 确保有NVIDIA显卡
2. 使用较小的图片尺寸 (512x512)
3. 减少推理步数 (从30降到15)

### Q: 语音不工作？

```bash
# 安装edge-tts
pip install edge-tts

# 测试语音
edge-tts -t "你好" -v zh-CN-XiaoxiaoNeural -o test.mp3
```

### Q: 如何切换AI提供商？

编辑 `.env` 文件：

```bash
# 使用本地Ollama
AI_PROVIDER=ollama

# 使用Hugging Face
AI_PROVIDER=huggingface

# 使用Groq
AI_PROVIDER=groq

# 使用Gemini
AI_PROVIDER=gemini
```

---

## 💡 性能优化建议

### 1. 使用更小的模型

```bash
# 在Ollama中使用更小的模型
ollama pull llama2:7b     # 7B参数
ollama pull phi           # 2.7B参数，更快
```

### 2. 减少图片数量

默认生成较多图片以保证质量。可以在代码中减少：

```python
# 在 free_orchestrator.py 中
num_images = min(len(prompts), 3)  # 最多3张图片
```

### 3. 使用GPU加速

```bash
# 确认PyTorch使用GPU
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 📊 成本对比

### 付费版本 (OpenAI + ElevenLabs)

| 项目 | 单价 | 每次视频成本 |
|------|------|-------------|
| GPT-4 脚本 | $0.03/1K tokens | $0.05 |
| DALL-E 3 (10张) | $0.04/张 | $0.40 |
| ElevenLabs (1分钟) | $0.30/分钟 | $0.30 |
| **总计** | - | **$0.75/视频** |

### 免费版本 (本地运行)

| 项目 | 成本 | 说明 |
|------|------|------|
| Ollama (Llama 2) | $0 | 本地运行 |
| Stable Diffusion XL | $0 | 本地运行 |
| Edge TTS | $0 | 微软免费 |
| **总计** | **$0** | 无限使用 |

---

## 🎓 学习资源

- [Ollama官方文档](https://github.com/ollama/ollama)
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Edge TTS项目](https://github.com/rany2/edge-tts)
- [Hugging Face Inference](https://huggingface.co/inference-api)

---

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**🎉 祝您使用愉快！**
