import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter
import math

logger = logging.getLogger(__name__)

def load_scoring_config(weights_path: str, rules_path: str) -> tuple[Dict, Dict]:
    """設定ファイル読み込み"""
    with open(weights_path, 'r', encoding='utf-8') as f:
        weights = json.load(f)
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    return weights, rules

def extract_text_units(knowledge_core: Dict) -> tuple[List[str], List[str]]:
    """center_pins と knowledge_points からテキスト抽出"""
    center_pin_texts = []
    knowledge_point_texts = []
    
    center_pins = knowledge_core.get("center_pins", [])
    for pin in center_pins:
        if isinstance(pin, dict) and "content" in pin:
            center_pin_texts.append(pin["content"])
    
    knowledge_points = knowledge_core.get("knowledge_points", [])
    for kp in knowledge_points:
        if isinstance(kp, dict) and "content" in kp:
            knowledge_point_texts.append(kp["content"])
    
    return center_pin_texts, knowledge_point_texts

def calculate_text_quality_score(center_pin_texts: List[str], knowledge_point_texts: List[str]) -> tuple[float, Dict]:
    """text_quality_score を計算"""
    all_texts = center_pin_texts + knowledge_point_texts
    
    if not all_texts:
        return 0.5, {"warning": "insufficient_text_data"}
    
    # 簡略版: テキスト品質指標を計算
    total_length = sum(len(text) for text in all_texts)
    avg_length = total_length / len(all_texts) if all_texts else 0
    
    missing_rate = 0.0 if center_pin_texts else 0.2
    noise_rate = 0.05
    duplication_rate = 0.02
    short_fragment_rate = 0.1 if avg_length < 50 else 0.0
    
    text_quality_score = 1 - (
        0.25 * missing_rate +
        0.25 * noise_rate +
        0.25 * duplication_rate +
        0.25 * short_fragment_rate
    )
    
    details = {
        "missing_rate": missing_rate,
        "noise_rate": noise_rate,
        "duplication_rate": duplication_rate,
        "short_fragment_rate": short_fragment_rate,
        "total_texts": len(all_texts),
        "avg_text_length": round(avg_length, 2)
    }
    
    return max(0.0, min(1.0, text_quality_score)), details

def calculate_semantic_purity_score(knowledge_core: Dict) -> tuple[float, Dict]:
    """semantic_purity_score を計算"""
    center_pins = knowledge_core.get("center_pins", [])
    
    if not center_pins:
        return 0.5, {"warning": "no_center_pins"}
    
    # テーマ分布を抽出
    themes = []
    for pin in center_pins:
        if isinstance(pin, dict) and "labels" in pin:
            labels = pin["labels"]
            if isinstance(labels, dict) and "business_theme" in labels:
                pin_themes = labels["business_theme"]
                if isinstance(pin_themes, list):
                    themes.extend(pin_themes)
    
    if not themes:
        return 0.5, {"warning": "no_themes_found"}
    
    # dominant_theme_ratio 計算
    theme_counts = Counter(themes)
    most_common_count = theme_counts.most_common(1)[0][1] if theme_counts else 0
    dominant_theme_ratio = most_common_count / len(themes) if themes else 0.0
    
    # topic_entropy_score 計算（散らばりの逆数）
    total = len(themes)
    entropy = 0.0
    for count in theme_counts.values():
        if count > 0:
            prob = count / total
            entropy -= prob * math.log(prob) if prob > 0 else 0
    max_entropy = math.log(len(theme_counts)) if len(theme_counts) > 1 else 1
    topic_entropy_score = 1 - (entropy / max_entropy) if max_entropy > 0 else 0.5
    
    # topic_transition_stability （簡略版: ランダムに 0.7～0.9）
    topic_transition_stability = 0.75
    
    semantic_purity_score = (
        0.4 * dominant_theme_ratio +
        0.3 * topic_entropy_score +
        0.3 * topic_transition_stability
    )
    
    details = {
        "dominant_theme_ratio": round(dominant_theme_ratio, 2),
        "topic_entropy_score": round(topic_entropy_score, 2),
        "topic_transition_stability": round(topic_transition_stability, 2),
        "unique_themes": len(theme_counts),
        "total_theme_mentions": len(themes)
    }
    
    return max(0.0, min(1.0, semantic_purity_score)), details

def calculate_business_fit_score(knowledge_core: Dict, rules: Dict) -> tuple[float, Dict]:
    """business_fit_score を計算"""
    classification_confidence = knowledge_core.get("classification_confidence", {})
    
    content_type_confidence = classification_confidence.get("content_type", 0.5)
    business_stage_confidence = classification_confidence.get("business_stage", 0.5)
    
    # theme_business_value_score を計算
    center_pins = knowledge_core.get("center_pins", [])
    theme_business_value_scores = []
    
    theme_mapping = rules.get("business_fit_mapping", {}).get("theme_business_value", {})
    
    for pin in center_pins:
        if isinstance(pin, dict) and "labels" in pin:
            labels = pin["labels"]
            if isinstance(labels, dict) and "business_theme" in labels:
                themes = labels["business_theme"]
                if isinstance(themes, list):
                    for theme in themes:
                        score = theme_mapping.get(theme, 0.5)
                        theme_business_value_scores.append(score)
    
    theme_business_value_score = (
        sum(theme_business_value_scores) / len(theme_business_value_scores)
        if theme_business_value_scores else 0.5
    )
    
    business_fit_score = (
        0.35 * content_type_confidence +
        0.35 * business_stage_confidence +
        0.3 * theme_business_value_score
    )
    
    details = {
        "content_type_confidence": round(content_type_confidence, 2),
        "business_stage_confidence": round(business_stage_confidence, 2),
        "theme_business_value_score": round(theme_business_value_score, 2),
        "theme_scores_count": len(theme_business_value_scores)
    }
    
    return max(0.0, min(1.0, business_fit_score)), details

def calculate_quality_score(text_quality_score: float, semantic_purity_score: float) -> float:
    """quality_score を計算"""
    quality_score = (
        0.45 * text_quality_score +
        0.55 * semantic_purity_score
    )
    return max(0.0, min(1.0, quality_score))

def calculate_ranking_score(quality_score: float, business_fit_score: float) -> float:
    """ranking_score を計算"""
    ranking_score = (
        0.75 * quality_score +
        0.25 * business_fit_score
    )
    return max(0.0, min(1.0, ranking_score))

def build_scoring_result(insight_json: Dict, weights: Dict, rules: Dict) -> Dict[str, Any]:
    """スコアリング結果を構築"""
    knowledge_core = insight_json.get("knowledge_core", {})
    
    # テキスト抽出
    center_pin_texts, knowledge_point_texts = extract_text_units(knowledge_core)
    
    # 各スコアを計算
    text_quality_score, tq_details = calculate_text_quality_score(
        center_pin_texts, knowledge_point_texts
    )
    semantic_purity_score, sp_details = calculate_semantic_purity_score(knowledge_core)
    business_fit_score, bf_details = calculate_business_fit_score(knowledge_core, rules)
    
    # 総合スコアを計算
    quality_score = calculate_quality_score(text_quality_score, semantic_purity_score)
    ranking_score = calculate_ranking_score(quality_score, business_fit_score)
    
    # warnings を集約
    warnings = []
    if "warning" in tq_details:
        warnings.append(tq_details["warning"])
    if "warning" in sp_details:
        warnings.append(sp_details["warning"])
    
    # classification_confidence を取得
    classification_confidence = knowledge_core.get("classification_confidence", {
        "theme": 0.5,
        "content_type": 0.5,
        "business_stage": 0.5
    })
    
    # 結果を構築
    result = {
        "classification_confidence": classification_confidence,
        "scoring": {
            "text_quality_score": round(text_quality_score, 2),
            "semantic_purity_score": round(semantic_purity_score, 2),
            "business_fit_score": round(business_fit_score, 2),
            "quality_score": round(quality_score, 2),
            "ranking_score": round(ranking_score, 2),
            "score_version": weights.get("version", "v2.1"),
            "rules_version": rules.get("rules_version", "unknown"),
            "calculation_timestamp": datetime.now().isoformat()
        },
        "score_details": {
            **tq_details,
            **sp_details,
            **bf_details
        },
        "warnings": warnings
    }
    
    return result

def score_insight_json(insight_json: Dict, weights_path: str, rules_path: str) -> Dict[str, Any]:
    """メイン関数: insight JSON をスコアリング"""
    weights, rules = load_scoring_config(weights_path, rules_path)
    return build_scoring_result(insight_json, weights, rules)
