# AutoCreator AI - Render Deployment Configuration
# =============================================

## Quick Deploy to Render:

1. Go to: https://dashboard.render.com/blueprint

2. Connect your GitHub repository:
   - Repository: Nawa-AI-lab/auto-creator-ai
   - Branch: main

3. Review the Blueprint and click "Apply"

4. Add your environment variables:
   - OPENAI_API_KEY: sk-...
   - ELEVENLABS_API_KEY: ...
   - YOUTUBE_CLIENT_ID: ...
   - YOUTUBE_CLIENT_SECRET: ...
   - YOUTUBE_REFRESH_TOKEN: ...

5. Wait for deployment to complete

## Services Created:

- autocreator-backend: Main API server (FastAPI)
- autocreator-worker: Background task worker (Celery)
- autocreator-db: PostgreSQL database
- autocreator-redis: Redis for task queue
- autocreator-frontend: Next.js frontend (optional)

## After Deployment:

- API Docs: https://your-backend-url/api/docs
- Health Check: https://your-backend-url/api/health

## Troubleshooting:

If build fails:
- Check that requirements.txt is in root directory
- Verify all API keys are set
- Check Python version is 3.11

If worker fails:
- Check Redis connection
- Verify database is running
