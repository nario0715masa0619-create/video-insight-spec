# converter/views_generator_service.py

"""
Views Generator Service for insight_spec

生成される views:
- competitive: YouTube メトリクス + top_pins_by_engagement
- education: 難易度分布 + top_pins_by_difficulty
- self_improvement: テーマ・ファネル分布 + funnel_flow
"""

from datetime import datetime
from collections import Counter
from .engagement_scorer import calculate_engagement_score


class ViewsGeneratorService:
    
    def generate_views(self, video_meta, center_pins, youtube_metrics):
        """
        Generate views section for insight_spec.
        
        Args:
            video_meta (dict): {video_id, channel_id, title, url, published_at}
            center_pins (list): List of center_pin objects
            youtube_metrics (dict): {view_count, like_count, comment_count}
        
        Returns:
            dict: views section with competitive, education, self_improvement
        """
        
        views = {
            "competitive": self._generate_competitive_view(center_pins, youtube_metrics),
            "education": self._generate_education_view(center_pins),
            "self_improvement": self._generate_self_improvement_view(center_pins),
        }
        
        return views
    
    def _generate_competitive_view(self, center_pins, youtube_metrics):
        """YouTube メトリクス + top_pins_by_engagement"""
        
        # Snapshot timestamp（統一）
        now = datetime.utcnow().isoformat() + "Z"
        
        # engagement_score を各ピンに付与してソート
        pins_with_score = []
        for pin in center_pins:
            score = calculate_engagement_score(pin)
            pins_with_score.append({
                "pin": pin,
                "engagement_score": score
            })
        
        # 上位 3 件を抽出
        top_pins = sorted(pins_with_score, key=lambda x: x['engagement_score'], reverse=True)[:3]
        
        view_count = youtube_metrics.get('view_count', 0)
        like_count = youtube_metrics.get('like_count', 0)
        comment_count = youtube_metrics.get('comment_count', 0)
        
        return {
            "###_metadata": {
                "snapshot_timestamp": now,
                "snapshot_history": [
                    {
                        "timestamp": now,
                        "view_count": view_count,
                        "like_count": like_count,
                        "comment_count": comment_count,
                    }
                ]
            },
            "metrics": {
                "view_count": view_count,
                "like_count": like_count,
                "comment_count": comment_count,
                "engagement_rate": round((like_count + comment_count) / view_count, 4) if view_count > 0 else 0.0,
                "likes_per_1000_views": round((like_count / view_count * 1000), 2) if view_count > 0 else 0.0,
                "comments_per_1000_views": round((comment_count / view_count * 1000), 2) if view_count > 0 else 0.0,
            },
            "top_pins_by_engagement": [
                {
                    "element_id": item['pin']['element_id'],
                    "type": item['pin']['type'],
                    "content": self._truncate_content(item['pin']['content']),
                    "business_theme": item['pin']['labels'].get('business_theme', []),
                    "funnel_stage": item['pin']['labels'].get('funnel_stage'),
                    "difficulty": item['pin']['labels'].get('difficulty'),
                    "engagement_score": round(item['engagement_score'], 2)
                }
                for item in top_pins
            ]
        }
    
    def _generate_education_view(self, center_pins):
        """難易度分布 + top_pins_by_difficulty"""
        
        # 難易度別に分類
        pins_by_difficulty = {
            "beginner": [],
            "intermediate": [],
            "advanced": []
        }
        
        difficulty_distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}
        
        for pin in center_pins:
            difficulty = pin['labels'].get('difficulty', 'beginner')
            
            # 未知の難易度が来た場合は setdefault で対応
            pins_by_difficulty.setdefault(difficulty, []).append(pin)
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1
        
        # 各難易度で top 3 を抽出
        top_pins_by_difficulty = {}
        for difficulty in ["beginner", "intermediate", "advanced"]:
            pins = pins_by_difficulty.get(difficulty, [])
            sorted_pins = sorted(pins, key=lambda p: calculate_engagement_score(p), reverse=True)[:3]
            top_pins_by_difficulty[difficulty] = [
                {
                    "element_id": pin['element_id'],
                    "content": self._truncate_content(pin['content']),
                    "business_theme": pin['labels'].get('business_theme', []),
                    "type": pin['type']
                }
                for pin in sorted_pins
            ]
        
        return {
            "difficulty_distribution": difficulty_distribution,
            "top_pins_by_difficulty": top_pins_by_difficulty
        }
    
    def _generate_self_improvement_view(self, center_pins):
        """business_theme/funnel_stage 分布 + funnel_flow"""
        
        # Theme と Stage の分布を集計
        theme_dist = {}
        stage_dist = {}
        pins_by_stage = {}
        
        for pin in center_pins:
            # Theme 集計
            for theme in pin['labels'].get('business_theme', []):
                theme_dist[theme] = theme_dist.get(theme, 0) + 1
            
            # Stage 集計
            stage = pin['labels'].get('funnel_stage', '認知')
            stage_dist[stage] = stage_dist.get(stage, 0) + 1
            
            pins_by_stage.setdefault(stage, []).append(pin)
        
        # Funnel Flow を構築
        funnel_order = ["認知", "興味", "比較", "教育", "クロージング", "継続・LTV"]
        funnel_flow = []
        
        for stage in funnel_order:
            pins = pins_by_stage.get(stage, [])
            pin_count = len(pins)
            
            # Top themes in this stage
            stage_themes = {}
            for pin in pins:
                for theme in pin['labels'].get('business_theme', []):
                    stage_themes[theme] = stage_themes.get(theme, 0) + 1
            
            top_themes = sorted(stage_themes.items(), key=lambda x: x[1], reverse=True)[:3]
            top_themes_list = [theme for theme, _ in top_themes]
            
            # Average difficulty（簡易版：最初の値）
            difficulties = [pin['labels'].get('difficulty', 'beginner') for pin in pins]
            avg_difficulty = difficulties[0] if difficulties else None
            
            funnel_flow.append({
                "stage": stage,
                "pin_count": pin_count,
                "top_themes": top_themes_list,
                "average_difficulty": avg_difficulty
            })
        
        return {
            "business_theme_distribution": theme_dist,
            "funnel_stage_distribution": stage_dist,
            "funnel_flow": funnel_flow
        }
    
    @staticmethod
    def _truncate_content(content, max_length=100):
        """Content を指定長さで切り詰める"""
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content

