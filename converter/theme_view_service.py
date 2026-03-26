"""
Theme View Service - テーマ別"勝ち講座"ランキング生成
"""


class ThemeViewService:
    """Theme View 生成サービス"""

    @staticmethod
    def generate_theme_view(insight_specs, role="self"):
        """
        複数講座の insight_spec からテーマ別ランキング (theme_view) を生成
        
        Args:
            insight_specs: List of insight_spec dicts
            role: "self" or "competitor"
        
        Returns:
            Dict with structure: {"theme_name": [items]}
            Each item: {role, lecture_id, title, view_count, engagement_rate, representative_pin}
        """
        theme_groups = {}

        for spec in insight_specs:
            lecture_id = spec.get("lecture_id", "unknown")
            title = spec.get("video_meta", {}).get("title", "")

            # center_pins を取得
            center_pins = spec.get("knowledge_core", {}).get("center_pins", [])
            if not center_pins:
                continue

            # business_theme でグループ化
            for pin in center_pins:
                labels = pin.get("labels", {})
                business_theme_raw = labels.get("business_theme")
                
                # business_theme が list の場合は最初の要素を使用
                if isinstance(business_theme_raw, list):
                    business_theme = business_theme_raw[0] if business_theme_raw else None
                else:
                    business_theme = business_theme_raw
                
                if not business_theme:
                    continue

                # theme_groups に講座を追加
                if business_theme not in theme_groups:
                    theme_groups[business_theme] = []

                # views から最新の view_count と engagement_rate を取得
                views = spec.get("views", {})
                competitive = views.get("competitive", {})
                snapshot_history = competitive.get("snapshot_history", [])

                if snapshot_history:
                    latest_snap = snapshot_history[-1]
                    view_count = latest_snap.get("view_count", 0)
                    engagement_rate = latest_snap.get("engagement_rate", 0.0)
                else:
                    view_count = 0
                    engagement_rate = 0.0

                # 講座の情報を集約（重複排除）
                lecture_info = {
                    "role": role,
                    "lecture_id": lecture_id,
                    "title": title,
                    "view_count": view_count,
                    "engagement_rate": engagement_rate,
                    "max_pin_engagement": 0.0,
                    "representative_pin": None
                }

                # このテーマに既に同じ講座があるかチェック
                existing = [item for item in theme_groups[business_theme] 
                           if item["lecture_id"] == lecture_id]
                if existing:
                    continue

                theme_groups[business_theme].append(lecture_info)

        # 各テーマで最も engagement_score が高い pin を representative_pin として選出
        for spec in insight_specs:
            lecture_id = spec.get("lecture_id", "unknown")
            title = spec.get("video_meta", {}).get("title", "")
            center_pins = spec.get("knowledge_core", {}).get("center_pins", [])

            for business_theme, items in theme_groups.items():
                for item in items:
                    if item["lecture_id"] != lecture_id:
                        continue

                    # このテーマに属する pin の中で engagement_score が最高のものを選出
                    theme_pins = []
                    for p in center_pins:
                        labels = p.get("labels", {})
                        business_theme_raw = labels.get("business_theme")
                        
                        # business_theme が list の場合は最初の要素を使用
                        if isinstance(business_theme_raw, list):
                            pin_theme = business_theme_raw[0] if business_theme_raw else None
                        else:
                            pin_theme = business_theme_raw
                        
                        if pin_theme == business_theme:
                            theme_pins.append(p)

                    if theme_pins:
                        best_pin = None
                        best_score = -1

                        for pin in theme_pins:
                            labels = pin.get("labels", {})
                            purity = labels.get("base_purity_score", 0) / 100.0

                            # type_weight
                            pin_type = labels.get("type", "concept")
                            type_weights = {
                                "framework": 1.0,
                                "strategy": 0.8,
                                "tactic": 0.6,
                                "concept": 0.4
                            }
                            type_weight = type_weights.get(pin_type, 0.4)

                            # stage_weight
                            stage = labels.get("funnel_stage", "認知")
                            stage_weights = {
                                "クロージング": 1.0,
                                "継続・LTV": 0.9,
                                "比較": 0.8,
                                "教育": 0.7,
                                "興味": 0.5,
                                "認知": 0.3
                            }
                            stage_weight = stage_weights.get(stage, 0.3)

                            # engagement_score = 0.6 * purity + 0.2 * type_weight + 0.2 * stage_weight
                            engagement_score = 0.6 * purity + 0.2 * type_weight + 0.2 * stage_weight

                            if engagement_score > best_score:
                                best_score = engagement_score
                                best_pin = pin

                        if best_pin:
                            item["representative_pin"] = {
                                "element_id": best_pin.get("element_id", "unknown"),
                                "content": best_pin.get("content", "")
                            }
                            item["max_pin_engagement"] = round(best_score, 4)

        # 各テーマ内で view_count が最高の講座を選出
        theme_view = {}
        for business_theme, items in theme_groups.items():
            if items:
                sorted_items = sorted(items, key=lambda x: x["view_count"], reverse=True)
                top_items = sorted_items[:3]
                
                for item in top_items:
                    del item["max_pin_engagement"]
                
                theme_view[business_theme] = top_items

        return theme_view
