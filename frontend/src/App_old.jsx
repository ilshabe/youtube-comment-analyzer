
import React, { useState } from 'react'
import axios from 'axios'
import './App.css'

export default function App() {
  const [videoUrl, setVideoUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const getVideoId = (url) => {
    const match = url.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/)
    return match ? match[1] : null
  }

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  const handleAnalyze = async () => {
    const videoId = getVideoId(videoUrl)
    if (!videoId) {
      showNotification('Пожалуйста, введите корректный URL YouTube видео', 'error')
      return
    }

    setLoading(true)
    try {
      const res = await axios.get(`http://localhost:8000/analyze?video_id=${videoId}`)
      if (res.data.success) {
        setResult(res.data)
        showNotification('Анализ комментариев завершен!', 'success')
      } else {
        throw new Error('Анализ не удался')
      }
    } catch (e) {
      if (e.response?.status === 404) {
        showNotification('Видео не найдено или недоступно', 'error')
      } else if (e.response?.status === 400) {
        showNotification('Некорректная ссылка на YouTube видео', 'error')
      } else {
        showNotification('Ошибка при анализе комментариев. Проверьте подключение к серверу.', 'error')
      }
      console.error('Analysis error:', e)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const showNotification = (message, type) => {
    const notification = document.createElement('div')
    notification.textContent = message
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      border-radius: 8px;
      color: white;
      font-weight: 500;
      z-index: 1000;
      animation: slideIn 0.3s ease;
      ${type === 'error' ? 'background: #ff6b6b;' : 'background: #4ecdc4;'}
    `
    document.body.appendChild(notification)
    setTimeout(() => {
      notification.remove()
    }, 3000)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleAnalyze()
    }
  }

  const SentimentBar = ({ label, percentage, color }) => (
    <div className="sentiment-item">
      <div className="sentiment-label">
        <span>{label}</span>
        <span className="sentiment-percentage">{percentage}%</span>
      </div>
      <div className="sentiment-bar">
        <div
          className="sentiment-fill"
          style={{
            width: `${percentage}%`,
            backgroundColor: color
          }}
        ></div>
      </div>
    </div>
  )

  return (
    <div className="app">
      <div className="container">
        {/* Заголовок */}
        <header className="header">
          <h1 className="title">YouTube Comment Analyzer</h1>
          <p className="subtitle">Transform audience feedback into your next viral video</p>
        </header>

        {/* Форма ввода */}
        <section className="input-section glass-effect hover-glow">
          <div className="input-group">
            <input
              type="text"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="https://www.youtube.com/watch?v=..."
              className="url-input"
              disabled={loading}
            />
            <button
              onClick={handleAnalyze}
              disabled={loading || !videoUrl.trim()}
              className="analyze-btn"
            >
              {loading && <span className="loading-spinner"></span>}
              {loading ? 'Analyzing...' : 'Analyze Comments'}
            </button>
          </div>
          <p className="example-text">
            Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ
          </p>
        </section>

        {/* Результаты */}
        {result && (
          <>
            {/* Информация о видео */}
            <section className="video-info-section glass-effect">
              <h2 className="video-title">{result.video_info.title}</h2>
              <div className="video-stats">
                <div className="stat-item">
                  <span className="stat-value">{formatNumber(result.video_info.views)}</span>
                  <span className="stat-label">views</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{result.video_info.comments}</span>
                  <span className="stat-label">comments</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{result.video_info.engagement_rate}%</span>
                  <span className="stat-label">engagement</span>
                </div>
              </div>
            </section>

            {/* Анализ комментариев */}
            <section className="analysis-section glass-effect">
              <h3 className="section-title">Comment Analysis Summary</h3>
              
              <div className="analysis-grid">
                {/* Анализ настроений */}
                <div className="sentiment-section">
                  <h4 className="subsection-title">Sentiment Breakdown</h4>
                  <div className="sentiment-list">
                    <SentimentBar
                      label="Excited"
                      percentage={result.sentiment_analysis.excited}
                      color="#4ecdc4"
                    />
                    <SentimentBar
                      label="Neutral"
                      percentage={result.sentiment_analysis.neutral}
                      color="#6c757d"
                    />
                    <SentimentBar
                      label="Confused"
                      percentage={result.sentiment_analysis.confused}
                      color="#ffa726"
                    />
                    <SentimentBar
                      label="Frustrated"
                      percentage={result.sentiment_analysis.frustrated}
                      color="#ff6b6b"
                    />
                  </div>
                </div>

                {/* Топ темы */}
                <div className="themes-section">
                  <h4 className="subsection-title">Top Themes</h4>
                  <div className="themes-list">
                    <div className="theme-item">
                      <span className="theme-count">{result.themes.frequently_asked_questions}</span>
                      <span className="theme-text">frequently asked questions</span>
                    </div>
                    <div className="theme-item">
                      <span className="theme-count">{result.themes.high_priority_pain_points}</span>
                      <span className="theme-text">high-priority pain points</span>
                    </div>
                    <div className="theme-item">
                      <span className="theme-count">{result.themes.content_requests}</span>
                      <span className="theme-text">content requests</span>
                    </div>
                    <div className="theme-item">
                      <span className="theme-count">{result.themes.topics_of_interest}</span>
                      <span className="theme-text">topics of interest</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Популярные комментарии */}
            <section className="comments-section glass-effect">
              <h3 className="section-title">Most Liked Comments</h3>
              <div className="comments-list">
                {result.popular_comments.map((comment, index) => (
                  <div key={index} className="comment-item">
                    <div className="comment-header">
                      <span className="comment-author">{comment.author}</span>
                      <span className="comment-likes">{comment.likes} likes</span>
                    </div>
                    <p className="comment-text">{comment.text}</p>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

        {/* Информация о проекте */}
        {!result && !loading && (
          <section className="info-section">
            <p>💡 Paste a YouTube video link and get detailed comment analysis</p>
            <p>
              Supported formats: youtube.com/watch?v=... and youtu.be/...
            </p>
          </section>
        )}
      </div>
    </div>
  )
}
