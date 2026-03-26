"""
Growth View Service - 伸びている講座ランキング生成
"""


class GrowthViewService:
    """Growth View 生成サービス"""

    @staticmethod
    def generate_growth_view(insight_specs, role="self"):
        """
        複数講座の insight_spec から growth_view を生成
        """
        growth_items = []
        
        for spec in insight_specs:
            lecture_id = spec.get("lecture_id", "unknown")
            # ✅ FIX: video_meta から title を取得
            title = spec.get("video_meta", {}).get("title", "")
            
            views = spec.get("views", {})
            competitive = views.get("competitive", {})
            snapshot_history = competitive.get("snapshot_history", [])
            
            if len(snapshot_history) < 2:
                continue
            
            baseline = snapshot_history[0]
            current = snapshot_history[-1]
            
            baseline_view_count = baseline.get("view_count", 0)
            current_view_count = current.get("view_count", 0)
            baseline_engagement_rate = baseline.get("engagement_rate", 0.0)
            current_engagement_rate = current.get("engagement_rate", 0.0)
            
            view_count_delta = current_view_count - baseline_view_count
            view_count_growth_rate = (
                round(view_count_delta / baseline_view_count, 4) 
                if baseline_view_count > 0 else 0.0
            )
            engagement_rate_delta = round(
                current_engagement_rate - baseline_engagement_rate, 4
            )
            
            growth_item = {
                "role": role,
                "lecture_id": lecture_id,
                "title": title,  # ✅ FIX: video_meta.title を使用
                "view_count_delta": view_count_delta,
                "view_count_growth_rate": view_count_growth_rate,
                "engagement_rate_delta": engagement_rate_delta
            }
            
            growth_items.append(growth_item)
        
        growth_items.sort(key=lambda x: x["view_count_delta"], reverse=True)
        
        period_start = "unknown"
        period_end = "unknown"
        
        if insight_specs and len(insight_specs[0].get("views", {}).get("competitive", {}).get("snapshot_history", [])) >= 2:
            first_spec_history = insight_specs[0]["views"]["competitive"]["snapshot_history"]
            period_start = first_spec_history[0].get("timestamp", "unknown").split("T")[0]
            period_end = first_spec_history[-1].get("timestamp", "unknown").split("T")[0]
        
        return {
            "period": f"{period_start} to {period_end}",
            "top_by_view_growth": growth_items
        }
