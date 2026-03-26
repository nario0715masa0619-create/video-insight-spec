"""
Portfolio View Service - 講座ポートフォリオマップ生成

目的：自社・競合それぞれの「講座構造」を俯瞳する。
- role（self / competitor）
- dominant_funnel_stage（最多 stage）
- dominant_difficulty（最多 difficulty）
- total_center_pins
- latest_view_count / engagement_rate
"""

from collections import Counter


class PortfolioViewService:
    """Portfolio View 生成サービス"""

    @staticmethod
    def generate_portfolio_view(insight_specs, role="self"):
        """
        複数講座の insight_spec から portfolio_view を生成
        
        Args:
            insight_specs: [{ lecture_id, title, video_meta, knowledge_core, views }, ...]
            role: "self" または "competitor"
        
        Returns:
            [{ role, lecture_id, title, dominant_funnel_stage, dominant_difficulty, 
               total_center_pins, view_count, engagement_rate }, ...]
        """
        portfolio = []
        
        for spec in insight_specs:
            lecture_id = spec.get("lecture_id", "unknown")
            title = spec.get("title", "")
            
            # center_pins から dominant_funnel_stage と dominant_difficulty を計算
            center_pins = spec.get("knowledge_core", {}).get("center_pins", [])
            total_center_pins = len(center_pins)
            
            # funnel_stage, difficulty の出現頻度を計算
            funnel_stages = []
            difficulties = []
            
            for pin in center_pins:
                labels = pin.get("labels", {})
                funnel_stage = labels.get("funnel_stage")
                difficulty = labels.get("difficulty")
                
                if funnel_stage:
                    funnel_stages.append(funnel_stage)
                if difficulty:
                    difficulties.append(difficulty)
            
            # 最多の funnel_stage と difficulty を決定
            dominant_funnel_stage = Counter(funnel_stages).most_common(1)[0][0] if funnel_stages else "unknown"
            dominant_difficulty = Counter(difficulties).most_common(1)[0][0] if difficulties else "unknown"
            
            # latest_view_count と engagement_rate を取得（snapshot_history の最新から）
            views = spec.get("views", {})
            competitive = views.get("competitive", {})
            
            # snapshot_history が存在すればそこから、なければ metrics から取得
            snapshot_history = competitive.get("snapshot_history", [])
            if snapshot_history:
                latest_snapshot = snapshot_history[-1]
                view_count = latest_snapshot.get("view_count", 0)
                engagement_rate = latest_snapshot.get("engagement_rate", 0.0)
            else:
                metrics = competitive.get("metrics", {})
                view_count = metrics.get("view_count", 0)
                engagement_rate = metrics.get("engagement_rate", 0.0)
            
            portfolio_item = {
                "role": role,
                "lecture_id": lecture_id,
                "title": title,
                "dominant_funnel_stage": dominant_funnel_stage,
                "dominant_difficulty": dominant_difficulty,
                "total_center_pins": total_center_pins,
                "view_count": view_count,
                "engagement_rate": round(engagement_rate, 4)
            }
            
            portfolio.append(portfolio_item)
        
        return portfolio
