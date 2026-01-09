# 🎬 AutoCreator AI - Render Minimal Deployment Guide

**100% Pure Python - No Rust, No Compilation!**

---

## 📋 Problem

```
ERROR: Failed building wheel for pydantic-core
ERROR: Failed building wheel for asyncpg
```

**Reason:** Render doesn't support Rust compilation on free tier.

**Solution:** Use this minimal version with pure Python only!

---

## 🚀 Quick Deploy to Render

### Step 1: Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub: `Nawa-AI-lab/auto-creator-ai`

### Step 2: Configure Service

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements-render-minimal.txt` |
| **Start Command** | `uvicorn backend.app.main_minimal:app --host 0.0.0.0 --port $PORT` |
| **Python Version** | `3.11` ✅ (NOT 3.13!) |
| **Plan** | `Free` |
| **Disk** | `1 GB` |

### Step 3: Environment Variables

Add these in Render settings (optional):

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
```

### Step 4: Deploy

Click **"Create Web Service"** and wait ~2 minutes!

---

## 📦 What's Included (Pure Python Only)

### Backend Dependencies:
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.109.2 | Web framework |
| `uvicorn` | 0.27.1 | ASGI server |
| `httpx` | 0.26.0 | HTTP client |
| `aiofiles` | 23.2.1 | Async files |
| `aiosqlite` | 0.19.0 | Database |
| `redis` | 5.0.1 | Cache/Queue |
| `celery` | 5.3.6 | Background tasks |
| `aiohttp` | 3.9.3 | Async HTTP |

### ❌ Removed (Require Rust/Compilation):
- `pydantic` (use simple dicts)
- `asyncpg` (use aiosqlite)
- `sqlalchemy` (use sqlite directly)
- `torch`, `transformers`, `diffusers` (GPU only)
- `TTS`, `edge-tts` (require compilation)

---

## 🎯 Features

### ✅ Working:
- REST API endpoints
- SQLite database
- Project CRUD operations
- Health checks
- CORS support

### ⏳ Limited (Need API Keys):
- AI Text Generation (requires Groq/HuggingFace API key)
- Image Generation (requires API key)
- Voice Synthesis (requires API key)

---

## 📊 Cost Comparison

| Version | Monthly Cost | Features |
|---------|-------------|----------|
| **Full (OpenAI)** | ~$30+/month | All features |
| **Free (Render)** | **$0** | API + Database only |

---

## 🔧 Post-Deployment

### 1. Test API
```bash
curl https://your-service.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "sqlite",
  "python_version": "3.11+"
}
```

### 2. Create Project
```bash
curl -X POST https://your-service.onrender.com/api/projects \
  -H "Content-Type: application/json" \
  -d '{"topic": "测试视频", "language": "zh"}'
```

### 3. View API Docs
Open: `https://your-service.onrender.com/api/docs`

---

## 🚨 Troubleshooting

### "Python 3.13 not supported"

**Fix:** Set Python Version to `3.11` in Render settings.

### "Database locked"

**Fix:** Enable Disk (1GB) in Render settings for SQLite.

### "Module not found"

**Fix:** Ensure you're using `requirements-render-minimal.txt`

### "Import error"

**Fix:** This minimal version doesn't use pydantic or sqlalchemy. Use simple dicts instead.

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/projects` | List projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/{id}` | Get project |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |
| POST | `/api/projects/{id}/generate` | Start generation |

---

## 💡 Next Steps

### Upgrade to Full Version

For production, upgrade to paid plan:

1. **Render Starter**: $25/month (no sleep)
2. **PostgreSQL**: $7/month (better database)
3. **Add API Keys** for full AI features

### Add AI Features

Set these environment variables:
```env
AI_PROVIDER=groq           # or "huggingface" or "gemini"
GROQ_API_KEY=your_key      # Get free key: https://console.groq.com
HUGGINGFACE_API_KEY=your_key
GEMINI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key  # For voice
```

---

## 📚 Resources

- **Render Docs**: https://render.com/docs
- **Groq API**: https://console.groq.com
- **GitHub**: https://github.com/Nawa-AI-lab/auto-creator-ai

---

**🎉 Zero-cost deployment achieved!**
