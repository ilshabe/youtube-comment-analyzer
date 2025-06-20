"""
Сервис для работы с YouTube Data API v3
"""

import os
import random
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

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
        """Получает информацию о видео"""
        if self.youtube:
            return self._get_real_video_info(video_id)
        else:
            return self._simulate_video_info(video_id)

    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Получает комментарии к видео"""
        if self.youtube:
            return self._get_real_comments(video_id, max_results)
        else:
            return self._simulate_comments(video_id, max_results)

    def _get_real_video_info(self, video_id: str) -> Optional[Dict]:
        """Получает реальную информацию о видео через API"""
        try:
            safe_print(f"YouTube API available: {self.youtube is not None}")
            if not self.youtube:
                safe_print("YouTube API not initialized, using simulation")
                return None
            # Получаем информацию о видео
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            video = response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']
            channel_id = snippet['channelId']
            
            # Получаем информацию о канале для аватарки
            channel_info = self._get_channel_info(channel_id)
            
            return {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'channel_title': snippet['channelTitle'],
                'channel_id': channel_id,
                'channel_avatar': channel_info.get('avatar_url') if channel_info else None,
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
            if not self.youtube:
                safe_print("YouTube API not initialized, using simulation")
                return self._simulate_comments(video_id, max_results)
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
            # Возвращаем симулированные комментарии в случае ошибки
            return self._simulate_comments(video_id, max_results)
        except Exception as e:
            safe_print(f"Error fetching comments: {e}")
            import traceback
            safe_print(f"Traceback: {traceback.format_exc()}")
            return self._simulate_comments(video_id, max_results)
        
        return comments[:max_results]

    def _get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Получает информацию о канале"""
        try:
            request = self.youtube.channels().list(
                part="snippet",
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            channel = response['items'][0]
            snippet = channel['snippet']
            
            # Получаем URL аватарки канала (высокое качество)
            thumbnails = snippet.get('thumbnails', {})
            avatar_url = None
            
            # Приоритет: high -> medium -> default
            for quality in ['high', 'medium', 'default']:
                if quality in thumbnails:
                    avatar_url = thumbnails[quality]['url']
                    break
            
            return {
                'avatar_url': avatar_url,
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'subscriber_count': channel.get('statistics', {}).get('subscriberCount', 0)
            }
            
        except Exception as e:
            safe_print(f"Error fetching channel info: {e}")
            import traceback
            safe_print(f"Traceback: {traceback.format_exc()}")
            return None

    def _simulate_video_info(self, video_id: str) -> Dict:
        """Симулирует информацию о видео"""
        random.seed(hash(video_id) % 2**32)
        
        titles = [
            "Как создать успешный YouTube канал: секреты блогеров",
            "10 лайфхаков для YouTube создателей",
            "Обзор новых технологий в области ИИ: итоги 2024",
            "Секреты монетизации контента",
            "Психология успешного контента",
            "How to Build a Successful YouTube Channel",
            "Top 10 Content Creation Tips",
            "AI Technology Review: 2024 Updates",
            "Content Monetization Strategies",
            "The Psychology of Viral Content"
        ]
        
        channels = [
            "TechReview", "CreatorTips", "AIInsights", "ContentMaster", "DigitalSuccess",
            "ТехОбзор", "СоветыБлогерам", "ИИАналитика", "КонтентМастер", "ЦифровойУспех"
        ]
        
        channel_name = random.choice(channels)
        
        return {
            'title': random.choice(titles),
            'description': "Подробное описание видео с полезной информацией...",
            'channel_title': channel_name,
            'channel_id': f"UC{random.randint(100000000000000000000, 999999999999999999999)}",
            'channel_avatar': f"https://ui-avatars.com/api/?name={channel_name.replace(' ', '+')}&size=240&background=00ffff&color=000000&bold=true",
            'published_at': "2024-01-15T10:00:00Z",
            'view_count': random.randint(1000, 500000),
            'like_count': random.randint(50, 25000),
            'comment_count': random.randint(10, 1000),
            'duration': "PT10M30S",
            'tags': ["youtube", "tutorial", "tips", "content creation"]
        }

    def _simulate_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Симулирует комментарии к видео"""
        random.seed(hash(video_id) % 2**32)
        
        # Расширенный набор комментариев на разных языках
        comment_templates = {
            'positive_ru': [
                "Отличное видео! Очень полезная информация",
                "Спасибо за подробное объяснение, все понятно",
                "Супер контент! Жду новых видео",
                "Браво! Именно то, что искал",
                "Классная подача материала, лайк!",
                "Очень крутой канал, подписался",
                "Потрясающе! Узнал много нового",
                "Отлично объяснили, спасибо большое"
            ],
            'positive_en': [
                "Amazing video! Very helpful information",
                "Thanks for the detailed explanation, very clear",
                "Great content! Looking forward to more videos",
                "Awesome! Exactly what I was looking for",
                "Love the way you present the material!",
                "Really cool channel, subscribed",
                "Fantastic! Learned so much new stuff",
                "Excellent explanation, thank you so much"
            ],
            'neutral_ru': [
                "Интересно, но хотелось бы больше примеров",
                "Неплохо, но можно было бы подробнее",
                "Нормальное видео, но есть вопросы",
                "В целом понятно, спасибо",
                "Хорошо, но не хватает практических советов",
                "Видео норм, но звук мог быть лучше"
            ],
            'neutral_en': [
                "Interesting, but would like more examples",
                "Not bad, but could be more detailed",
                "Decent video, but I have some questions",
                "Generally clear, thanks",
                "Good, but lacks practical advice",
                "Video is okay, but audio could be better"
            ],
            'confused_ru': [
                "Не совсем понял момент с...",
                "Можете объяснить подробнее?",
                "А как это работает на практике?",
                "Что делать, если не получается?",
                "Непонятно, почему так происходит",
                "Можно пример попроще?"
            ],
            'confused_en': [
                "Didn't quite understand the part about...",
                "Could you explain in more detail?",
                "How does this work in practice?",
                "What to do if it doesn't work?",
                "Not clear why this happens",
                "Could you give a simpler example?"
            ],
            'frustrated_ru': [
                "Не работает, что делать?",
                "Слишком сложно объясняете",
                "Потратил время зря",
                "Ничего не понял из видео",
                "Плохо объяснили",
                "Не помогло решить проблему"
            ],
            'frustrated_en': [
                "Doesn't work, what should I do?",
                "Too complicated explanation",
                "Wasted my time",
                "Didn't understand anything from the video",
                "Poorly explained",
                "Didn't help solve the problem"
            ]
        }
        
        authors = [
            "@user123", "@techfan", "@learner2024", "@creator_pro", "@newbie_yt",
            "@пользователь123", "@техноман", "@ученик2024", "@создатель_про", "@новичок_yt",
            "@content_lover", "@video_watcher", "@tutorial_fan", "@knowledge_seeker",
            "@любитель_контента", "@зритель_видео", "@фан_туториалов", "@искатель_знаний"
        ]
        
        comments = []
        num_comments = min(max_results, random.randint(20, 100))
        
        # Распределение типов комментариев
        comment_types = ['positive_ru', 'positive_en', 'neutral_ru', 'neutral_en', 
                        'confused_ru', 'confused_en', 'frustrated_ru', 'frustrated_en']
        
        for i in range(num_comments):
            comment_type = random.choice(comment_types)
            text = random.choice(comment_templates[comment_type])
            
            # Добавляем вариативность
            if random.random() < 0.3:  # 30% шанс добавить эмодзи
                emojis = ["👍", "❤️", "🔥", "💯", "👏", "🤔", "😊", "🙏", "✨", "💪"]
                text += " " + random.choice(emojis)
            
            author = random.choice(authors)
            
            comments.append({
                'author': author,
                'text': text,
                'likes': random.randint(0, 50),
                'published_at': f"2024-01-{random.randint(10, 20):02d}T{random.randint(10, 23):02d}:00:00Z",
                'reply_count': random.randint(0, 5),
                'author_avatar': f"https://ui-avatars.com/api/?name={author.replace('@', '').replace('_', '+')}&size=88&background={random.choice(['ff6b6b', '4ecdc4', '45b7d1', 'feca57', 'ff9ff3'])}&color=ffffff&bold=true"
            })
        
        # Сортируем по лайкам (самые популярные сначала)
        comments.sort(key=lambda x: x['likes'], reverse=True)
        
        return comments

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
