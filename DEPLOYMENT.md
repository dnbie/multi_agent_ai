# Agent X - Deployment Guide

## Local Development

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip & npm package managers

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd agentic-ai
   ```

2. **Backend Setup**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your API keys:
     - `GOOGLE_API_KEY` - Required for AI features (Google Gemini)
     - `WEATHER_API_KEY` - OpenWeatherMap API
     - `NEWS_API_KEY` - NewsAPI.org
     - `AVIATION_STACK_API_KEY` - Aviation Stack (flight search)
     - `SECRET_KEY` - JWT secret key
     - `GOOGLE_CLIENT_ID` - Google OAuth client ID

5. **Run the application**
   ```bash
   # Terminal 1 - Backend
   python app.py

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

6. **Access the app**
   - Frontend: http://localhost:3002
   - API: http://localhost:5000

---

## Vercel Deployment

### Prerequisites
- [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/docs/cli) (optional but recommended)
- Git repository (GitHub, GitLab, or Bitbucket)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/agent-x.git
git push -u origin main
```

### Step 2: Import Project on Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select your GitHub repo
4. Vercel will auto-detect `vercel.json` configuration
5. **Before deploying**, add Environment Variables (see Step 3)
6. Click **Deploy**

### Step 3: Configure Environment Variables

In the Vercel project dashboard → **Settings** → **Environment Variables**, add:

| Variable | Value | Required |
|----------|-------|----------|
| `GOOGLE_API_KEY` | Your Google Gemini API key | Yes |
| `SECRET_KEY` | A strong random secret for JWT | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Yes |
| `WEATHER_API_KEY` | OpenWeatherMap API key | Optional |
| `NEWS_API_KEY` | NewsAPI.org key | Optional |
| `AVIATION_STACK_API_KEY` | Aviation Stack key | Optional |
| `RAZORPAY_KEY_ID` | Razorpay key ID | Optional |
| `RAZORPAY_KEY_SECRET` | Razorpay key secret | Optional |

### Step 4: Update Google OAuth

After deployment, update your Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client ID
3. Add your Vercel URL to **Authorized JavaScript origins**:
   - `https://your-app.vercel.app`
4. Add to **Authorized redirect URIs**:
   - `https://your-app.vercel.app`

### Step 5: Deploy via CLI (Alternative)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy (from project root)
vercel

# Deploy to production
vercel --prod
```

### Step 6: Verify Deployment

- Visit `https://your-app.vercel.app` - should show the login page
- Visit `https://your-app.vercel.app/api/health` - should return `{"status": "healthy"}`

---

## Vercel Project Structure

```
vercel.json          → Build & routing configuration
api.py               → Python serverless function (Flask API)
frontend/            → React app (static build)
requirements.txt     → Python dependencies (auto-installed)
```

**How it works:**
- `/api/*` requests → routed to `api.py` (Python serverless function)
- All other requests → served from React static build
- React Router paths → fallback to `index.html`

---

## Known Limitations (Vercel Serverless)

1. **Database**: SQLite is ephemeral on serverless. Data resets on cold starts. For production, use a hosted database (e.g., Vercel Postgres, PlanetScale).
2. **File operations**: File Organizer agent won't work (no persistent filesystem).
3. **Cold starts**: First request after idle may take 2-5 seconds.
4. **Package size**: Must stay under 250MB uncompressed.

---

## API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| Google Gemini | AI/LLM features | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| OpenWeatherMap | Weather data | [openweathermap.org](https://openweathermap.org/api) |
| NewsAPI | News headlines | [newsapi.org](https://newsapi.org) |
| Aviation Stack | Flight search | [aviationstack.com](https://aviationstack.com) |
| Razorpay | Payments | [razorpay.com](https://dashboard.razorpay.com) |
| Google OAuth | Login | [console.cloud.google.com](https://console.cloud.google.com/apis/credentials) |

---

## Troubleshooting

### Common Issues

1. **"API key not found"**
   - Check Environment Variables in Vercel dashboard
   - Redeploy after adding variables

2. **"Module not found"**
   - Check `requirements.txt` has the dependency
   - Vercel auto-installs from `requirements.txt`

3. **Build fails with warnings**
   - Build script uses `CI=false` to prevent warnings from failing the build

4. **CORS errors**
   - The API auto-allows the Vercel deployment URL via `VERCEL_URL` env var
   - For custom domains, set `FRONTEND_URL` env var

5. **Google OAuth not working**
   - Add your Vercel URL to Google Cloud Console authorized origins
   - Set `GOOGLE_CLIENT_ID` in Vercel env vars

6. **502/504 errors on API**
   - Check Vercel function logs in dashboard
   - May be a cold start timeout — retry the request

---

## Support

For issues or questions, create an issue on GitHub.

**Agent X v1.0** - BSc Final Year Project
