"""
YouTube Video ID Enricher

insight_spec_XX.json に video_id を自動補充するモジュール
タイトルから YouTube 検索 -> video_id 取得 -> JSON 更新
"""

import json
import pathlib
import logging
from typing import Optional, Dict, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubeVideoIDEnricher:
    """YouTube API を使用して video_id を取得・補充"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: YouTube Data API v3 キー
        """
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)
        self.search_cache = {}

    def search_video_by_title(self, title: str, max_results: int = 1) -> Optional[str]:
        """
        タイトルから YouTube 動画を検索し video_id を取得
        
        Args:
            title: 検索タイトル
            max_results: 最大検索結果数
        
        Returns:
            video_id（見つからない場合は None）
        """
        if title in self.search_cache:
            return self.search_cache[title]
        
        try:
            request = self.youtube.search().list(
                q=title,
                part="snippet",
                type="video",
                maxResults=max_results,
                order="relevance"
            )
            response = request.execute()
            
            if response["items"]:
                video_id = response["items"][0]["id"]["videoId"]
                self.search_cache[title] = video_id
                logger.info(f"✅ Found video_id: {video_id} for title: {title}")
                return video_id
            else:
                logger.warning(f"⚠️ No video found for title: {title}")
                return None
                
        except Exception as e:
            logger.error(f"❌ YouTube API error: {e}")
            return None

    def enrich_insight_spec_json(self, json_path: str) -> Dict:
        """
        insight_spec_XX.json を読込、video_id を補充して保存
        
        Args:
            json_path: insight_spec_XX.json のパス
        
        Returns:
            統計情報（更新件数、失敗件数など）
        """
        json_path = pathlib.Path(json_path)
        
        if not json_path.exists():
            logger.error(f"❌ File not found: {json_path}")
            return {"status": "error", "message": "File not found"}
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # video_meta から情報を取得
            video_meta = data.get("video_meta", {})
            current_video_id = video_meta.get("video_id")
            title = video_meta.get("title", "")
            
            # video_id が lecture_id（"01"～"21"）の場合のみ、YouTube 検索で置き換え
            is_lecture_id = current_video_id and len(current_video_id) <= 2 and current_video_id.isdigit()
            
            if is_lecture_id and title:
                logger.info(f"🔍 Searching video_id for: {title}")
                video_id = self.search_video_by_title(title)
                
                if video_id:
                    data["video_meta"]["video_id"] = video_id
                    
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"✅ Updated {json_path} with video_id: {video_id}")
                    return {
                        "status": "success",
                        "video_id": video_id,
                        "title": title,
                        "json_path": str(json_path)
                    }
                else:
                    return {
                        "status": "not_found",
                        "title": title,
                        "json_path": str(json_path)
                    }
            else:
                return {
                    "status": "already_exists",
                    "video_id": current_video_id,
                    "title": title,
                    "json_path": str(json_path)
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing {json_path}: {e}")
            return {"status": "error", "message": str(e)}

    def enrich_all_lectures(self, archive_dir: str) -> Dict:
        """
        全講義（01～21）の insight_spec_XX.json を一括補充
        
        Args:
            archive_dir: アーカイブディレクトリ
        
        Returns:
            全体統計
        """
        archive_path = pathlib.Path(archive_dir)
        results = {
            "total": 0,
            "success": 0,
            "not_found": 0,
            "already_exists": 0,
            "errors": 0,
            "details": []
        }
        
        # 全講義ファイルを処理
        for i in range(1, 22):  # 01～21
            lecture_id = f"{i:02d}"
            json_path = archive_path / f"insight_spec_{lecture_id}.json"
            
            if json_path.exists():
                results["total"] += 1
                result = self.enrich_insight_spec_json(str(json_path))
                results["details"].append(result)
                
                if result["status"] == "success":
                    results["success"] += 1
                elif result["status"] == "not_found":
                    results["not_found"] += 1
                elif result["status"] == "already_exists":
                    results["already_exists"] += 1
                else:
                    results["errors"] += 1
        
        return results
