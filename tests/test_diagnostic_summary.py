import pytest
from streamlit_app.diagnostic_summary import (
    extract_competitive_advantage_summary,
    extract_golden_pattern_summary,
    extract_hidden_weakness_diagnosis
)

def test_extract_competitive_advantage_summary():
    advantage = {
        "beginner_suitability": 90.0,
        "theme_diversity": 60.0,
        "content_diversity": 80.0
    }
    result = extract_competitive_advantage_summary(advantage)
    
    assert isinstance(result, dict)
    assert result["beginner_focus"] == "初心者向けに最適化された構成"
    assert result["theme_diversity_desc"] == "テーマの多様性は中程度"
    assert result["content_richness"] == "コンテンツの豊かさは高い"
    assert "初心者向けに最適化された構成" in result["overall_positioning"]
    
    # 状態翻訳なので生の数字(90.0)は含まれないことを確認
    assert "90.0" not in result["beginner_focus"]

def test_extract_golden_pattern_summary():
    patterns = [
        {"funnel_stage": "認知", "content_type": "概念解説", "theme": "マーケティング", "avg_engagement": 85.5},
        {"funnel_stage": "関心", "content_type": "ケーススタディ", "theme": "セールス", "avg_engagement": 70.2}
    ]
    result = extract_golden_pattern_summary(patterns)
    
    assert isinstance(result, list)
    assert len(result) == 2
    
    # パターン1
    assert "認知層" in result[0]
    assert "概念解説" in result[0]
    assert "マーケティング" in result[0]
    assert "85.5" not in result[0]  # 数字が含まれないこと
    
    # パターン2
    assert "関心層" in result[1]
    assert "セールス" in result[1]
    assert "70.2" not in result[1]  # 数字が含まれないこと

def test_extract_hidden_weakness_diagnosis():
    weakness_data = {
        "base_purity_score": 90.0,
        "actual_engagement": 65.0,
        "gap": 25.0,
        "funnel_stage": "検討",
        "themes": "セールス",
        "content": "具体的なクロージング手法の解説..."
    }
    result = extract_hidden_weakness_diagnosis(weakness_data)
    
    assert isinstance(result, dict)
    assert "内容は充実しているが視聴者反応が期待値より低い" in result["state"]
    assert result["funnel"] == "検討"
    assert result["theme"] == "セールス"
    
    # 品質スコアやギャップなどの数字が含まれていないこと
    assert "90.0" not in result["state"]
    assert "25.0" not in result["state"]
