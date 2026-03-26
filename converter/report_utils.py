# converter/report_utils.py

from datetime import datetime
from typing import Dict, Any, List

def calculate_delta(baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, int]:
    """
    Baseline と current のメトリクスから delta（差分）を計算
    
    Args:
        baseline: 前回のスナップショット metrics
        current: 今回のスナップショット metrics
    
    Returns:
        各メトリクスの増加量
    """
    return {
        "view_count": current.get("view_count", 0) - baseline.get("view_count", 0),
        "like_count": current.get("like_count", 0) - baseline.get("like_count", 0),
        "comment_count": current.get("comment_count", 0) - baseline.get("comment_count", 0),
    }

def calculate_growth_percentage(baseline: Dict[str, Any], delta: Dict[str, int]) -> Dict[str, float]:
    """
    成長率（パーセンテージ）を計算
    
    Args:
        baseline: 前回のスナップショット metrics
        delta: 増加量
    
    Returns:
        各メトリクスの成長率（%）
    """
    result = {}
    for key in ["view_count", "like_count", "comment_count"]:
        baseline_val = baseline.get(key, 0)
        if baseline_val == 0:
            result[key] = 0.0
        else:
            result[key] = round((delta[key] / baseline_val) * 100, 2)
    return result

def format_metric(value: int, metric_type: str = "count") -> str:
    """
    メトリクスをフォーマット（カンマ区切りなど）
    
    Args:
        value: メトリクス値
        metric_type: タイプ（"count" または "percentage"）
    
    Returns:
        フォーマット済み文字列
    """
    if metric_type == "count":
        return f"{value:,}"
    elif metric_type == "percentage":
        return f"{value:.2f}%"
    return str(value)

def generate_delta_summary(delta: Dict[str, int], growth_percentage: Dict[str, float]) -> str:
    """
    Delta をサマリーテキストで生成
    
    例: "先週比 +0.58% 増加（+666 views、+46 likes）"
    
    Args:
        delta: 増加量
        growth_percentage: 成長率
    
    Returns:
        サマリーテキスト
    """
    view_delta = delta.get("view_count", 0)
    view_growth = growth_percentage.get("view_count", 0)
    like_delta = delta.get("like_count", 0)
    
    return f"先週比 +{view_growth:.2f}% 増加（+{format_metric(view_delta)} views、+{format_metric(like_delta)} likes）"

def get_trend_indicator(growth_percentage: float) -> str:
    """
    成長率に基づいてトレンドを判定
    
    Args:
        growth_percentage: 成長率（%）
    
    Returns:
        トレンド指標（"📈"、"→"、"📉"）
    """
    if growth_percentage > 2.0:
        return "📈 上昇傾向"
    elif growth_percentage > -2.0:
        return "→ 横ばい"
    else:
        return "📉 下降傾向"
