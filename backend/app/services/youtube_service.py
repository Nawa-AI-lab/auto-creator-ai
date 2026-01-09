"""خدمة يوتيوب"""
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import pickle
from pathlib import Path

from app.core.config import settings


class YouTubeService:
    """خدمة متكاملة ليوتيوب"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube.readonly'
    ]
    
    def __init__(self):
        self.credentials = None
        self.youtube = None
        self._load_credentials()
    
    def _load_credentials(self):
        """تحميل بيانات الاعتماد"""
        
        # محاولة تحميل من ملف
        token_file = 'token.pickle'
        
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # التحقق من صلاحية الاعتماد
        if self.credentials and self.credentials.expired:
            if self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                self._get_new_credentials()
        
        # تهيئة يوتيوب
        if self.credentials:
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
    
    def _get_new_credentials(self):
        """الحصول على اعتمادات جديدة"""
        
        # هذا يتطلب تفاعل المستخدم مرة واحدة
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',  # ملف بيانات OAuth
            self.SCOPES
        )
        
        self.credentials = flow.run_local_server(port=8080)
        
        # حفظ الاعتماد
        with open('token.pickle', 'wb') as token:
            pickle.dump(self.credentials, token)
    
    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category_id: str = None,
        privacy_status: str = None,
        channel_id: int = None
    ) -> Dict:
        """رفع فيديو على يوتيوب"""
        
        if not self.youtube:
            raise Exception("لم يتم إعداد اعتمادات يوتيوب")
        
        # الإعدادات الافتراضية
        category_id = category_id or settings.YOUTUBE_DEFAULT_CATEGORY
        privacy_status = privacy_status or settings.YOUTUBE_DEFAULT_PRIVACY
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id,
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }
        
        # رفع الفيديو
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True
        )
        
        request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        return {
            'video_id': response['id'],
            'url': f"https://www.youtube.com/watch?v={response['id']}",
            'status': response['status']['uploadStatus']
        }
    
    async def get_video_stats(self, video_id: str) -> Dict:
        """الحصول على إحصائيات الفيديو"""
        
        if not self.youtube:
            raise Exception("لم يتم إعداد اعتمادات يوتيوب")
        
        response = self.youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()
        
        if not response['items']:
            return None
        
        stats = response['items'][0]['statistics']
        
        return {
            'views': stats.get('viewCount', 0),
            'likes': stats.get('likeCount', 0),
            'comments': stats.get('commentCount', 0),
            'favorites': stats.get('favoriteCount', 0)
        }
    
    async def get_channel_info(self) -> Dict:
        """الحصول على معلومات القناة"""
        
        if not self.youtube:
            raise Exception("لم يتم إعداد اعتمادات يوتيوب")
        
        response = self.youtube.channels().list(
            part='snippet,statistics,contentDetails',
            mine=True
        ).execute()
        
        if not response['items']:
            return None
        
        channel = response['items'][0]
        
        return {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'subscribers': channel['statistics'].get('subscriberCount', 0),
            'views': channel['statistics'].get('viewCount', 0),
            'video_count': channel['statistics'].get('videoCount', 0),
            'uploads_playlist': channel['contentDetails']['relatedPlaylists']['uploads']
        }
    
    async def list_videos(self, max_results: int = 50) -> List[Dict]:
        """قائمة فيديوهات القناة"""
        
        if not self.youtube:
            raise Exception("لم يتم إعداد اعتمادات يوتيوب")
        
        channel_info = await self.get_channel_info()
        uploads_playlist = channel_info['uploads_playlist']
        
        response = self.youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=uploads_playlist,
            maxResults=max_results
        ).execute()
        
        videos = []
        for item in response['items']:
            videos.append({
                'id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url']
            })
        
        return videos
