# Agent X - Deployment Guide

## Local Development

### Prerequisites
- Python 3.9+
- pip package manager

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd agentic-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your API keys:
     - `GOOGLE_API_KEY` - Required for AI features (Google Gemini)
     - `WEATHER_API_KEY` - OpenWeatherMap API
     - `NEWS_API_KEY` - NewsAPI.org
     - `AVIATION_STACK_API_KEY` - Aviation Stack (flight search)

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the app**
   - Open http://localhost:8501 in your browser
   - Login with default credentials:
     - Username: `admin` | Password: `admin123`
     - Username: `user` | Password: `user123`

---

## Streamlit Cloud Deployment

### Step 1: Push to GitHub
Create a new GitHub repository and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/agent-x.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Secrets
In Streamlit Cloud dashboard:
1. Go to your app settings
2. Click "Secrets"
3. Add your API keys:
```toml
GOOGLE_API_KEY = "your-key"
WEATHER_API_KEY = "your-key"
NEWS_API_KEY = "your-key"
AVIATION_STACK_API_KEY = "your-key"
```

---

## Docker Deployment (Optional)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run
```bash
docker build -t agent-x .
docker run -p 8501:8501 --env-file .env agent-x
```

---

## API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| Google Gemini | AI/LLM features | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| OpenWeatherMap | Weather data | [openweathermap.org](https://openweathermap.org/api) |
| NewsAPI | News headlines | [newsapi.org](https://newsapi.org) |
| Aviation Stack | Flight search | [aviationstack.com](https://aviationstack.com) |

---

## Troubleshooting

### Common Issues

1. **"API key not found"**
   - Check your `.env` file exists with correct keys
   - For Streamlit Cloud, add keys in Secrets section

2. **"Module not found"**
   - Run `pip install -r requirements.txt`

3. **"Database error"**
   - Delete `database/users.db` to reset
   - App will recreate it on startup

4. **"Port already in use"**
   - Kill existing Streamlit process
   - Or use different port: `streamlit run app.py --server.port 8502`

---

## Support

For issues or questions, create an issue on GitHub.

**Agent X v1.0** - BSc Final Year Project
