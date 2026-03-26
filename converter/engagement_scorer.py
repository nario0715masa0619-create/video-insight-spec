# converter/engagement_scorer.py

"""
Engagement Score Calculator for video-insight-spec

engagement_score = 0.6 * purity_norm + 0.2 * type_weight + 0.2 * stage_weight
"""

TYPE_WEIGHT = {
    "framework": 1.0,
    "strategy": 0.8,
    "tactic": 0.6,
    "concept": 0.4,
}

STAGE_WEIGHT = {
    "クロージング": 1.0,
    "継続・LTV": 0.9,
    "比較": 0.8,
    "教育": 0.7,
    "興味": 0.5,
    "認知": 0.3,
}


def calculate_engagement_score(center_pin):
    """
    Calculate engagement score for a center pin.
    
    engagement_score = 0.6 * purity_norm + 0.2 * type_weight + 0.2 * stage_weight
    
    Args:
        center_pin (dict): {
            "element_id": "cp_001",
            "type": "concept",
            "base_purity_score": 90,
            "labels": {
                "funnel_stage": "認知",
                ...
            }
        }
    
    Returns:
        float: Engagement score (0.0 ~ 1.0)
    """
    
    # A) Purity を正規化（0～100 → 0～1）
    purity_score = center_pin.get('base_purity_score', 80)
    purity_norm = max(0.0, min(purity_score, 100.0)) / 100.0
    
    # B) Type の重みを取得
    pin_type = center_pin.get('type', 'concept')
    type_score = TYPE_WEIGHT.get(pin_type, 0.5)
    
    # D) Funnel Stage の重みを取得
    funnel_stage = center_pin.get('labels', {}).get('funnel_stage', '認知')
    stage_score = STAGE_WEIGHT.get(funnel_stage, 0.5)
    
    # 合成スコア（0～1 スケール）
    engagement_score = (
        0.6 * purity_norm +
        0.2 * type_score +
        0.2 * stage_score
    )
    
    # Clip to [0.0, 1.0]
    return max(0.0, min(engagement_score, 1.0))
