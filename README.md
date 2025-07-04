#  YouTube Comment Analyzer

> AI-powered YouTube comment analyzer with advanced sentiment analysis and keyword extraction

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-purple.svg)](https://youtube-comment-analyzer-z35t.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)

![YouTube Comment Analyzer Demo](screenshot.png)

##  Features

- ** Real YouTube Data** - Fetches actual video information and comments via YouTube Data API v3
- ** AI-Powered Analysis** - Advanced video and audience feedback analysis using Google Gemini 2.5 Flash
- ** Sentiment Analysis** - Detects emotions: excited, neutral, confused, frustrated
- ** Keyword Extraction** - TF-IDF based keyword and phrase analysis
- ** Multi-language Support** - English and Russian language detection
- ** Engagement Metrics** - Comprehensive video statistics
- ** Popular Comments** - Identifies most liked and relevant comments
- ** Beautiful UI** - Modern neon-themed interface

##  Live Demo

**Try it now:** [https://youtube-comment-analyzer-z35t.onrender.com/](https://youtube-comment-analyzer-z35t.onrender.com/)

##  Local Development

### Prerequisites
- Python 3.11+
- Node.js 16+
- YouTube Data API key
- Gemini AI API key

### Setup
\\\ash
# Clone repository
git clone https://github.com/ilshabe/youtube-comment-analyzer.git
cd youtube-comment-analyzer

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env.local
# Add your API keys to .env.local
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
\\\

##  Deployment on Render

### Build Settings
\\\
Root Directory: (empty)
Build Command: cd frontend && npm install -g vite && npm run build && cd ../backend && pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
Start Command: cd backend && python main.py
Health Check Path: /health
\\\

### Environment Variables
\\\
YOUTUBE_API_KEY = your_youtube_api_key
GEMINI_API_KEY = your_gemini_api_key
GEMINI_API_KEYS = key1,key2,key3,key4,key5
\\\

##  API Endpoints

- \GET /analyze?video_id={id}\ - Analyze video comments
- \POST /gemini-analysis\ - AI-powered analysis
- \GET /health\ - Health check
- \GET /docs\ - API documentation

##  Getting API Keys

### YouTube Data API v3
1. [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create API key

### Gemini AI API
1. [Google AI Studio](https://aistudio.google.com/)
2. Create API key
3. For reliability, create multiple keys

---

**Made with  for YouTube content creators**

 **Star this repo if it helped you!**
