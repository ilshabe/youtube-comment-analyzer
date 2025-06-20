import React from 'react'

const WordCloud = ({ keywords, title = "Key Words" }) => {
  if (!keywords || keywords.length === 0) {
    return (
      <div className="wordcloud-container">
        <h4 className="wordcloud-title">{title}</h4>
        <p className="no-data">No keywords available</p>
      </div>
    )
  }

  // Создаем простое облако слов без внешних библиотек
  const maxScore = Math.max(...keywords.map(k => k.score || k.frequency || 1))
  
  const getWordSize = (score) => {
    const normalizedScore = (score / maxScore) * 100
    return Math.max(12, Math.min(32, 12 + normalizedScore / 5))
  }

  const getWordColor = (index) => {
    const colors = [
      '#00ffff', '#bf00ff', '#ff0080', '#0080ff', 
      '#00ff80', '#ff8000', '#8000ff', '#00ff40',
      '#ff4080', '#4080ff', '#80ff00', '#ff0040'
    ]
    return colors[index % colors.length]
  }

  return (
    <div className="wordcloud-container">
      <h4 className="wordcloud-title">{title}</h4>
      <div className="wordcloud-words">
        {keywords.map((keyword, index) => (
          <span
            key={index}
            className="wordcloud-word"
            style={{
              fontSize: getWordSize(keyword.score || keyword.frequency || 1) + 'px',
              color: getWordColor(index),
              margin: '4px 8px',
              display: 'inline-block',
              fontWeight: keyword.score > maxScore * 0.7 ? 'bold' : 'normal',
              opacity: 0.8 + (keyword.score || keyword.frequency || 1) / maxScore * 0.2
            }}
            title={`Frequency: ${keyword.frequency || '-'}${keyword.relevance ? ', Relevance: ' + keyword.relevance : ''}` }
          >
            {keyword.word}
          </span>
        ))}
      </div>
    </div>
  )
}

export default WordCloud
