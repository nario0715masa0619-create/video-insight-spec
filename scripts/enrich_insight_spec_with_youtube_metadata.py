import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.env_loader import ensure_env_loaded
ensure_env_loaded()

"""
enrich_insight_spec_with_youtube_metadata.py

video_mapping.csv から YouTube video_id を取得し、
YouTube API でメタデータを取得して insight_spec を更新する
"""

import os
import sys
import csv
import logging
import argparse
from pathlib import Path

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 環境変数読み込み
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
from env_loader import load_env
load_env()

try:
    from converter.youtube_metadata_service import YouTubeMetadataService, YouTubeAPIError
    from converter.insight_spec_repository import InsightSpecRepository, InsightSpecLoadError, InsightSpecSaveError
except ImportError as e:
    logger.error(f"❌ インポートエラー: {e}")
    sys.exit(1)

def load_video_mapping(csv_path: str) -> dict:
    """
    video_mapping.csv から lecture_id -> youtube_video_id のマッピングを読み込み
    
    Returns:
        dict: {lecture_id: youtube_video_id, ...}
    """
    mapping = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lecture_id = row['lecture_id'].zfill(2)
                video_id = row['video_id']
                if video_id and video_id != 'NOT_FOUND':
                    mapping[lecture_id] = video_id
        logger.info(f"✅ video_mapping.csv から {len(mapping)} 件の video_id マッピングを読み込みました")
        return mapping
    except Exception as e:
        logger.error(f"❌ video_mapping.csv 読み込みエラー: {e}")
        raise

def enrich_insight_specs(archive_dir: str, csv_path: str, lecture_ids: list, api_key: str = None):
    """
    insight_spec を YouTube メタデータで更新
    
    Args:
        archive_dir: アーカイブディレクトリパス
        csv_path: video_mapping.csv パス
        lecture_ids: 講座ID リスト（["01", "02", ...] など）
        api_key: YouTube API キー（オプション）
    """
    
    logger.info("=" * 80)
    logger.info("【Phase 3.3: YouTube メタデータで insight_spec を更新】")
    logger.info("=" * 80)
    
    try:
        # video_mapping.csv からマッピング読み込み
        video_mapping = load_video_mapping(csv_path)
        
        # YouTube API クライアント初期化
        youtube_service = YouTubeMetadataService(api_key=api_key)
        
        # リポジトリ初期化
        repository = InsightSpecRepository(archive_dir)
        
        total_success = 0
        total_failure = 0
        
        for lecture_id in lecture_ids:
            try:
                logger.info(f"\n【Lecture {lecture_id}】")
                
                # video_mapping から YouTube video_id を取得
                youtube_video_id = video_mapping.get(lecture_id)
                
                if not youtube_video_id:
                    logger.warning(f"⚠️ video_mapping.csv に video_id が見つかりません。スキップします。")
                    total_failure += 1
                    continue
                
                logger.info(f"  YouTube video_id: {youtube_video_id}")
                
                # YouTube API からメタデータを取得
                youtube_metadata = youtube_service.get_video_metadata(youtube_video_id)
                
                # video_meta を更新
                updated_meta = {
                    "video_id": lecture_id,
                    "channel_id": youtube_metadata["channel_id"],
                    "title": youtube_metadata["title"],
                    "url": youtube_metadata["url"],
                    "published_at": youtube_metadata["published_at"]
                }
                
                # ファイルに保存
                repository.update_video_meta(lecture_id, updated_meta)
                
                logger.info(f"✅ Lecture {lecture_id} の video_meta を更新しました")
                logger.info(f"  - channel_id: {updated_meta['channel_id']}")
                logger.info(f"  - title: {updated_meta['title']}")
                logger.info(f"  - url: {updated_meta['url']}")
                logger.info(f"  - published_at: {updated_meta['published_at']}")
                
                total_success += 1
            
            except (YouTubeAPIError, InsightSpecLoadError, InsightSpecSaveError) as e:
                logger.error(f"❌ Lecture {lecture_id} の更新に失敗しました: {e}")
                total_failure += 1
            except Exception as e:
                logger.error(f"❌ 予期しないエラー (Lecture {lecture_id}): {e}")
                total_failure += 1
        
        logger.info("\n" + "=" * 80)
        logger.info(f"【結果】成功: {total_success}, 失敗: {total_failure}")
        logger.info("=" * 80)
        
        return total_failure == 0
    
    except Exception as e:
        logger.error(f"❌ 処理エラー: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube メタデータで insight_spec を更新")
    parser.add_argument("--lecture-ids", type=str, default="01,02,03,04,05",
                        help="講座ID（カンマ区切り、デフォルト: 01,02,03,04,05）")
    parser.add_argument("--archive-dir", type=str, default=os.getenv("ARCHIVE_OUTPUT_DIR", "./archive"),
                        help="アーカイブディレクトリ（デフォルト: 環境変数 ARCHIVE_OUTPUT_DIR または ./archive）")
    parser.add_argument("--csv-path", type=str, default="phase2_2_output/video_mapping.csv",
                        help="video_mapping.csv パス（デフォルト: phase2_2_output/video_mapping.csv）")
    parser.add_argument("--api-key", type=str, default=os.getenv("YOUTUBE_API_KEY"),
                        help="YouTube API キー（デフォルト: 環境変数 YOUTUBE_API_KEY）")
    
    args = parser.parse_args()
    
    if not args.archive_dir:
        logger.error("エラー: アーカイブディレクトリが指定されていません（--archive-dir または ARCHIVE_OUTPUT_DIR）。")
        logger.error("正しい実行例:\n  python scripts/enrich_insight_spec_with_youtube_metadata.py\nまたは\n  python scripts/enrich_insight_spec_with_youtube_metadata.py --archive-dir /path/to/archive")
        sys.exit(1)
    
    if not Path(args.csv_path).exists():
        logger.error(f"エラー: video_mapping.csv が見つかりません: {args.csv_path}")
        logger.error("正しい実行例:\n  python scripts/enrich_insight_spec_with_youtube_metadata.py --csv-path /path/to/video_mapping.csv")
        sys.exit(1)
    
    lecture_ids = [lid.strip().zfill(2) for lid in args.lecture_ids.split(",")]
    
    if not args.api_key:
        logger.error("エラー: YouTube API キーが設定されていません（--api-key または YOUTUBE_API_KEY）。")
        logger.error("正しい実行例:\n  python scripts/enrich_insight_spec_with_youtube_metadata.py --api-key YOUR_API_KEY")
        sys.exit(1)
    
    success = enrich_insight_specs(args.archive_dir, args.csv_path, lecture_ids, args.api_key)
    sys.exit(0 if success else 1)
