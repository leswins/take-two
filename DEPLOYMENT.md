# Deployment Guide: Sports Commentary Analyzer

This guide covers deploying the application using:
- **Frontend**: Vercel
- **Backend**: Railway or Render
- **Database**: Supabase PostgreSQL
- **Cache**: Upstash Redis

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Vercel      │────▶│  Railway/Render │────▶│    Supabase     │
│   (Frontend)    │     │    (Backend)    │     │  (PostgreSQL)   │
│   React/Vite    │     │    FastAPI      │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │     Upstash     │
                        │     (Redis)     │
                        └─────────────────┘
```

## Step 1: Set Up Supabase Database

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com) and create a new project
   - Note your project's region (choose closest to your users)

2. **Get Connection String**
   - Go to Settings → Database → Connection string
   - Copy the "Transaction" pooler connection string (recommended for serverless)
   - Format: `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

3. **Note**: Database tables will be created automatically by Alembic migrations on first deploy

## Step 2: Set Up Upstash Redis

1. **Create Upstash Account**
   - Go to [upstash.com](https://upstash.com) and create an account
   - Create a new Redis database

2. **Get Connection String**
   - Copy the Redis URL from the dashboard
   - Format: `rediss://default:[password]@[endpoint]:6379`

3. **Free Tier**: Upstash offers a generous free tier (10,000 commands/day)

## Step 3: Deploy Backend to Railway

### Option A: Railway (Recommended)

1. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select the repository and `backend` as the root directory

2. **Configure Environment Variables**
   In Railway dashboard, add these variables:
   ```
   DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   REDIS_URL=rediss://default:[password]@[endpoint]:6379
   CORS_ORIGINS=https://your-app.vercel.app
   DEBUG=false
   ```

3. **Deploy**
   - Railway will auto-detect Python and use the `Procfile`
   - First deploy runs migrations automatically

4. **Note Your Backend URL**
   - Railway provides a URL like `your-app.railway.app`
   - You'll need this for the frontend configuration

### Option B: Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository

2. **Create Web Service**
   - Select "Web Service"
   - Connect to your repo
   - Set root directory to `backend`
   - Environment: Python 3
   - Build command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - Start command: `python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Configure Environment Variables**
   Same as Railway above.

## Step 4: Deploy Frontend to Vercel

1. **Create Vercel Project**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Framework preset: Vite
   - Root directory: `frontend`

2. **Configure Environment Variables**
   In Vercel dashboard, add:
   ```
   VITE_API_URL=https://your-backend.railway.app  (or render.com URL)
   ```

3. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically

4. **Update CORS**
   - After getting your Vercel URL (e.g., `your-app.vercel.app`)
   - Update `CORS_ORIGINS` in your backend environment to include it

## Environment Variables Reference

### Backend (Railway/Render)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Supabase PostgreSQL connection string | `postgresql://postgres.[ref]:[pw]@...` |
| `REDIS_URL` | Yes | Upstash Redis connection string | `rediss://default:[pw]@...` |
| `CORS_ORIGINS` | Yes | Allowed frontend origins (comma-separated) | `https://your-app.vercel.app` |
| `DEBUG` | No | Enable debug mode (default: false) | `false` |
| `HUGGINGFACE_TOKEN` | No | HuggingFace API token for private models | `hf_xxxxx` |
| `SENTRY_DSN` | No | Sentry error tracking DSN | `https://xxx@sentry.io/xxx` |

### Frontend (Vercel)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | Yes | Backend API URL | `https://your-api.railway.app` |

## Post-Deployment Checklist

- [ ] Verify frontend loads at your Vercel URL
- [ ] Check `/health` endpoint on backend returns `healthy`
- [ ] Test file upload and analysis flow
- [ ] Verify CORS is working (no cross-origin errors in browser console)
- [ ] Test database connectivity by creating a transcript
- [ ] Monitor first cold start (ML models take ~30-60s to load initially)

## Troubleshooting

### "CORS error" in browser console
- Ensure `CORS_ORIGINS` includes your exact Vercel URL (with https://)
- Include trailing variations if needed: `https://app.vercel.app,https://www.app.vercel.app`

### "Database connection failed"
- Verify Supabase connection string is correct
- Ensure you're using the "Transaction" pooler URL, not direct connection
- Check that your IP isn't blocked (Supabase dashboard → Settings → Database)

### "Analysis timeout"
- First analysis after deploy takes longer (model loading)
- Consider increasing timeout settings in Railway/Render
- For large transcripts, analysis can take 30-60 seconds

### "Redis connection failed"
- Redis is optional - the app works without it
- Verify Upstash URL uses `rediss://` (with 's' for TLS)
- Check Upstash dashboard for connection limits

## Cost Estimates

| Service | Free Tier | Paid Starting At |
|---------|-----------|------------------|
| Vercel | Generous (hobby) | $20/mo (Pro) |
| Railway | $5 free credit/mo | $0.000463/vCPU-min |
| Render | Free (with limits) | $7/mo (Starter) |
| Supabase | 500MB database | $25/mo (Pro) |
| Upstash | 10k commands/day | $0.2/100k commands |

**Estimated monthly cost for light usage**: $7-15/month (Render Starter + free tiers)

## Local Development

To run locally with cloud services:

1. Copy environment files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. Fill in your cloud credentials in `.env` files

3. Start services:
   ```bash
   # Terminal 1 - Backend
   cd backend
   pip install -r requirements.txt
   python -m alembic upgrade head
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm install
   npm run dev
   ```

## Security Notes

- Never commit `.env` files to git
- Use environment variables for all secrets
- Enable Supabase Row Level Security for additional protection
- Consider enabling Vercel password protection for staging environments
