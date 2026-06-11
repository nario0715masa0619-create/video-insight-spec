import pandas as pd
import numpy as np
from data_loader import load_insight_specs, load_executive_report
from narrative_engine import NarrativeEngine
from collections import defaultdict
import json
from streamlit_app.utils import translate_type

class AdvancedAnalyticsEngine:
    """唯一無二の複合分析エンジン"""
    
    def __init__(self):
        self.insight_specs = load_insight_specs()
        self.exec_report = load_executive_report()
        self.narrative = NarrativeEngine()

    # ========== 唯一無二分析 1: 「黄金の組み合わせ」検出 ==========
    def detect_golden_combination(self, lecture_id):
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return None

        pins = spec.get('knowledge_core', {}).get('center_pins', [])
        matrix_3d = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for pin in pins:
            labels = pin.get('labels', {})
            funnel_stage = labels.get('funnel_stage', '不明')
            content_type = translate_type(pin.get('type', '不明'))
            themes = labels.get('business_theme', [])
            engagement = pin.get('engagement_score', pin.get('base_purity_score', 0)) / 100.0
            
            for theme in themes:
                matrix_3d[funnel_stage][content_type][theme].append(engagement)
        
        golden_combos = []
        for stage, types in matrix_3d.items():
            for ctype, themes_dict in types.items():
                for theme, scores in themes_dict.items():
                    avg_engagement = np.mean(scores)
                    golden_combos.append({
                        'funnel_stage': stage,
                        'content_type': ctype,
                        'theme': theme,
                        'avg_engagement': round(avg_engagement, 3),
                        'count': len(scores)
                    })
        
        golden_combos.sort(key=lambda x: x['avg_engagement'], reverse=True)
        return golden_combos[:10]

    # ========== 唯一無二分析 2: 「隠れた弱点」検出 ==========
    def detect_hidden_weaknesses(self, lecture_id):
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return None

        pins = spec.get('knowledge_core', {}).get('center_pins', [])
        weaknesses = []
        for pin in pins:
            labels = pin.get('labels', {})
            base_purity = pin.get('base_purity_score', 0)
            engagement = pin.get('engagement_score', pin.get('base_purity_score', 0)) / 100.0
            
            if base_purity >= 85 and engagement < 0.7:
                themes = labels.get('business_theme', [])
                weaknesses.append({
                    'element_id': pin.get('element_id', ''),
                    'content': pin.get('content', '')[:60],
                    'base_purity_score': base_purity,
                    'actual_engagement': round(engagement, 2),
                    'gap': round(base_purity / 100 - engagement, 3),
                    'funnel_stage': labels.get('funnel_stage', ''),
                    'themes': ', '.join(themes),
                    'difficulty': labels.get('difficulty', '')
                })
        
        weaknesses.sort(key=lambda x: x['gap'], reverse=True)
        return weaknesses

    # ========== 唯一無二分析 3: 「視聴者心理ロードマップ」生成（バグ修正版）==========
    def generate_viewer_psychology_roadmap(self, lecture_id):
        """【視聴者心理ロードマップ】"""
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return None

        pins = spec.get('knowledge_core', {}).get('center_pins', [])
        funnel_flow = spec.get('views', {}).get('self_improvement', {}).get('funnel_flow', [])
        
        roadmap = []
        
        for flow in funnel_flow:
            stage = flow.get('stage', '不明')
            stage_pins = [p for p in pins if p.get('labels', {}).get('funnel_stage') == stage]
            
            if stage_pins:
                # このステージの全ピンのエンゲージメントを集計
                all_engagements = []
                content_types = defaultdict(list)
                
                for p in stage_pins:
                    engagement = p.get('engagement_score', p.get('base_purity_score', 0)) / 100.0
                    all_engagements.append(engagement)
                    
                    ctype = translate_type(p.get('type', '不明'))
                    content_types[ctype].append(engagement)
                
                # ステージ全体の平均
                stage_avg_engagement = np.mean(all_engagements) if all_engagements else 0
                
                # 最適なコンテンツタイプ
                best_content_type = max(content_types.items(), key=lambda x: np.mean(x[1])) if content_types else ('不明', [0])
                
                top_themes = flow.get('top_themes', [])
                
                roadmap.append({
                    'stage': stage,
                    'description': self._get_stage_description(stage),
                    'best_content_type': best_content_type[0],
                    'avg_engagement': round(stage_avg_engagement, 2),
                    'recommended_themes': top_themes[:3],
                    'pin_count': flow.get('pin_count', 0),
                    'psychology_cue': self._get_psychology_cue(stage)
                })
        
        return roadmap

    # ========== 唯一無二分析 4: 「競争優位性スコア」計算 ==========
    def calculate_competitive_advantage_score(self, lecture_id):
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return None

        pins = spec.get('knowledge_core', {}).get('center_pins', [])
        metrics = spec.get('views', {}).get('competitive', {}).get('metrics', {})
        
        all_themes = {}
        for i in range(1, 6):
            spec_i = self.insight_specs.get(f"{i:02d}")
            themes_i = spec_i['views'].get('self_improvement', {}).get('business_theme_distribution', {}) if spec_i else {}
            for theme, count in themes_i.items():
                all_themes[theme] = all_themes.get(theme, 0) + count
        
        lecture_themes = spec.get('views', {}).get('self_improvement', {}).get('business_theme_distribution', {})
        # テーマ多様性 = このチャンネルが扱うテーマの種類数 / 全体テーマ数（平均5個程度が標準）
        theme_diversity = min(100, (len(lecture_themes) / 5) * 100) if lecture_themes else 0
        
        content_types = set(p.get('type') for p in pins if p.get('type'))
        # 最大 4 種類（concept, strategy, framework, tactic）
        content_diversity = (len(content_types) / 4) * 100 if content_types else 0
        
        # エンゲージメント効率 = (likes + comments) / views を業界平均と比較
        engagement_rate = (metrics.get('like_count', 0) + metrics.get('comment_count', 0)) / max(metrics.get('view_count', 1), 1)
        # 業界平均 ~0.08（8%）に対する相対値。低いと 50% 以下、高いと 80%+ 程度に調整
        engagement_density_score = min(100, (engagement_rate / 0.08) * 50)  # 業界平均 8% を基準に正規化
        
        difficulty_dist = spec.get('views', {}).get('education', {}).get('difficulty_distribution', {})
        beginner_ratio = difficulty_dist.get('beginner', 0) / sum(difficulty_dist.values()) * 100 if sum(difficulty_dist.values()) > 0 else 0
        
        total_score = (theme_diversity * 0.3 + content_diversity * 0.2 + engagement_density_score * 0.3 + beginner_ratio * 0.2)
        
        return {
            'total_score': round(total_score, 1),
            'theme_diversity': round(theme_diversity, 1),
            'content_diversity': round(content_diversity, 1),
            'engagement_density': round(engagement_density_score, 1),
            'beginner_suitability': round(beginner_ratio, 1),
            'interpretation': self._get_advantage_interpretation(total_score)
        }

    # ========== 唯一無二分析 5: 「次のステップ提案」自動生成 ==========
    def generate_next_step_recommendation(self, lecture_id):
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return None

        funnel_flow = spec.get('views', {}).get('self_improvement', {}).get('funnel_flow', [])
        current_stage = funnel_flow[-1]['stage'] if funnel_flow else '不明'
        
        stage_order = ['認知', '興味・関心', '比較検討', '教育', 'クロージング', '継続・LTV']
        current_idx = stage_order.index(current_stage) if current_stage in stage_order else -1
        next_stage = stage_order[current_idx + 1] if current_idx < len(stage_order) - 1 else '継続・LTV'
        
        required_themes = []
        for i in range(1, 6):
            spec_i = self.insight_specs.get(f"{i:02d}")
            if spec_i:
                funnel_i = spec_i.get('views', {}).get('self_improvement', {}).get('funnel_flow', [])
                for flow in funnel_i:
                    if flow.get('stage') == next_stage:
                        required_themes.extend(flow.get('top_themes', []))
        
        return {
            'current_stage': current_stage,
            'next_stage': next_stage,
            'required_themes': list(set(required_themes))[:5],
            'missing_content_types': self._get_missing_content_types(lecture_id, next_stage)
        }

    # ========== ヘルパーメソッド ==========
    def _get_stage_description(self, stage):
        descriptions = {
            '認知': '視聴者が初めて認識する段階。基本知識の提供が重要',
            '興味・関心': '視聴者の興味が高まる段階。実例やメリットの強調',
            '比較検討': '視聴者が複数選択肢を比較。独自性の強調',
            '教育': '深い学習段階。スキルアップとベストプラクティス',
            'クロージング': '購買/申し込み直前。最後の後押し',
            '継続・LTV': 'ファン化とリピート促進。付加価値の提供'
        }
        return descriptions.get(stage, stage)

    def _get_psychology_cue(self, stage):
        cues = {
            '認知': '「これって何？」',
            '興味・関心': '「へえ、面白そう」',
            '比較検討': '「他と何が違うの？」',
            '教育': '「なるほど、こうやるんだ」',
            'クロージング': '「今すぐやってみたい」',
            '継続・LTV': '「また見たい、もっと知りたい」'
        }
        return cues.get(stage, '')

    def _get_advantage_interpretation(self, score):
        if score >= 80:
            return '⭐⭐⭐ 強力な競争優位性を持つ講座'
        elif score >= 60:
            return '⭐⭐ 中程度の競争優位性'
        elif score >= 40:
            return '⭐ 改善の余地あり'
        else:
            return '要改善：複数領域で対策が必要'

    def _get_missing_content_types(self, lecture_id, target_stage):
        spec = self.insight_specs.get(str(lecture_id))
        if not spec:
            return []
        
        current_types = set(p.get('type') for p in spec.get('knowledge_core', {}).get('center_pins', []))
        all_types = {'concept', 'strategy', 'tactic', 'framework'}
        
        return list(all_types - current_types)

