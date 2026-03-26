"""
Growth View Service - 伸びている講座ランキング生成

目的：ここ数週間でどの講座が伸びているかを把握する。
- view_count_delta / growth_rate
- engagement_rate_delta
"""


class GrowthViewService:
    """Growth View 生成サービス"""

    @staticmethod
    def generate_growth_view(insight_specs, role="self"):
        """
        複数講座の insight_spec から growth_view を生成
        
        Args:
            insight_specs: [{ lecture_id, title, views }, ...]
            role: "self" または "competitor"
        
        Returns:
            {
              "period": "YYYY-MM-DD to YYYY-MM-DD",
              "top_by_view_growth": [
                { role, lecture_id, title, view_count_delta, view_count_growth_rate, 
                  engagement_rate_delta },
                ...
              ]
            }
        """
        growth_items = []
        
        for spec in insight_specs:
            lecture_id = spec.get("lecture_id", "unknown")
            title = spec.get("title", "")
            
            # snapshot_history から baseline と current を取得
            views = spec.get("views", {})
            competitive = views.get("competitive", {})
            snapshot_history = competitive.get("snapshot_history", [])
            
            if len(snapshot_history) < 2:
                # baseline のみの場合は delta を計算できないのでスキップ
                continue
            
            baseline = snapshot_history[0]
            current = snapshot_history[-1]
            
            baseline_view_count = baseline.get("view_count", 0)
            current_view_count = current.get("view_count", 0)
            baseline_engagement_rate = baseline.get("engagement_rate", 0.0)
            current_engagement_rate = current.get("engagement_rate", 0.0)
            
            # delta と growth_rate を計算
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
                "title": title,
                "view_count_delta": view_count_delta,
                "view_count_growth_rate": view_count_growth_rate,
                "engagement_rate_delta": engagement_rate_delta
            }
            
            growth_items.append(growth_item)
        
        # view_count_delta でソート（降順）
        growth_items.sort(key=lambda x: x["view_count_delta"], reverse=True)
        
        # 期間を取得（snapshot_history の最初と最後のタイムスタンプから）
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
