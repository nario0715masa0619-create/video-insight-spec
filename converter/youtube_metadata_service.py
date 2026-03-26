"""
YouTubeMetadataService - YouTube API でメタデータを取得

責務:
- YouTube API キー管理
- video_id から動画情報を取得
- channel_id, url, published_at を抽出
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError("google-api-python-client がインストールされていません。pip install google-api-python-client を実行してください。")

class YouTubeAPIError(Exception):
    pass

class YouTubeMetadataService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("❌ YOUTUBE_API_KEY が設定されていません。環境変数または引数で指定してください。")
        
        try:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)
            self.logger.info("✅ YouTube API クライアントを初期化しました")
        except Exception as e:
            self.logger.error(f"❌ YouTube API 初期化エラー: {e}")
            raise YouTubeAPIError(f"YouTube API 初期化失敗: {e}")
    
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """
        video_id から YouTube メタデータを取得
        
        Args:
            video_id (str): YouTube video_id
        
        Returns:
            Dict[str, Any]: {
                "video_id": str,
                "channel_id": str,
                "title": str,
                "url": str,
                "published_at": str (ISO8601)
            }
        
        Raises:
            YouTubeAPIError: API 呼び出し失敗時
        """
        try:
            self.logger.info(f"📡 YouTube API から video_id '{video_id}' のメタデータを取得中...")
            
            request = self.youtube.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            
            if not response.get("items"):
                self.logger.error(f"❌ video_id '{video_id}' が見つかりません")
                raise YouTubeAPIError(f"video_id '{video_id}' が見つかりません")
            
            item = response["items"][0]
            snippet = item.get("snippet", {})
            
            metadata = {
                "video_id": video_id,
                "channel_id": snippet.get("channelId"),
                "title": snippet.get("title"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "published_at": snippet.get("publishedAt")
            }
            
            self.logger.info(f"✅ メタデータ取得成功: {metadata['title']}")
            return metadata
        
        except HttpError as e:
            self.logger.error(f"❌ YouTube API エラー: {e}")
            raise YouTubeAPIError(f"YouTube API エラー: {e}")
        except Exception as e:
            self.logger.error(f"❌ 予期しないエラー: {e}")
            raise YouTubeAPIError(f"予期しないエラー: {e}")
    
    def get_video_analytics(self, video_id: str) -> Dict[str, Any]:
        """
        YouTube Data API から動画の統計情報を取得
        
        Args:
            video_id (str): YouTube video ID
        
        Returns:
            dict: {
                "view_count": int,
                "like_count": int,
                "comment_count": int
            }
        """
        
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            # Statistics を取得
            request = youtube.videos().list(
                part='statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"video_id '{video_id}' が見つかりません")
            
            stats = response['items'][0]['statistics']
            
            return {
                "view_count": int(stats.get('viewCount', 0)),
                "like_count": int(stats.get('likeCount', 0)),
                "comment_count": int(stats.get('commentCount', 0)),
            }
        
        except Exception as e:
            raise YouTubeAPIError(f"YouTube Analytics API エラー: {str(e)}")
