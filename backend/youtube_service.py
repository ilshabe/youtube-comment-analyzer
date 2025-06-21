"""
Исправленный сервис для работы с YouTube Data API v3
Добавлены: прямые ссылки на каналы и улучшенное получение аватаров
"""

import os
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def safe_print(text):
    """Безопасная печать для избежания проблем с кодировкой"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Заменяем проблемные символы на безопасные
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

class YouTubeService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.youtube = None
        
        if self.api_key and self.api_key != "YOUR_API_KEY_HERE":
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                safe_print(f"Failed to initialize YouTube API: {e}")
                self.youtube = None

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Получает информацию о видео через реальный API"""
        if not self.youtube:
            safe_print("YouTube API not initialized, cannot fetch video info.")
            return None
        return self._get_real_video_info(video_id)

    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Получает комментарии к видео через реальный API"""
        if not self.youtube:
            safe_print("YouTube API not initialized, cannot fetch comments.")
            return []
        return self._get_real_comments(video_id, max_results)

    def _get_real_video_info(self, video_id: str) -> Optional[Dict]:
        """Получает реальную информацию о видео через API"""
        try:
            safe_print(f"YouTube API available: {self.youtube is not None}")
            if not self.youtube:
                safe_print("YouTube API not initialized")
                return None
            # Получаем информацию о видео
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            video = response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']
            channel_id = snippet['channelId']
            safe_print(f"Channel ID from API: {channel_id}")
            
            # Получаем информацию о канале для аватарки и прямой ссылки
            channel_info = self._get_channel_info(channel_id)
            
            return {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'channel_title': snippet['channelTitle'],
                'channel_id': channel_id,
                'channel_avatar': channel_info.get('avatar_url') if channel_info else None,
                'channel_url': channel_info.get('channel_url') if channel_info else f"https://www.youtube.com/channel/{channel_id}",
                'published_at': snippet['publishedAt'],
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'duration': video.get('contentDetails', {}).get('duration', ''),
                'tags': snippet.get('tags', [])
            }
            
        except HttpError as e:
            safe_print(f"YouTube API error: {e}")
            safe_print(f"Error details: {e.resp.status}, {e.content}")
            return None
        except Exception as e:
            safe_print(f"Error fetching video info: {e}")
            import traceback
            safe_print(f"Traceback: {traceback.format_exc()}")
            return None

    def _get_real_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Получает реальные комментарии через API"""
        comments = []
        
        try:
            safe_print(f"Getting real comments for video: {video_id}")
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(max_results, 100),
                order="relevance"
            )
            
            while request and len(comments) < max_results:
                response = request.execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    
                    comments.append({
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'likes': comment['likeCount'],
                        'published_at': comment['publishedAt'],
                        'reply_count': item['snippet']['totalReplyCount'],
                        'author_avatar': comment.get('authorProfileImageUrl', '')
                    })
                
                # Получаем следующую страницу, если есть
                if 'nextPageToken' in response and len(comments) < max_results:
                    request = self.youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=min(max_results - len(comments), 100),
                        pageToken=response['nextPageToken'],
                        order="relevance"
                    )
                else:
                    break
                    
        except HttpError as e:
            safe_print(f"YouTube API error while fetching comments: {e}")
            safe_print(f"Error details: {e.resp.status}, {e.content}")
        except Exception as e:
            safe_print(f"Error fetching comments: {e}")
            import traceback
            safe_print(f"Traceback: {traceback.format_exc()}")
        
        return comments[:max_results]

    def _get_channel_info(self, channel_id: str) -> Optional[Dict]:
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
            
            # Получаем URL аватарки канала (приоритет: high -> medium -> default)
            thumbnails = snippet.get('thumbnails', {})
            avatar_url = None
            
            # Приоритет: high -> medium -> default
            for quality in ['high', 'medium', 'default']:
                if quality in thumbnails:
                    avatar_url = thumbnails[quality]['url']
                    break
            
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

    def _get_channel_url(self, snippet: Dict, channel_id: str) -> str:
        """Получает прямую ссылку на канал"""
        # Пробуем получить handle (новый формат @username)
        custom_url = snippet.get('customUrl', '')
        
        if custom_url:
            # Если есть customUrl, проверяем формат
            if custom_url.startswith('@'):
                return f"https://www.youtube.com/{custom_url}"
            elif custom_url.startswith('c/') or custom_url.startswith('user/'):
                return f"https://www.youtube.com/{custom_url}"
            else:
                # Если customUrl без префикса, добавляем @
                return f"https://www.youtube.com/@{custom_url}"
        
        # Fallback на стандартную ссылку через channel ID
        return f"https://www.youtube.com/channel/{channel_id}"

    def extract_video_id(self, url: str) -> Optional[str]:
        """Извлекает video_id из различных форматов YouTube URL"""
        import re
        
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

    def validate_video_id(self, video_id: str) -> bool:
        """Проверяет корректность video_id"""
        import re
        if not video_id or len(video_id) != 11:
            return False
        return bool(re.match(r'^[0-9A-Za-z_-]{11}$', video_id))

