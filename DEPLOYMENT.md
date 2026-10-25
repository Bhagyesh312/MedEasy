# 🚀 Deployment Guide - MedEasy AI 2.0

## ⚠️ Memory Optimization for Render Free Tier

Render free tier has a **512MB RAM limit**. The original `requirements.txt` included heavy ML libraries (torch, transformers, sentence-transformers, faiss-cpu) that consume 300-400MB+, causing **Out of Memory** errors.

## ✅ Solution: Lightweight Production Build

We've created two requirement files:

### 1. **Production (Render)** — `requirements.txt`
- ✅ Core Flask dependencies only
- ✅ Groq API for all AI features (no local models)
- ✅ Minimal dependencies (~150MB total)
- ✅ Works on Render free tier (512MB)
- ❌ RAG/Vector store disabled (not needed, Groq handles everything)

### 2. **Full Local Development** — `requirements-full.txt`
- ✅ All production dependencies
- ✅ ML libraries for RAG/embeddings (torch, transformers, faiss-cpu)
- ✅ Full feature set with vector search
- ⚠️ Requires 2GB+ RAM
- 🖥️ For local development only

---

## 📦 Deployment Steps (Render)

### Step 1: Configure Render Web Service

1. Go to [render.com](https://render.com) → Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `https://github.com/Bhagyesh312/MedEasy`

### Step 2: Build Settings

```yaml
Name: medeasy
Region: Singapore (or closest to your users)
Branch: main
Root Directory: backend
Runtime: Python 3.11

Build Command: pip install --no-cache-dir -r requirements.txt

Start Command: gunicorn app:app --timeout 300 --workers 1 --worker-class sync --max-requests 1000 --max-requests-jitter 50 --preload

Instance Type: Free
```

### Step 3: Environment Variables

Add these in Render dashboard → Environment:

```env
# ── Groq AI API ────────────────────────────────────────────────
GROQ_API_KEY=gsk_your_actual_key_here

# ── Database (Neon PostgreSQL) ─────────────────────────────────
DB_HOST=your-neon-host.neon.tech
DB_PORT=5432
DB_NAME=medical_report_db
DB_USER=your_neon_user
DB_PASSWORD=your_neon_password

# ── JWT Secret (Generate new for production) ───────────────────
JWT_SECRET_KEY=generate_with_python_secrets_token_hex_32

# ── Flask Environment ──────────────────────────────────────────
FLASK_ENV=production

# ── Email Service (Gmail SMTP) ─────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_FROM=MedEasy <your-email@gmail.com>

# ── Optional: USDA API ─────────────────────────────────────────
USDA_API_KEY=your_usda_key_if_you_have_one
```

**Generate JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Deploy

- Click "Create Web Service"
- Render will clone repo, install dependencies, and start the service
- First deploy takes 3-5 minutes
- Watch logs for errors

### Step 5: Database Setup (Neon)

1. Go to [neon.tech](https://neon.tech) → Create account
2. Create new project → Choose region (same as Render)
3. Copy connection string
4. Connect via pgAdmin or Neon SQL Editor
5. Run SQL migrations **in order**:

```sql
-- Run these one by one in Neon SQL Editor
database/01_create_tables.sql
database/03_add_users.sql
database/04_add_otp.sql
database/05_add_finding_details.sql
database/06_add_conversations.sql
```

6. Update Render environment variables with Neon connection details

---

## 🔍 Troubleshooting

### ❌ Out of Memory Error (512MB limit)

**Symptoms:**
```
==> Out of memory (used over 512MB)
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
```

**Solutions:**

1. ✅ **Use correct requirements.txt** (already fixed)
   - Ensure using `requirements.txt` (not `requirements-full.txt`)
   - Check Build Command: `pip install --no-cache-dir -r requirements.txt`

2. ✅ **Optimize Procfile** (already fixed)
   - `--workers 1` (single worker saves memory)
   - `--preload` (loads app once)
   - `--max-requests 1000` (restarts worker periodically)

3. ✅ **Disable RAG in production**
   - Vector store auto-disabled when faiss-cpu not installed
   - All AI features work via Groq API

4. ⚠️ **If still failing:**
   - Upgrade to Render Starter plan ($7/month) with 512MB+ RAM
   - OR deploy to Railway.app (free tier has 8GB RAM)

### ❌ Module Not Found Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'faiss'
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solution:**
- ✅ This is EXPECTED in production (memory optimization)
- ✅ Code gracefully degrades without these libraries
- ✅ All features work via Groq API
- ❌ DO NOT add these to requirements.txt (causes OOM)

### ❌ Database Connection Refused

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solutions:**
1. Check Neon database is running
2. Verify `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` in Render
3. Ensure Neon allows connections (check IP whitelist)
4. Test connection string locally:
   ```bash
   psql "postgresql://user:pass@host/db?sslmode=require"
   ```

### ❌ Groq API Errors

**Symptoms:**
```
groq.APIError: Rate limit exceeded
groq.AuthenticationError: Invalid API key
```

**Solutions:**
1. Verify `GROQ_API_KEY` in Render environment variables
2. Check API key at [console.groq.com](https://console.groq.com)
3. Free tier limits: 30 requests/minute, 14,400/day
4. Upgrade to Groq Pro if needed

### ❌ Frontend Not Showing

**Symptoms:**
- API works (`/api/health` returns 200)
- Frontend shows 404

**Solutions:**
1. Build frontend locally:
   ```bash
   cd frontend
   npm run build
   ```
2. Commit `frontend/dist/` folder
3. Push to GitHub
4. Render will serve static files from `frontend/dist/`

---

## 🔄 Updating Deployment

### Push Changes

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render auto-deploys on every push to `main` branch.

### Manual Redeploy

1. Go to Render dashboard
2. Click your service → "Manual Deploy" → "Deploy latest commit"

### View Logs

1. Render dashboard → Your service → "Logs"
2. Real-time logs show startup, requests, errors

---

## 📊 Performance Tips

### 1. Enable Caching (Redis - Optional)

Add Redis addon in Render:
```bash
# Render dashboard → Add Redis instance
# Update app.py to use Redis for rate limiter
```

### 2. Connection Pooling

Already enabled via `psycopg2-binary`. Neon handles connection pooling automatically.

### 3. CDN for Static Files

For better performance, upload `frontend/dist/` to Cloudflare Pages or Netlify:
- Faster loading (CDN edge locations)
- Reduced load on Flask server

---

## 🌍 Alternative Deployment Platforms

### Railway.app (Recommended for free tier)

**Pros:**
- 8GB RAM on free tier (vs 512MB on Render)
- No OOM issues with full `requirements-full.txt`
- PostgreSQL included
- Auto-deploys from GitHub

**Steps:**
1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Select your repo
4. Add PostgreSQL service
5. Set environment variables
6. Deploy

### Heroku

**Pros:**
- 512MB RAM on free tier (Eco Dynos $5/month)
- PostgreSQL addon available
- Easy setup

**Steps:**
```bash
heroku login
heroku create medeasy
heroku addons:create heroku-postgresql:mini
heroku config:set GROQ_API_KEY=gsk_...
# ... (set all env vars)
git push heroku main
```

### Vercel (Frontend Only)

Deploy frontend separately:
1. Build: `cd frontend && npm run build`
2. Deploy `dist/` folder to Vercel
3. Backend stays on Render/Railway
4. Update `VITE_API_URL` to point to backend

---

## 📈 Monitoring

### Health Check Endpoint

```bash
curl https://your-app.onrender.com/api/health
# Should return: {"status": "healthy"}
```

### Database Connection

```bash
curl https://your-app.onrender.com/api/auth/me
# Should return 401 (auth working) or 500 (DB issue)
```

### Memory Usage

Check Render dashboard → Metrics tab:
- RAM usage should stay under 400MB
- CPU should be <50% average

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] ✅ Use `requirements.txt` (not `requirements-full.txt`)
- [ ] ✅ Build frontend: `cd frontend && npm run build`
- [ ] ✅ Commit `frontend/dist/` folder
- [ ] ✅ Set `FLASK_ENV=production` in Render
- [ ] ✅ Generate new `JWT_SECRET_KEY` for production
- [ ] ✅ Set up Neon PostgreSQL database
- [ ] ✅ Run all SQL migrations in order
- [ ] ✅ Add all environment variables in Render
- [ ] ✅ Test Groq API key
- [ ] ✅ Test Gmail SMTP credentials
- [ ] ✅ Enable HTTPS (Render does this automatically)
- [ ] ✅ Test registration flow (OTP email)
- [ ] ✅ Test upload and analysis
- [ ] ✅ Test all generators (diet, exercise, education)
- [ ] ✅ Test chat functionality
- [ ] ✅ Test PDF export
- [ ] ✅ Test report comparison
- [ ] ✅ Check error logs for issues

---

## 🆘 Support

If deployment fails:

1. Check Render logs for specific error
2. Search error message in this guide
3. Check GitHub Issues: https://github.com/Bhagyesh312/MedEasy/issues
4. Create new issue with:
   - Error message
   - Render logs
   - Steps to reproduce

---

## 📝 Summary

| Feature | Production (Render) | Local Development |
|---------|---------------------|-------------------|
| **Requirements** | `requirements.txt` | `requirements-full.txt` |
| **Memory Usage** | ~150MB | ~2GB |
| **ML Libraries** | ❌ Disabled | ✅ Enabled |
| **Vector Store** | ❌ Disabled | ✅ Enabled |
| **RAG System** | ❌ Disabled | ✅ Enabled |
| **AI Features** | ✅ Via Groq API | ✅ Via Groq API + Local |
| **Analysis** | ✅ Works | ✅ Works |
| **Chat** | ✅ Works | ✅ Works |
| **Generators** | ✅ Works | ✅ Works |
| **PDF Export** | ✅ Works | ✅ Works |

**All features work in production** — just using Groq API instead of local ML models.
