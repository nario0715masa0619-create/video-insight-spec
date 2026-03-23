import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class InsightsConverter:
    """最終的な video-insight-spec JSON を生成するクラス"""

    @staticmethod
    def build_insight_spec(
        video_meta: Dict[str, Any],
        knowledge_core: Dict[str, Any],
        views_competitive: Dict[str, Any]
    ) -> Dict[str, Any]:
        """video-insight-spec 形式の完全な JSON を生成"""
        return {
            "video_meta": video_meta,
            "knowledge_core": knowledge_core,
            "views": {
                "competitive": views_competitive,
                "self_improvement": {},
                "education": {}
            },
            "_metadata": {
                "converted_at": datetime.utcnow().isoformat() + "Z",
                "source_system": "video-scraper / Antigravity Ver.1.0",
                "conversion_version": "v1.0_phase1",
                "conversion_phase": "Phase 1",
                "data_sources": {
                    "core_json": "Mk2_Core_XX.json",
                    "sidecar_db": "Mk2_Sidecar_XX.db",
                    "youtube_api": False,
                    "youtube_analytics_api": False
                },
                "implementation_notes": {
                    "like_count_and_comment_count": "推定値（null 許容）",
                    "youtube_api_fields": "Phase 2 以降で実装予定",
                    "nlp_keyword_extraction": "Phase 2 で JANOME/transformers に差し替え予定"
                }
            }
        }

    @staticmethod
    def save_to_file(insight_spec: Dict[str, Any], output_path: str) -> bool:
        """JSON をファイルに保存
        
        Note: 出力ディレクトリが存在しない場合、自動作成する
        """
        try:
            import os
            # 出力ディレクトリを確保
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(insight_spec, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved insight spec to {output_path}")
            return True

        except PermissionError as e:
            logger.error(f"Permission denied writing to {output_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving insight spec: {e}")
            return False


def calculate_engagement_metrics(view_count, like_count, comment_count):
    """
    基本メトリクスから派生指標を計算する
    
    Args:
        view_count (int): 再生数
        like_count (int): 高評価数
        comment_count (int): コメント数
    
    Returns:
        dict: engagement_metrics
            - engagement_rate (float): (likes + comments) / view_count * 100
                                       view_count が 0 の場合は 0
            - likes_per_1000_views (float): likes / view_count * 1000
                                             view_count が 0 の場合は 0
            - comments_per_1000_views (float): comments / view_count * 1000
                                                view_count が 0 の場合は 0
    """
    if view_count == 0:
        return {
            "engagement_rate": 0.0,
            "likes_per_1000_views": 0.0,
            "comments_per_1000_views": 0.0
        }
    
    engagement_rate = ((like_count + comment_count) / view_count) * 100
    likes_per_1000 = (like_count / view_count) * 1000
    comments_per_1000 = (comment_count / view_count) * 1000
    
    return {
        "engagement_rate": round(engagement_rate, 2),
        "likes_per_1000_views": round(likes_per_1000, 2),
        "comments_per_1000_views": round(comments_per_1000, 2)
    }
