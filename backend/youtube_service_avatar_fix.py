"""
Исправленная версия _get_channel_info с улучшенной обработкой аватаров
"""

def _get_channel_info_fixed(self, channel_id: str) -> Optional[Dict]:
    """Получает информацию о канале с улучшенным получением аватара и прямой ссылки"""
    try:
        request = self.youtube.channels().list(
            part="snippet,statistics,brandingSettings",
            id=channel_id
        )
        response = request.execute()
        
        if not response.get('items'):
            return None
        
        channel = response['items'][0]
        snippet = channel['snippet']
        
        # Получаем URL аватарки канала с улучшенной логикой
        thumbnails = snippet.get('thumbnails', {})
        avatar_url = None
        
        # Приоритет: high -> medium -> default
        for quality in ['high', 'medium', 'default']:
            if quality in thumbnails and thumbnails[quality].get('url'):
                avatar_url = thumbnails[quality]['url']
                safe_print(f"Found avatar ({quality}): {avatar_url}")
                break
        
        # Если аватар не найден, создаем fallback URL
        if not avatar_url:
            # Используем стандартный формат аватара YouTube
            channel_name = snippet.get('title', 'Channel')
            avatar_url = f"https://ui-avatars.com/api/?name={channel_name.replace(' ', '+')}&size=240&background=ff0000&color=ffffff&bold=true"
            safe_print(f"Using fallback avatar: {avatar_url}")
        
        # Проверяем, что URL корректный
        if avatar_url and not avatar_url.startswith('http'):
            avatar_url = f"https:{avatar_url}" if avatar_url.startswith('//') else f"https://{avatar_url}"
        
        # Получаем прямую ссылку на канал
        channel_url = self._get_channel_url(snippet, channel_id)
        
        return {
            'avatar_url': avatar_url,
            'channel_url': channel_url,
            'title': snippet['title'],
            'description': snippet.get('description', ''),
            'subscriber_count': int(channel.get('statistics', {}).get('subscriberCount', 0))
        }
        
    except Exception as e:
        safe_print(f"Error fetching channel info: {e}")
        import traceback
        safe_print(f"Traceback: {traceback.format_exc()}")
        return None

# Инструкция по применению:
# Замените метод _get_channel_info в youtube_service.py на этот код
