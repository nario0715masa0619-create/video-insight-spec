"""
generate_video_mapping.py

downloaded_videos フォルダから新しい video_mapping.csv を生成
YouTube API で各動画を検索して video_id を取得
"""

import os
import csv
import logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

try:
    from googleapiclient.discovery import build
except ImportError:
    logger.error("google-api-python-client がインストールされていません")
    exit(1)

def generate_video_mapping(videos_dir: str, output_csv: str, api_key: str):
    """
    downloaded_videos から video_mapping.csv を生成
    """
    videos_path = Path(videos_dir)
    
    if not videos_path.exists():
        logger.error(f"❌ ディレクトリが見つかりません: {videos_dir}")
        return False
    
    # YouTube API クライアント
    youtube = build("youtube", "v3", developerKey=api_key)
    
    # ビデオファイルリスト
    video_files = sorted(videos_path.glob("*.mp4"))
    logger.info(f"✅ {len(video_files)} 個のビデオファイルを検出")
    
    rows = []
    
    for video_file in video_files:
        filename = video_file.name
        # ファイル名から lecture_id とタイトルを抽出
        # 形式: XX_タイトル.mp4
        parts = filename.replace(".mp4", "").split("_", 1)
        lecture_id = parts[0]
        title = parts[1] if len(parts) > 1 else ""
        
        logger.info(f"\n【Lecture {lecture_id}】")
        logger.info(f"  ファイル名: {filename}")
        logger.info(f"  タイトル: {title}")
        
        # YouTube で検索
        try:
            request = youtube.search().list(
                part="snippet",
                q=title,
                type="video",
                maxResults=1
            )
            response = request.execute()
            
            if response.get("items"):
                item = response["items"][0]
                video_id = item["id"]["videoId"]
                logger.info(f"  ✅ video_id: {video_id}")
                
                # video_id から メタデータ取得
                videos_request = youtube.videos().list(
                    part="statistics",
                    id=video_id
                )
                videos_response = videos_request.execute()
                
                stats = videos_response["items"][0].get("statistics", {})
                view_count = int(stats.get("viewCount", 0))
                like_count = int(stats.get("likeCount", 0))
                comment_count = int(stats.get("commentCount", 0))
                
                engagement_rate = 0
                if view_count > 0:
                    engagement_rate = round((like_count + comment_count) / view_count * 100, 2)
                
                rows.append({
                    "lecture_id": lecture_id,
                    "filename": filename,
                    "title": title,
                    "video_id": video_id,
                    "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                    "view_count": view_count,
                    "like_count": like_count,
                    "comment_count": comment_count,
                    "engagement_rate": engagement_rate
                })
            else:
                logger.warning(f"  ⚠️ YouTube 検索結果なし")
                rows.append({
                    "lecture_id": lecture_id,
                    "filename": filename,
                    "title": title,
                    "video_id": "NOT_FOUND",
                    "youtube_url": "N/A",
                    "view_count": 0,
                    "like_count": 0,
                    "comment_count": 0,
                    "engagement_rate": 0
                })
        except Exception as e:
            logger.error(f"  ❌ エラー: {e}")
            rows.append({
                "lecture_id": lecture_id,
                "filename": filename,
                "title": title,
                "video_id": "ERROR",
                "youtube_url": "N/A",
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0,
                "engagement_rate": 0
            })
    
    # CSV に書き込み
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "lecture_id", "filename", "title", "video_id", "youtube_url",
            "view_count", "like_count", "comment_count", "engagement_rate"
        ])
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(f"\n✅ {output_csv} を生成しました")
    return True

if __name__ == "__main__":
    videos_dir = r"D:\AI_Data\video-insight-spec\downloaded_videos"
    output_csv = "phase2_2_output/video_mapping_new.csv"
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        logger.error("❌ YOUTUBE_API_KEY が設定されていません")
        exit(1)
    
    generate_video_mapping(videos_dir, output_csv, api_key)
