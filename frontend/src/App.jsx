import React, { useState } from 'react'
import axios from 'axios'
import './App.css'
import WordCloud from './components/WordCloud'
import ProfileCard from './components/ProfileCard'

export default function App() {
  const [videoUrl, setVideoUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [geminiAnalysis, setGeminiAnalysis] = useState(null)
  const [geminiLoading, setGeminiLoading] = useState(false)

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

  const formatDuration = (duration) => {
    if (!duration) return 'N/A'
    // Парсим ISO 8601 duration (PT10M30S -> 10:30)
    const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/)
    if (!match) return duration
    
    const hours = parseInt(match[1] || 0)
    const minutes = parseInt(match[2] || 0)
    const seconds = parseInt(match[3] || 0)
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    } catch {
      return 'N/A'
    }
  }

  const cleanCommentText = (text) => {
    if (!text) return ''
    
    return text
      // Убираем все виды ссылок
      .replace(/https?:\/\/[^\s<>"']+/gi, '[ссылка]')
      .replace(/www\.[^\s<>"']+/gi, '[ссылка]')
      .replace(/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\/[^\s<>"']*/gi, '[ссылка]')
      .replace(/bit\.ly\/[^\s<>"']*/gi, '[ссылка]')
      .replace(/youtu\.be\/[^\s<>"']*/gi, '[ссылка]')
      // Убираем HTML теги и атрибуты
      .replace(/<[^>]*>/g, '')
      .replace(/&[a-zA-Z0-9#]+;/g, '')
      .replace(/href="[^"]*"/gi, '')
      // Очищаем лишние пробелы
      .replace(/\s+/g, ' ')
      .trim()
  }

  const handleAnalyze = async () => {
    const videoId = getVideoId(videoUrl)
    if (!videoId) {
      showNotification('Error: Please enter a valid YouTube video URL', 'error')
      return
    }

    setLoading(true)
    setGeminiAnalysis(null) // Сбрасываем предыдущий анализ Gemini
    try {
      console.log('Analyzing video ID:', videoId);
      const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
      const res = await axios.get(`${apiUrl}/analyze?video_id=${videoId}`)
      console.log('API Response:', res.data);
      if (res.data.success) {
        console.log('Channel avatar URL:', res.data.video_info.channel_avatar);
        setResult(res.data)
        showNotification('Analysis completed successfully!', 'success')
      } else {
        throw new Error('Analysis failed')
      }
    } catch (e) {
      console.error('Full error object:', e);
      console.error('Error response:', e.response);
      console.error('Error message:', e.message);
      
      if (e.response?.status === 404) {
        showNotification('Video not found or unavailable', 'error')
      } else if (e.response?.status === 400) {
        showNotification('Invalid YouTube video URL', 'error')
      } else if (e.response?.status === 500) {
        showNotification(`Server error: ${e.response?.data?.detail || 'Unknown error'}`, 'error')
      } else if (e.code === 'ECONNREFUSED') {
        showNotification('Cannot connect to server. Please make sure the backend is running.', 'error')
      } else {
        showNotification(`Error: ${e.message || 'Unknown error occurred'}`, 'error')
      }
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handleGeminiAnalysis = async () => {
    const videoId = getVideoId(videoUrl)
    if (!videoId) {
      showNotification('Error: Please enter a valid YouTube video URL', 'error')
      return
    }

    setGeminiLoading(true)
    try {
      showNotification('Starting Clever AI analysis... This may take up to 2 minutes.', 'info')
      
      const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
      const res = await axios.post(`${apiUrl}/gemini-analysis`, {
        video_id: videoId
      }, {
        timeout: 120000 // 2 минуты timeout
      })
      
      if (res.data.success) {
        setGeminiAnalysis(res.data)
        showNotification('Clever AI analysis completed!', 'success')
      } else {
        throw new Error('Gemini analysis failed')
      }
    } catch (e) {
      if (e.code === 'ECONNABORTED') {
        showNotification('Analysis timeout. Please try again.', 'error')
      } else if (e.response?.status === 500) {
        showNotification(e.response.data.detail || 'Clever AI analysis error', 'error')
      } else {
        showNotification('Error during Clever AI analysis. Please try again.', 'error')
      }
      console.error('Gemini analysis error:', e)
    } finally {
      setGeminiLoading(false)
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
      ${type === 'error' ? 'background: #ff6b6b;' : type === 'info' ? 'background: #45b7d1;' : 'background: #4ecdc4;'}
    `;
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

  const LanguageDistribution = ({ languages }) => {
    if (!languages || Object.keys(languages).length === 0) return null
    
    return (
      <div className="language-section">
        <h4 className="subsection-title">Language Distribution</h4>
        <div className="language-list">
          {Object.entries(languages).map(([lang, percentage]) => (
            <div key={lang} className="language-item">
              <span className="language-code">{lang.toUpperCase()}</span>
              <div className="language-bar">
                <div 
                  className="language-fill" 
                  style={{ width: `${percentage}%`, backgroundColor: '#45b7d1' }}
                ></div>
              </div>
              <span className="language-percentage">{percentage}%</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const KeywordsList = ({ keywords, title = "Top Keywords" }) => {
    if (!keywords || keywords.length === 0) return null
    
    return (
      <div className="keywords-section">
        <h4 className="subsection-title">{title}</h4>
        <div className="keywords-list">
          {keywords.slice(0, 8).map((keyword, index) => (
            <div key={index} className="keyword-item">
              <span className="keyword-word">{keyword.word}</span>
              <div className="keyword-stats">
                <span className="keyword-frequency">×{keyword.frequency}</span>
                {keyword.relevance && (
                  <span className="keyword-relevance">({keyword.relevance})</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const PhrasesList = ({ phrases }) => {
    if (!phrases || phrases.length === 0) return null
    
    return (
      <div className="phrases-section">
        <h4 className="subsection-title">Common Phrases</h4>
        <div className="phrases-list">
          {phrases.slice(0, 5).map((phrase, index) => (
            <div key={index} className="phrase-item">
              <span className="phrase-text">"{phrase.phrase}"</span>
              <span className="phrase-frequency">×{phrase.frequency}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const VideoTags = ({ tags }) => {
    const [showAllTags, setShowAllTags] = React.useState(false)
    
    if (!tags || tags.length === 0) return null
    
    const videoTagsStyle = {
      margin: '1.5rem 0',
      textAlign: 'center'
    }
    
    const tagsTitleStyle = {
      fontSize: '1.1rem',
      color: 'var(--text-secondary)',
      marginBottom: '1rem',
      fontWeight: '600'
    }
    
    const tagsContainerStyle = {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '0.75rem',
      justifyContent: 'center',
      maxWidth: '100%'
    }
    
    const videoTagStyle = {
      display: 'inline-block',
      padding: '0.4rem 0.8rem',
      background: 'var(--bg-secondary)',
      color: 'var(--text-secondary)',
      borderRadius: '12px',
      fontSize: '0.8rem',
      fontWeight: '500',
      textTransform: 'lowercase',
      letterSpacing: '0.2px',
      transition: 'all 0.3s ease',
      border: '1px solid var(--border-glass)',
      cursor: 'default'
    }
    
    const moreTagsStyle = {
      ...videoTagStyle,
      background: 'var(--bg-glass)',
      color: 'var(--neon-cyan)',
      border: '1px solid var(--border-neon)',
      cursor: 'pointer'
    }
    
    const displayTags = showAllTags ? tags : tags.slice(0, 8)
    
    return (
      <div style={videoTagsStyle}>
        <h4 style={tagsTitleStyle}>Video Tags</h4>
        <div style={tagsContainerStyle}>
          {displayTags.map((tag, index) => (
            <span key={index} style={videoTagStyle}>
              #{tag}
            </span>
          ))}
          {tags.length > 8 && !showAllTags && (
            <span 
              style={moreTagsStyle}
              onClick={() => setShowAllTags(true)}
            >
              +{tags.length - 8} more
            </span>
          )}
          {showAllTags && tags.length > 8 && (
            <span 
              style={moreTagsStyle}
              onClick={() => setShowAllTags(false)}
            >
              show less
            </span>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="container">
        {/* Заголовок */}
        <header className="header">
          <h1 className="title">YouTube Comment Analyzer</h1>
          <p className="subtitle">Advanced NLP-powered analysis with real sentiment detection</p>
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
              <div className="video-info-grid">
                <div className="video-details">
                  <h2 className="video-title">{result.video_info.title}</h2>
                  
                  {/* Метаинформация о видео */}
                  {(result.video_info.published_at || result.video_info.duration) && (
                    <div style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '1.5rem',
                      margin: '1rem 0 1.5rem 0',
                      justifyContent: 'center'
                    }}>
                      {result.video_info.published_at && (
                        <span style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          padding: '0.5rem 1rem',
                          background: 'var(--bg-glass)',
                          border: '1px solid var(--border-glass)',
                          borderRadius: '12px',
                          color: 'var(--text-secondary)',
                          fontSize: '0.95rem',
                          fontWeight: '500',
                          transition: 'all 0.3s ease'
                        }}>
                          📅 Published: {formatDate(result.video_info.published_at)}
                        </span>
                      )}
                      {result.video_info.duration && (
                        <span style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          padding: '0.5rem 1rem',
                          background: 'var(--bg-glass)',
                          border: '1px solid var(--border-glass)',
                          borderRadius: '12px',
                          color: 'var(--text-secondary)',
                          fontSize: '0.95rem',
                          fontWeight: '500',
                          transition: 'all 0.3s ease'
                        }}>
                          ⏱️ Duration: {formatDuration(result.video_info.duration)}
                        </span>
                      )}
                    </div>
                  )}
                  
                  {/* Статистика видео */}
                  <div className="video-stats" style={{justifyContent: 'center', gap: '1.5rem', margin: '1.5rem 0'}}>
                    <div className="stat-item">
                      <span className="stat-value">{formatNumber(result.video_info.views)}</span>
                      <span className="stat-label">views</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{formatNumber(result.video_info.likes)}</span>
                      <span className="stat-label">likes</span>
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

                  {/* Теги видео */}
                  <VideoTags tags={result.video_info.tags} />
                </div>
                <div className="channel-card">
                  <ProfileCard
                    name={result.video_info.channel_title}
                    title="YouTube Channel"
                    handle={result.video_info.channel_title.toLowerCase().replace(/\s+/g, '')}
                    status="Active Creator"
                    contactText="Visit Channel"
                    avatarUrl={result.video_info.channel_avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(result.video_info.channel_title)}&size=400&background=00ffff&color=000000&bold=true`}
                    enableTilt={true}
                    showUserInfo={true}
                    onContactClick={() => {
                      // ИСПРАВЛЕНО: Используем channel_url из API
                      const channelUrl = result.video_info.channel_url || `https://www.youtube.com/channel/${result.video_info.channel_id}`;
                      window.open(channelUrl, '_blank', 'noopener,noreferrer');
                    }}
                  />
                </div>
              </div>
            </section>

            {/* Анализ комментариев */}
            <section className="analysis-section glass-effect">
              <h3 className="section-title">Advanced Comment Analysis</h3>
              
              <div className="analysis-grid">
                {/* Анализ тональности */}
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
                  {result.average_sentiment !== undefined && (
                    <div className="sentiment-average">
                      <span>Average Sentiment: </span>
                      <span className={`sentiment-score ${result.average_sentiment > 0.1 ? 'positive' : result.average_sentiment < -0.1 ? 'negative' : 'neutral'}`}>
                        {result.average_sentiment > 0 ? '+' : ''}{result.average_sentiment.toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Языковое распределение */}
                <LanguageDistribution languages={result.language_distribution} />
              </div>
            </section>

            {/* Ключевые слова и фразы */}
            <section className="keywords-section glass-effect">
              <h3 className="section-title">Keywords & Phrases Analysis</h3>
              
              <div className="keywords-grid">
                {/* Облако слов */}
                <div className="wordcloud-wrapper">
                  <WordCloud keywords={result.keywords} title="Key Words Cloud" />
                </div>
                
                {/* Ключевые слова и фразы в одной колонке */}
                <div 
                  className="keywords-phrases-wrapper"
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '2rem'
                  }}
                >
                  <KeywordsList keywords={result.keywords} />
                  <PhrasesList phrases={result.phrases} />
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
                      <div className="comment-author-section">
                        <img 
                          src={comment.author_avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(comment.author)}&size=80&background=4ecdc4&color=000000&bold=true`}
                          alt={`${comment.author} avatar`}
                          className="comment-avatar"
                          onError={(e) => {
                            e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(comment.author)}&size=80&background=4ecdc4&color=000000&bold=true`;
                          }}
                        />
                        <span className="comment-author">{comment.author}</span>
                      </div>
                      <span className="comment-likes">{comment.likes} likes</span>
                    </div>
                    <p className="comment-text">
                      {cleanCommentText(comment.text)}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* Расширенная статистика */}
            {result.statistics && (
              <section className="statistics-section glass-effect">
                <h3 className="section-title">Detailed Statistics</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-number">{result.statistics.total_comments_analyzed}</span>
                    <span className="stat-description">Comments Analyzed</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-number">{result.statistics.average_comment_length}</span>
                    <span className="stat-description">Avg Comment Length</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-number">{result.statistics.total_likes_on_comments}</span>
                    <span className="stat-description">Total Likes on Comments</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-number">{result.statistics.total_words_analyzed}</span>
                    <span className="stat-description">Unique Words Found</span>
                  </div>
                </div>
              </section>
            )}

            {/* Gemini AI Analysis Section */}
            {result && (
              <section className="gemini-section glass-effect">
                <div className="gemini-header">
                  <h3 className="section-title">🤖 AI-Powered Video Analysis</h3>
                  <p className="gemini-description">
                    Get detailed insights about your video and audience feedback using Clever AI
                  </p>
                </div>
                
                {!geminiAnalysis && !geminiLoading && (
                  <div className="gemini-action">
                    <button
                      onClick={handleGeminiAnalysis}
                      className="gemini-btn"
                      disabled={geminiLoading}
                    >
                      <span className="gemini-btn-icon">✨</span>
                      Analyze with Clever AI
                    </button>
                    <p className="gemini-note">
                      This analysis takes 1-2 minutes and provides detailed insights about video quality, 
                      audience feedback, and improvement recommendations.
                    </p>
                  </div>
                )}

                {geminiLoading && (
                  <div className="gemini-loading">
                    <div className="gemini-spinner"></div>
                    <h4>🧠 Clever AI is analyzing your video...</h4>
                    <p>Analyzing video content and {result.statistics?.total_comments_analyzed || 'multiple'} comments</p>
                    <div className="loading-steps">
                      <div className="step active">📹 Processing video content</div>
                      <div className="step active">💬 Analyzing comments</div>
                      <div className="step active">🔍 Identifying patterns</div>
                      <div className="step">📊 Generating insights</div>
                    </div>
                  </div>
                )}

                {geminiAnalysis && (
                  <div className="gemini-results">
                    <div className="gemini-results-header">
                      <h4>🎯 Clever AI Analysis Results</h4>
                      <div className="analysis-meta">
                        <span>📹 {geminiAnalysis.video_info.title}</span>
                        <span>💬 {geminiAnalysis.video_info.comments_analyzed} comments analyzed</span>
                      </div>
                    </div>
                    <div className="gemini-content">
                      <div 
                        className="gemini-analysis-text"
                        style={{
                          color: 'var(--text-primary)',
                          lineHeight: '1.7',
                          fontSize: '1rem'
                        }}
                        dangerouslySetInnerHTML={{
                          __html: geminiAnalysis.gemini_analysis
                            .replace(/\n/g, '<br>')
                            .replace(/## (.*?)$/gm, '<h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 600; margin: 2rem 0 1rem 0; border-bottom: 1px solid var(--border-glass); padding-bottom: 0.5rem;">$1</h3>')
                            .replace(/### (.*?)$/gm, '<h4 style="color: var(--text-primary); font-size: 1.1rem; font-weight: 500; margin: 1.5rem 0 0.75rem 0;">$1</h4>')
                            .replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>')
                            .replace(/\*(.*?)\*/g, '<em style="color: var(--text-secondary); font-style: italic;">$1</em>')
                        }}
                      />
                    </div>
                  </div>
                )}
              </section>
            )}
          </>
        )}

        {/* Информация о проекте */}
        {!result && !loading && (
          <section className="info-section">
            <h3>Enhanced with Real NLP Analysis</h3>
            <div className="features-list">
              <div className="feature-item">
                <span className="feature-icon">🧠</span>
                <span>Real sentiment analysis using TextBlob & custom algorithms</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🔍</span>
                <span>Advanced keyword extraction with TF-IDF scoring</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🌍</span>
                <span>Multi-language support (English & Russian)</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <span>Comprehensive statistics and visualizations</span>
              </div>
            </div>
            <p>
              Paste a YouTube video link and get detailed NLP-powered comment analysis
            </p>
          </section>
        )}
      </div>
    </div>
  )
}


