import pandas as pd
import numpy as np
from data_loader import load_insight_specs, load_executive_report
from collections import defaultdict

class AnalyticsEngine:
    def __init__(self):
        self.insight_specs = load_insight_specs()
        self.exec_report = load_executive_report()

    def calculate_aggregate_metrics(self):
        """チャンネル全体の集約メトリクス"""
        if not self.exec_report:
            return {}
        
        lectures_dict = self.exec_report.get('lectures', {})
        if not isinstance(lectures_dict, dict) or len(lectures_dict) == 0:
            return {}

        views_list = []
        likes_list = []
        comments_list = []
        sp_list = []
        q_list = []
        r_list = []
        
        for lecture_id, lec in lectures_dict.items():
            metadata = lec.get('metadata', {})
            views_list.append(metadata.get('views', 0))
            likes_list.append(metadata.get('likes', 0))
            comments_list.append(metadata.get('comments', 0))
            sp = lec.get('semantic_purity_score')
            if sp is not None: sp_list.append(sp)
            q = lec.get('quality_score')
            if q is not None: q_list.append(q)
            r = lec.get('ranking_score')
            if r is not None: r_list.append(r)
        
        return {
            'avg_semantic_purity': round(np.mean(sp_list), 1) if sp_list else None,
            'avg_quality': round(np.mean(q_list), 1) if q_list else None,
            'avg_ranking': round(np.mean(r_list), 1) if r_list else None,
            'total_views': sum(views_list),
            'total_likes': sum(likes_list),
            'total_comments': sum(comments_list),
            'semantic_purity_count': len(sp_list),
            'quality_count': len(q_list),
            'ranking_count': len(r_list)
        }

    def get_funnel_stage_analysis(self, lecture_id):
        """ファネルステージ別分析"""
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return None

        pins = spec.get('knowledge_core', {}).get('center_pins', [])
        funnel_data = defaultdict(list)
        
        for pin in pins:
            labels = pin.get('labels', {})
            funnel_stage = labels.get('funnel_stage', '不明')
            engagement = pin.get('engagement_score', pin.get('base_purity_score', 0)) / 100.0
            funnel_data[funnel_stage].append(engagement)
        
        result = {}
        for stage, scores in funnel_data.items():
            result[stage] = {
                'avg_engagement': round(np.mean(scores), 2),
                'count': len(scores)
            }
        
        return result

    def get_content_type_analysis(self, lecture_id):
        """コンテンツタイプ別分析"""
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return None

        pins = spec.get('knowledge_core', {}).get('center_pins', [])
        content_data = defaultdict(list)
        
        for pin in pins:
            content_type = pin.get('type', '不明')
            quality = pin.get('base_purity_score', 0)
            content_data[content_type].append(quality)
        
        result = {}
        for ctype, scores in content_data.items():
            result[ctype] = {
                'avg_quality': round(np.mean(scores), 1),
                'count': len(scores)
            }
        
        return result

    def get_theme_distribution(self, lecture_id):
        """テーマ分布"""
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return {}
        
        return spec['views'].get('self_improvement', {}).get('business_theme_distribution', {})

    def get_engagement_metrics(self, lecture_id):
        """エンゲージメント効率メトリクス"""
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return {}
        
        metrics = spec.get('views', {}).get('competitive', {}).get('metrics', {})
        return {
            'likes_per_1000_views': metrics.get('likes_per_1000_views', 0),
            'comments_per_1000_views': metrics.get('comments_per_1000_views', 0),
            'engagement_rate': metrics.get('engagement_rate', 0)
        }

    def calculate_efficiency_score(self, lecture_id):
        """エンゲージメント効率スコア（0-100）"""
        metrics = self.get_engagement_metrics(lecture_id)
        likes_per_1k = metrics.get('likes_per_1000_views', 0)
        comments_per_1k = metrics.get('comments_per_1000_views', 0)
        
        likes_score = min(100, (likes_per_1k / 20) * 100) if likes_per_1k else 0
        comments_score = min(100, (comments_per_1k / 1) * 100) if comments_per_1k else 0
        
        overall = (likes_score * 0.6 + comments_score * 0.4)
        return round(min(100, max(0, overall)), 1)

