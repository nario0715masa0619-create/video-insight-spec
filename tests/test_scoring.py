import pytest
import sys
from pathlib import Path

# streamlit_app モジュールをパスに追加
sys.path.append(str(Path(__file__).parent.parent / "streamlit_app"))

from scoring import calculate_quality_score

def test_calculate_quality_score_full():
    """ラベル・メタデータが完全な場合"""
    insight = {
        "knowledge_core": {
            "center_pins": [
                {"label": "概念A"}, {"label": "概念B"}
            ]
        },
        "video_metadata": {
            "title": "...", "url": "...", "publish_date": "...",
            "views": 100, "likes": 10, "comments": 5, "duration": 120, "author": "me"
        },
        "content_summary": "..."
    }
    score = calculate_quality_score(insight)
    assert score is not None
    assert 0 <= score <= 100

def test_calculate_quality_score_minimal():
    """ラベルが少ない場合"""
    insight = {
        "knowledge_core": {"center_pins": []},
        "video_metadata": {}
    }
    score = calculate_quality_score(insight)
    assert score is not None
    assert score < 50  # 低スコア期待

def test_calculate_quality_score_broken():
    """構造が不正な場合"""
    insight = {}
    score = calculate_quality_score(insight)
    # The requirement says "insight = {} -> calculate_quality_score(insight) assert score is None"
    # But wait! If insight = {} is passed, is it invalid?
    # Our code: if not insight_spec or not isinstance(insight_spec, dict): return None
    # If insight = {}, not {} is True, so it returns None.
    assert score is None  # 計算不可
