"""
Phase 2.1 品質検証スクリプト（修正版）
- 実データの content + visual_text からキーワード抽出
- JANOME と正規表現の両方で検証
- 品質評価レポート生成
"""

import os
import sys
import json
import csv
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import Counter

# =====================================
# 設定
# =====================================
REPO_ROOT = Path.cwd()
ARCHIVE_DIR = Path("D:/Knowledge_Base/Brain_Marketing/archive")
OUTPUT_DIR = REPO_ROOT / "quality_validation_results"

LECTURE_ID = "01"
CORE_JSON_PATH = ARCHIVE_DIR / f"Mk2_Core_{LECTURE_ID}.json"
SIDECAR_DB_PATH = ARCHIVE_DIR / f"Mk2_Sidecar_{LECTURE_ID}.db"

OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("🔍 Phase 2.1 品質検証スクリプト（修正版）")
print("=" * 80)

# =====================================
# Step 1: 実データの存在確認
# =====================================
print("\n[Step 1] 実データ確認中...")

if not CORE_JSON_PATH.exists():
    print(f"❌ {CORE_JSON_PATH} が見つかりません")
    sys.exit(1)

if not SIDECAR_DB_PATH.exists():
    print(f"❌ {SIDECAR_DB_PATH} が見つかりません")
    sys.exit(1)

print(f"✅ Core JSON: {CORE_JSON_PATH}")
print(f"✅ Sidecar DB: {SIDECAR_DB_PATH}")

# =====================================
# Step 2: 実データを読み込み
# =====================================
print("\n[Step 2] 実データを読み込み中...")

sys.path.insert(0, str(REPO_ROOT))

from converter.json_extractor import JSONExtractor
from converter.db_helper import SidecarDBHelper
from converter.keyword_extractor import KeywordExtractor

# Core JSON を読み込み
extractor_json = JSONExtractor(str(CORE_JSON_PATH))
center_pins = extractor_json.center_pins
print(f"✅ Core JSON 読み込み: {len(center_pins)} 個の要素")

# Sidecar DB を読み込み
records = SidecarDBHelper.load_evidence_index(str(SIDECAR_DB_PATH))
print(f"✅ Sidecar DB 読み込み: {len(records)} 個のレコード")

# =====================================
# Step 3: 抽出対象テキストを準備
# =====================================
print("\n[Step 3] 抽出対象テキストを準備中...")

# content フィールドからテキストを集める
content_text = " ".join([pin["content"] for pin in center_pins])
print(f"✅ Content テキスト: {len(content_text)} 文字")

# visual_text フィールドからテキストを集める
visual_texts = [r.get("visual_text", "") for r in records]
visual_text_combined = " ".join(visual_texts)
print(f"✅ Visual text: {len(visual_text_combined)} 文字")

# 両者を結合
full_text = content_text + " " + visual_text_combined

# =====================================
# Step 4: キーワード抽出（JANOME + 正規表現）
# =====================================
print("\n[Step 4] キーワード抽出中...")

# JANOME モード
extractor_nlp = KeywordExtractor(
    str(SIDECAR_DB_PATH), 
    records, 
    use_nlp=True
)
keywords_nlp = extractor_nlp.extract_keywords(full_text)

# 正規表現モード
extractor_regex = KeywordExtractor(
    str(SIDECAR_DB_PATH), 
    records, 
    use_nlp=False
)
keywords_regex = extractor_regex.extract_keywords(full_text)

print(f"✅ JANOME キーワード: {len(keywords_nlp)} 個")
if keywords_nlp:
    print(f"   例: {keywords_nlp[:10]}")

print(f"✅ 正規表現キーワード: {len(keywords_regex)} 個")
if keywords_regex:
    print(f"   例: {keywords_regex[:10]}")

# =====================================
# Step 5: キーワード品質評価（改善版）
# =====================================
print("\n[Step 5] キーワード品質を評価中...")

class KeywordQualityAssessment:
    """キーワード品質評価クラス（改善版）"""
    
    def __init__(self, keywords, records, center_pins):
        self.keywords = keywords
        self.records = records
        self.center_pins = center_pins
        self.quality_scores = {}
    
    def assess(self):
        """全キーワードを評価"""
        for keyword in self.keywords:
            score = self._evaluate_single(keyword)
            self.quality_scores[keyword] = score
        return self.quality_scores
    
    def _evaluate_single(self, keyword):
        """単一キーワードの品質スコアを計算"""
        
        # 1. visual_text での出現頻度
        visual_freq = sum(1 for r in self.records if keyword in r.get("visual_text", ""))
        visual_freq_score = min(visual_freq * 15, 25)
        
        # 2. content での出現頻度
        content_freq = sum(1 for pin in self.center_pins if keyword in pin.get("content", ""))
        content_freq_score = min(content_freq * 20, 25)
        
        # 3. セグメント分散度
        segment_count = len([r for r in self.records if keyword in r.get("visual_text", "")])
        dispersion_score = min(segment_count * 5, 20)
        
        # 4. ノイズ度
        noise_score = 0
        if self._is_generic_word(keyword):
            noise_score = -15
        elif len(keyword) == 1:
            noise_score = -10
        
        # 5. 信頼度（visual_score の平均）
        avg_visual_score = 0
        count = 0
        for r in self.records:
            if keyword in r.get("visual_text", ""):
                avg_visual_score += r.get("visual_score", 0.5)
                count += 1
        
        trust_score = (avg_visual_score / count * 30) if count > 0 else 0
        
        total_score = max(0, min(100, 
            visual_freq_score + content_freq_score + dispersion_score + noise_score + trust_score
        ))
        
        return {
            "total_score": round(total_score, 2),
            "visual_freq_score": round(visual_freq_score, 2),
            "content_freq_score": round(content_freq_score, 2),
            "dispersion_score": round(dispersion_score, 2),
            "noise_score": round(noise_score, 2),
            "trust_score": round(trust_score, 2),
            "visual_freq": visual_freq,
            "content_freq": content_freq,
            "segment_count": segment_count,
            "avg_visual_confidence": round(avg_visual_score / count if count > 0 else 0, 2)
        }
    
    def _is_generic_word(self, keyword):
        """汎用ワード判定"""
        generic_words = {
            "video", "image", "content", "data", "system", "tool",
            "the", "a", "an", "and", "or", "is", "to", "of", "が", "を", "に", "は"
        }
        return keyword.lower() in generic_words
    
    def get_high_quality_keywords(self, threshold=60):
        """高品質キーワードを抽出"""
        return {
            kw: score for kw, score in self.quality_scores.items()
            if score["total_score"] >= threshold
        }

# 品質評価を実行
assessor = KeywordQualityAssessment(keywords_nlp if keywords_nlp else keywords_regex, records, center_pins)
quality_scores = assessor.assess()

high_quality_keywords = assessor.get_high_quality_keywords(threshold=60)

print(f"✅ 評価キーワード数: {len(quality_scores)} 個")
print(f"✅ 高品質キーワード（スコア >= 60）: {len(high_quality_keywords)} 個")

if high_quality_keywords:
    print("\n   上位 10 個:")
    for kw, score in sorted(high_quality_keywords.items(), key=lambda x: x[1]["total_score"], reverse=True)[:10]:
        print(f"   - {kw}: {score['total_score']} 点 (content: {score['content_freq']}, visual: {score['visual_freq']})")

# =====================================
# Step 6: レポート生成
# =====================================
print("\n[Step 6] レポート生成中...")

report = {
    "metadata": {
        "validation_timestamp": datetime.now().isoformat(),
        "lecture_id": LECTURE_ID,
        "core_json": str(CORE_JSON_PATH),
        "sidecar_db": str(SIDECAR_DB_PATH)
    },
    "data_summary": {
        "total_elements": len(center_pins),
        "total_records": len(records),
        "content_text_length": len(content_text),
        "visual_text_length": len(visual_text_combined)
    },
    "keyword_extraction": {
        "janome_keywords_count": len(keywords_nlp) if keywords_nlp else 0,
        "regex_keywords_count": len(keywords_regex) if keywords_regex else 0,
        "keywords_extracted": keywords_nlp if keywords_nlp else keywords_regex
    },
    "quality_assessment": {
        "total_evaluated": len(quality_scores),
        "high_quality_count": len(high_quality_keywords),
        "high_quality_keywords": {
            kw: score for kw, score in sorted(
                high_quality_keywords.items(),
                key=lambda x: x[1]["total_score"],
                reverse=True
            )[:20]
        },
        "average_quality_score": round(
            sum(s["total_score"] for s in quality_scores.values()) / len(quality_scores),
            2
        ) if quality_scores else 0
    }
}

# JSON レポート保存
report_json_path = OUTPUT_DIR / "phase2_1_quality_report_fixed.json"
with open(report_json_path, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"✅ JSON レポート保存: {report_json_path}")

# CSV レポート保存
csv_path = OUTPUT_DIR / "keyword_quality_scores_fixed.csv"
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "keyword", "total_score", "visual_freq", "content_freq", "segment_count",
        "visual_freq_score", "content_freq_score", "dispersion_score",
        "noise_score", "trust_score", "avg_visual_confidence", "quality_level"
    ])
    
    for kw, score in sorted(quality_scores.items(), key=lambda x: x[1]["total_score"], reverse=True):
        quality_level = "🟢 HIGH" if score["total_score"] >= 70 else "🟡 MEDIUM" if score["total_score"] >= 50 else "🔴 LOW"
        writer.writerow([
            kw,
            score["total_score"],
            score["visual_freq"],
            score["content_freq"],
            score["segment_count"],
            score["visual_freq_score"],
            score["content_freq_score"],
            score["dispersion_score"],
            score["noise_score"],
            score["trust_score"],
            score["avg_visual_confidence"],
            quality_level
        ])

print(f"✅ CSV レポート保存: {csv_path}")

# =====================================
# 最終サマリー
# =====================================
print("\n" + "=" * 80)
print("✅ Phase 2.1 品質検証完了（修正版）")
print("=" * 80)

summary = f"""
📊 検証結果:
  - 要素数: {report['data_summary']['total_elements']}
  - レコード数: {report['data_summary']['total_records']}
  - Content テキスト: {report['data_summary']['content_text_length']} 文字
  - Visual text: {report['data_summary']['visual_text_length']} 文字
  
🔍 キーワード抽出:
  - JANOME: {report['keyword_extraction']['janome_keywords_count']} 個
  - 正規表現: {report['keyword_extraction']['regex_keywords_count']} 個
  - 高品質キーワード: {report['quality_assessment']['high_quality_count']} 個
  - 平均品質スコア: {report['quality_assessment']['average_quality_score']}/100

📁 出力ファイル:
  - JSON: {report_json_path}
  - CSV: {csv_path}

✨ 次のステップ:
  1. CSV で高品質キーワードを確認
  2. Phase 2.2 へ進行（YouTube Analytics API 統合）
"""

print(summary)
