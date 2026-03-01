# Deployment Guide

Complete deployment guide for the Government Job Notification System.

## Prerequisites

1. **Supabase Account** - For PostgreSQL database
2. **Railway Account** - For hosting backend + workers
3. **Vercel Account** (optional) - For hosting frontend
4. **Telegram Account** - For bot and scraping
5. **Google Cloud Account** - For Gemini API key

---

## 1. Database Setup (Supabase)

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Save the following credentials:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY` (from Settings → API)
   - `SUPABASE_DATABASE_URL` (from Settings → Database → Connection String → URI)

### Step 2: Run Database Schema
1. Open SQL Editor in Supabase dashboard
2. Copy and paste contents of `backend/db/schema.sql`
3. Execute the SQL

### Step 3: Add Role Field (if upgrading existing database)
1. Run migration: `backend/db/migrations/001_add_user_role.sql`

### Step 4: Create First Admin User
1. Register a user through the frontend or API
2. Run the make_admin script:
   ```bash
   cd backend
   python db/make_admin.py your@email.com
   ```

---

## 2. Backend Deployment (Railway)

### Step 1: Create Redis Service
1. In Railway dashboard, click "New" → "Database" → "Redis"
2. Copy the `REDIS_URL` from the Connect tab

### Step 2: Create Backend Service
1. Click "New" → "Empty Service"
2. Connect your GitHub repository
3. Set root directory: `/backend`
4. Add environment variables:

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_DATABASE_URL=postgresql://...

# Telegram
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token

# Google AI
GOOGLE_API_KEY=your_gemini_api_key

# Redis
REDIS_URL=redis://default:password@host:port

# App
APP_ENV=production
SECRET_KEY=generate_strong_random_secret_key_here

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=72
```

5. Deploy Settings:
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Build Command: (leave empty, Docker will handle it)

### Step 3: Create Celery Worker Service
1. Click "New" → "Empty Service"
2. Connect same GitHub repository
3. Set root directory: `/backend`
4. Use the SAME environment variables as backend
5. Start Command: `celery -A worker.celery_app worker --loglevel=info`

### Step 4: Create Celery Beat Service
1. Click "New" → "Empty Service"
2. Connect same GitHub repository
3. Set root directory: `/backend`
4. Use the SAME environment variables as backend
5. Start Command: `celery -A worker.celery_app beat --loglevel=info`

---

## 3. Telegram Setup

### Step 1: Get Telegram API Credentials (for Telethon)
1. Go to https://my.telegram.org
2. Login and click "API Development Tools"
3. Create an app to get `API_ID` and `API_HASH`

### Step 2: Create Telegram Bot (for delivery)
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Save the `BOT_TOKEN`

### Step 3: Authorize Telethon (One-time setup)
1. SSH into Railway backend service or run locally:
   ```bash
   cd backend
   python -m scraper.auth
   ```
2. Enter your phone number and verification code
3. This creates `telegram_session.session` file (keep this safe!)

### Step 4: Add Telegram Channels to Monitor
1. Login to admin dashboard
2. Add channel usernames (e.g., @upscnotifications)

---

## 4. Frontend Deployment (Vercel)

### Step 1: Create Project
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set root directory: `/frontend`

### Step 2: Configure Build
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`

### Step 3: Environment Variables
```env
VITE_API_URL=https://your-railway-backend.railway.app
```

### Step 4: Deploy
- Click "Deploy"
- Vercel will auto-deploy on every git push

---

## 5. Post-Deployment Steps

### 1. Test the System
- [ ] Register a new user
- [ ] Login successfully
- [ ] Update profile with eligibility info
- [ ] View notifications list
- [ ] Check admin dashboard (if admin)
- [ ] Add a test Telegram channel
- [ ] Wait for scraper to run (15 mins)
- [ ] Verify notifications appear

### 2. Monitor Logs
- Railway → Backend Service → Logs
- Railway → Celery Worker → Logs
- Railway → Celery Beat → Logs

### 3. Check Background Jobs
```bash
# SSH into Railway backend
celery -A worker.celery_app inspect active
celery -A worker.celery_app inspect scheduled
```

---

## 6. Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ | Supabase anon key |
| `SUPABASE_SERVICE_KEY` | ✅ | Supabase service role key |
| `SUPABASE_DATABASE_URL` | ✅ | PostgreSQL connection string |
| `TELEGRAM_API_ID` | ✅ | Telegram API ID from my.telegram.org |
| `TELEGRAM_API_HASH` | ✅ | Telegram API hash |
| `TELEGRAM_BOT_TOKEN` | ✅ | Bot token from @BotFather |
| `GOOGLE_API_KEY` | ✅ | Google Gemini API key |
| `REDIS_URL` | ✅ | Redis connection URL |
| `SECRET_KEY` | ✅ | Random secret for JWT signing |
| `APP_ENV` | ❌ | Environment (development/production) |
| `JWT_ALGORITHM` | ❌ | JWT signing algorithm (default: HS256) |
| `JWT_EXPIRY_HOURS` | ❌ | JWT expiry in hours (default: 72) |

---

## 7. Troubleshooting

### Backend not starting
- Check Railway logs for errors
- Verify all environment variables are set
- Check database connection string

### Scraper not working
- Verify Telethon session file exists
- Check Telegram API credentials
- Ensure channels are added and active

### No notifications appearing
- Check Celery Beat is running
- Verify scraper is scheduled (every 15 mins)
- Check worker logs for errors
- Verify channels have recent posts

### Frontend can't connect to backend
- Check `VITE_API_URL` points to Railway backend
- Verify CORS is configured correctly in `backend/app/main.py`
- Check browser console for errors

---

## 8. Cost Estimation

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Supabase | Free tier | $0 |
| Railway | Hobby ($5 credit) | ~$10-15 |
| Vercel | Hobby | $0 |
| Google Gemini | Free tier | $0 |
| **Total** | | **~$10-15/month** |

---

## 9. Scaling Considerations

### For 10,000+ users:
1. Upgrade Railway to Pro plan
2. Add more Celery workers
3. Enable Redis persistence
4. Set up database replicas
5. Add CDN for frontend (Vercel auto-includes)
6. Consider upgrading to Gemini paid tier
7. Implement rate limiting on API

### For 100,000+ users:
1. Move to dedicated PostgreSQL (AWS RDS/Azure)
2. Use managed Redis (AWS ElastiCache)
3. Multiple Celery workers with auto-scaling
4. Implement caching layer (Redis)
5. Use message queue (RabbitMQ/SQS)
6. Load balancer for API
7. Separate read/write databases

---

## 10. Backup and Recovery

### Database Backups
1. Supabase auto-backs up daily (free tier)
2. For critical data, enable Point-in-Time Recovery (paid)

### Manual Backup
```bash
pg_dump $SUPABASE_DATABASE_URL > backup.sql
```

### Restore
```bash
psql $SUPABASE_DATABASE_URL < backup.sql
```

---

## Support

For issues or questions:
1. Check logs in Railway dashboard
2. Review error messages in browser console
3. Verify all environment variables
4. Check GitHub issues
