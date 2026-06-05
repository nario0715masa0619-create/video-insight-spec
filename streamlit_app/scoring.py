import yaml
from pathlib import Path
from typing import Optional

def load_config() -> dict:
    config_path = Path(__file__).parent / "scoring_config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def calculate_quality_score(insight_spec: dict) -> Optional[float]:
    """
    insight_spec から quality_score を計算（暫定ロジック）
    計算不可の場合は None を返す
    """
    if not insight_spec or not isinstance(insight_spec, dict):
        return None

    config = load_config()
    quality_config = config.get("quality_score", {})
    weights = quality_config.get("weights", {"labels": 30, "metadata": 40, "structure": 30})
    thresholds = quality_config.get("thresholds", {"max_labels": 50, "expected_metadata_keys": 8, "max_structure_score": 20})

    # 1. ラベル付与数スコア
    knowledge_core = insight_spec.get("knowledge_core", {})
    center_pins = knowledge_core.get("center_pins", [])
    label_count = sum(1 for pin in center_pins if pin.get("label"))
    max_labels = thresholds.get("max_labels", 50)
    label_score = min(label_count / max_labels, 1.0) * weights.get("labels", 30)

    # 2. メタデータ充実度
    video_metadata = insight_spec.get("video_metadata", {})
    metadata_count = len(video_metadata.keys())
    expected_keys = thresholds.get("expected_metadata_keys", 8)
    metadata_score = min(metadata_count / expected_keys, 1.0) * weights.get("metadata", 40)

    # 3. 構造化完成度
    # 簡易的に center_pins 数で評価。また content_summary 等があれば加点することも可能だが、今回は簡易版。
    structure_count = len(center_pins)
    if "content_summary" in insight_spec and insight_spec["content_summary"]:
        structure_count += 5  # content_summary があれば少し加点
        
    max_structure = thresholds.get("max_structure_score", 20)
    structure_score = min(structure_count / max_structure, 1.0) * weights.get("structure", 30)

    total_score = label_score + metadata_score + structure_score
    return round(total_score, 1)

