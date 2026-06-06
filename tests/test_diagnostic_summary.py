import pytest
from streamlit_app.diagnostic_summary import (
    extract_competitive_advantage_summary,
    extract_golden_pattern_summary,
    extract_hidden_weakness_diagnosis,
    load_diagnostic_config
)

def test_diagnostic_config_loading():
    config = load_diagnostic_config()
    assert isinstance(config, dict)
    assert "diagnostic_thresholds" in config
    assert "theme_labels" in config
    assert "funnel_labels" in config

def test_extract_competitive_advantage_summary_high_score():
    advantage = {
        "beginner_suitability": 90.0,
        "theme_diversity": 60.0,
        "content_diversity": 80.0
    }
    result = extract_competitive_advantage_summary(advantage)
    assert "初心者向けに最適化された構成" in result["beginner_focus"]

def test_extract_competitive_advantage_summary_low_score():
    advantage = {
        "beginner_suitability": 20.0,
        "theme_diversity": 20.0,
        "content_diversity": 20.0
    }
    result = extract_competitive_advantage_summary(advantage)
    # 30 未満は上級者・専門家向け
    assert "上級者・専門家向けに特化した構成" in result["beginner_focus"]
    assert "単一テーマに特化した専門的コンテンツ" in result["theme_diversity_desc"]

def test_extract_golden_pattern_summary_theme_translation():
    patterns = [
        {"funnel_stage": "awareness", "content_type": "概念解説", "theme": "marketing", "avg_engagement": 85.5},
        {"funnel_stage": "interest", "content_type": "ケーススタディ", "theme": "sales", "avg_engagement": 70.2}
    ]
    result = extract_golden_pattern_summary(patterns)
    
    # パターン1: marketing -> マーケティング
    assert "マーケティング" in result[0]
    assert "marketing" not in result[0]
    
    # パターン2: sales -> セールス
    assert "セールス" in result[1]
    assert "sales" not in result[1]

def test_extract_golden_pattern_summary_funnel_translation():
    patterns = [
        {"funnel_stage": "awareness", "content_type": "概念解説", "theme": "marketing", "avg_engagement": 85.5},
        {"funnel_stage": "consideration", "content_type": "解説", "theme": "strategy", "avg_engagement": 80.0}
    ]
    result = extract_golden_pattern_summary(patterns)
    assert "認知層" in result[0]
    assert "検討層" in result[1]

def test_config_fallback_on_missing_label():
    patterns = [
        {"funnel_stage": "unknown_funnel", "content_type": "概念解説", "theme": "unknown_theme"}
    ]
    result = extract_golden_pattern_summary(patterns)
    # Configに存在しない場合は元の文字列をそのまま出力するか、不明になるか（実装は get(f_raw, f_raw)なのでそのまま出るはず）
    assert "unknown_funnel層" in result[0]
    assert "unknown_theme" in result[0]

def test_extract_hidden_weakness_diagnosis_no_numbers():
    weakness_data = {
        "base_purity_score": 90.0,
        "actual_engagement": 65.0,
        "gap": 25.0,
        "funnel_stage": "検討",
        "themes": "セールス",
        "content": "具体的なクロージング手法の解説..."
    }
    result = extract_hidden_weakness_diagnosis(weakness_data)
    
    assert "90.0" not in result["state"]
    assert "25.0" not in result["state"]
    assert "65.0" not in result["state"]

def test_extract_hidden_weakness_diagnosis_with_config():
    weakness_data = {
        "funnel_stage": "awareness",
        "themes": "customer_success",
        "content": "CS手法..."
    }
    result = extract_hidden_weakness_diagnosis(weakness_data)
    assert result["funnel"] == "認知"
    assert result["theme"] == "カスタマーサクセス"

