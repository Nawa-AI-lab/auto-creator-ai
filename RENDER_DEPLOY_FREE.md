# 🎬 AutoCreator AI - Render免费部署指南

**无需信用卡，零成本在Render上部署！**

---

## 📋 部署步骤

### 1️⃣ 准备Render

1. 注册 [Render.com](https://render.com) (使用GitHub登录)
2. 进入 Dashboard

### 2️⃣ 创建Web服务

1. 点击 **"New"** → **"Web Service"**
2. 连接到你的GitHub仓库
3. 选择分支: `main`
4. 设置以下配置：

| 配置项 | 值 |
|--------|-----|
| **Build Command** | `pip install -r requirements-render.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Python Version** | `3.11` |
| **Plan** | `Free` |
| **Disk** | `1 GB` (启用磁盘存储) |

5. 点击 **"Create Web Service"**

### 3️⃣ 配置环境变量

在Render服务设置中添加以下环境变量：

```env
# AI提供商 (至少一个)
GROQ_API_KEY=    # 免费Llama 2 (推荐)
HUGGINGFACE_API_KEY=  # 可选
GEMINI_API_KEY=   # 可选

# 语音合成 (可选)
ELEVENLABS_API_KEY=   # 如果需要高质量语音

# YouTube (可选)
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
```

#### 获取免费API密钥：

**Groq** (推荐 - 免费Llama 2):
1. 访问 https://console.groq.com
2. 注册并获取API密钥
3. 免费额度：足够个人使用

**Hugging Face**:
1. 访问 https://huggingface.co/settings/tokens
2. 创建新token
3. 免费额度：1000次请求/月

**Google Gemini**:
1. 访问 https://aistudio.google.com
2. 获取API密钥
3. 免费额度：60次请求/分钟

### 4️⃣ 部署完成

- 等待构建完成 (约2-3分钟)
- 访问生成的URL: `https://your-service.onrender.com`
- API文档: `https://your-service.onrender.com/docs`

---

## 🔧 常见问题

### Q: 构建失败？

```error: Read-only file system```

**解决方案：**
- 使用 `requirements-render.txt` 而不是 `requirements-free.txt`
- 这个文件不包含需要Rust编译的包

### Q: 数据库错误？

```error: could not connect to server```

**解决方案：**
- 免费层使用SQLite，不需要PostgreSQL
- 确保已启用磁盘存储 (1GB)

### Q: 语音不工作？

**解决方案：**
1. 安装edge-tts (如果可以):
   ```bash
   pip install edge-tts
   ```
2. 或设置ELEVENLABS_API_KEY

### Q: 图片生成失败？

**解决方案：**
- 设置 `HUGGINGFACE_API_KEY`
- 或使用本地Stable Diffusion (需要GPU)

---

## 💰 成本对比

| 项目 | 付费版 | 免费版 |
|------|--------|--------|
| **Render** | $25/月 | **$0** |
| **OpenAI GPT-4** | $0.75/视频 | 使用免费替代 |
| **DALL-E 3** | $0.40/视频 | 使用免费替代 |
| **ElevenLabs** | $0.30/分钟 | 使用免费替代 |
| **总成本** | ~$30+/月 | **$0** |

---

## 🎯 免费服务配置

### 最佳免费配置 (推荐)

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
```

这将使用：
- **Llama 2 70B** - 免费文本生成
- **SQLite** - 免费数据库
- **占位符音频** - 需要设置ELEVENLABS_API_KEY或安装edge-tts

### 零配置运行

如果没有API密钥，应用仍可运行，但功能受限：
- ❌ 文本生成 (需要AI API)
- ❌ 语音合成 (需要edge-tts或API密钥)
- ✅ API服务器启动
- ✅ 基础路由工作

---

## 📚 高级配置

### 启用Edge TTS (免费语音)

1. 在构建命令中添加:
   ```bash
   pip install -r requirements-render.txt edge-tts
   ```

2. 或创建自定义requirements文件:
   ```txt
   # requirements-edge-tts.txt
   -r requirements-render.txt
   edge-tts>=6.1.0
   ```

### 使用自定义域名

1. 在Render服务设置中点击 **"Custom Domain"**
2. 添加你的域名
3. 更新DNS记录

### 启用HTTPS

Render自动为所有服务提供HTTPS，无需额外配置。

---

## 🚨 重要提示

### 免费层限制

- **构建时间**: 每次部署最多30分钟
- **磁盘**: 1GB (用于SQLite和临时文件)
- **睡眠**: 15分钟无活动后进入睡眠
- **每月构建次数**: 500次

### 生产环境建议

对于实际使用，建议升级到:
- **Render Starter Plan**: $25/月 (无睡眠)
- **PostgreSQL**: $7/月 (更好的数据库性能)

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/Nawa-AI-lab/auto-creator-ai/issues
- **文档**: 查看 `FREE_VERSION_README.md`
- **Render文档**: https://render.com/docs

---

**🎉 祝您部署愉快！**
