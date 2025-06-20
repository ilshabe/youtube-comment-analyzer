# 🎬 YouTube Comment Analyzer

Advanced YouTube comment analysis tool powered by **Clever AI** with real-time sentiment analysis, keyword extraction, and comprehensive video insights.

## ✨ Features

- 🔍 **Real YouTube Data** - Fetches actual video information and comments
- 🧠 **Clever AI Analysis** - Detailed video and audience feedback analysis
- 📊 **Sentiment Analysis** - Advanced NLP-powered emotion detection
- 🔤 **Keyword Extraction** - TF-IDF based keyword and phrase analysis
- 🌍 **Multi-language Support** - English and Russian language detection
- 📈 **Engagement Metrics** - Comprehensive video statistics
- 🎨 **Beautiful UI** - Modern neon-themed interface

## 🚀 Live Demo

[Visit YouTube Comment Analyzer](https://your-render-url.onrender.com)

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Google YouTube Data API v3** - Real video data
- **Google Gemini AI** - Advanced video analysis
- **TextBlob & NLTK** - Natural language processing
- **scikit-learn** - Machine learning for keyword extraction

### Frontend
- **React** - Modern UI framework
- **Axios** - HTTP client
- **CSS3** - Custom neon-themed styling

## 📋 Usage

1. **Enter YouTube URL** - Paste any YouTube video link
2. **Analyze Comments** - Get sentiment analysis and keywords
3. **Clever AI Insights** - Generate detailed AI-powered analysis
4. **View Results** - Explore comprehensive analytics

## 🔧 Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- YouTube Data API key
- Gemini AI API key

### Setup
```bash
# Clone repository
git clone <your-repo-url>
cd yt-comment-analyzer

# Backend setup
cd backend
pip install -r requirements.txt
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables
Create `.env` files:

**backend/.env:**
```
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
```

## 📊 API Endpoints

- `GET /` - API status and health check
- `GET /analyze?video_id={id}` - Analyze video comments
- `POST /gemini-analysis` - Generate AI analysis
- `GET /test-nlp` - Test NLP modules

## 🎯 Key Features Explained

### Sentiment Analysis
- **Excited** - Positive, enthusiastic comments
- **Neutral** - Balanced, informational comments  
- **Confused** - Questions and unclear feedback
- **Frustrated** - Negative, critical comments

### Keyword Extraction
- **TF-IDF Algorithm** - Statistical importance scoring
- **Multi-language** - English and Russian support
- **Phrase Detection** - Common bigrams and trigrams

### Clever AI Analysis
- **Audience Feedback** - Detailed reaction analysis
- **Technical Issues** - Problem identification
- **Improvement Suggestions** - Actionable recommendations
- **Growth Opportunities** - Content development ideas

## 🔒 Privacy & Security

- No data storage - All analysis is real-time
- API keys secured via environment variables
- CORS configured for secure cross-origin requests

## 📈 Performance

- **Fast Analysis** - Optimized NLP processing
- **API Rotation** - Multiple Gemini keys for reliability
- **Responsive Design** - Works on all devices

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google YouTube Data API
- Google Gemini AI
- TextBlob NLP Library
- React Community

---

**Made with ❤️ for the YouTube creator community**
