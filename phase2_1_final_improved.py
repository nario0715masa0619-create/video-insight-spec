"""
Phase 2.1 最終改善版
- content フィールドのみを使用（OCR ノイズ完全排除）
- JANOME による高品質キーワード抽出
- 強化された stopwords フィルタ
- 実データベースの検証
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime

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
print("🎯 Phase 2.1 最終改善版（content ベース）")
print("=" * 80)

# =====================================
# Step 1: データ読み込み
# =====================================
print("\n[Step 1] データを読み込み中...")

sys.path.insert(0, str(REPO_ROOT))

from converter.json_extractor import JSONExtractor
from converter.db_helper import SidecarDBHelper

# Core JSON を読み込み
with open(CORE_JSON_PATH, "r", encoding="utf-8") as f:
    center_pins = json.load(f)

# Sidecar DB を読み込み
records = SidecarDBHelper.load_evidence_index(str(SIDECAR_DB_PATH))

print(f"✅ 要素数: {len(center_pins)}")
print(f"✅ レコード数: {len(records)}")

# =====================================
# Step 2: content テキストを抽出
# =====================================
print("\n[Step 2] content テキストを抽出中...")

content_texts = [pin["content"] for pin in center_pins]
full_content = " ".join(content_texts)

print(f"✅ 合計テキスト長: {len(full_content)} 文字")
print(f"✅ 最初の 100 文字: {full_content[:100]}...")

# =====================================
# Step 3: JANOME でキーワード抽出
# =====================================
print("\n[Step 3] JANOME でキーワード抽出中...")

try:
    from janome.tokenizer import Tokenizer
    tokenizer = Tokenizer()
    
    # 強化された stopwords
    stopwords = {
        # 日本語汎用
        "が", "を", "に", "は", "の", "で", "と", "も", "から", "まで",
        "など", "および", "または", "ため", "こと", "もの", "ある", "いる",
        "する", "なる", "いく", "くる", "おく", "しまう", "みる", "やる",
        
        # 英語汎用
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "of", "by", "for", "with", "from", "is", "are", "be", "have",
        "do", "does", "did", "will", "would", "could", "should",
        
        # 数字・記号系（除外対象）
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "10", "100", "1000", "万", "円", "年", "月", "日",
    }
    
    keywords = set()
    
    for token in tokenizer.tokenize(full_content):
        word = token.surface
        pos = token.part_of_speech[0]
        
        # 名詞、動詞、形容詞のみ抽出
        if pos in ("名詞", "動詞", "形容詞"):
            # 長さチェック（1文字除外）
            if len(word) >= 2:
                # stopwords チェック
                if word not in stopwords and word.lower() not in stopwords:
                    keywords.add(word)
    
    keywords_list = sorted(list(keywords))
    
    print(f"✅ 抽出キーワード数: {len(keywords_list)}")
    print(f"✅ 例: {keywords_list[:20]}")
    
except ImportError:
    print("❌ JANOME が見つかりません")
    sys.exit(1)
except Exception as e:
    print(f"❌ エラー: {e}")
    sys.exit(1)

# =====================================
# Step 4: キーワード品質評価（改善版）
# =====================================
print("\n[Step 4] キーワード品質を評価中...")

quality_scores = {}

for keyword in keywords_list:
    # 1. content での出現回数
    content_freq = full_content.count(keyword)
    content_score = min(content_freq * 20, 50)  # max 50
    
    # 2. 複数の要素に出現するか
    element_count = sum(1 for pin in center_pins if keyword in pin["content"])
    element_score = min(element_count * 15, 30)  # max 30
    
    # 3. 信頼度（要素の平均 purity）
    purity_scores = [pin["base_purity_score"] for pin in center_pins if keyword in pin["content"]]
    avg_purity = sum(purity_scores) / len(purity_scores) if purity_scores else 0
    trust_score = (avg_purity / 100) * 20  # max 20
    
    total_score = min(100, content_score + element_score + trust_score)
    
    quality_scores[keyword] = {
        "total_score": round(total_score, 2),
        "content_frequency": content_freq,
        "element_count": element_count,
        "average_purity": round(avg_purity, 2),
        "content_score": round(content_score, 2),
        "element_score": round(element_score, 2),
        "trust_score": round(trust_score, 2)
    }

# 高品質キーワード（スコア >= 70）
high_quality = {kw: score for kw, score in quality_scores.items() if score["total_score"] >= 70}

print(f"✅ 高品質キーワード（スコア >= 70）: {len(high_quality)} 個")
print("\n   上位 15 個:")
for kw, score in sorted(high_quality.items(), key=lambda x: x[1]["total_score"], reverse=True)[:15]:
    print(f"   [{score['total_score']:6.2f}] {kw} (出現: {score['content_frequency']}回, 要素: {score['element_count']}個, 純度: {score['average_purity']})")

# =====================================
# Step 5: レポート生成
# =====================================
print("\n[Step 5] レポート生成中...")

report = {
    "metadata": {
        "validation_timestamp": datetime.now().isoformat(),
        "lecture_id": LECTURE_ID,
        "method": "JANOME (content-only, OCR noise eliminated)",
        "core_json": str(CORE_JSON_PATH),
        "sidecar_db": str(SIDECAR_DB_PATH)
    },
    "data_summary": {
        "total_elements": len(center_pins),
        "total_records": len(records),
        "content_text_length": len(full_content)
    },
    "keyword_extraction": {
        "total_keywords": len(keywords_list),
        "high_quality_count": len(high_quality),
        "keywords": keywords_list
    },
    "quality_assessment": {
        "high_quality_keywords": {
            kw: score for kw, score in sorted(
                high_quality.items(),
                key=lambda x: x[1]["total_score"],
                reverse=True
            )
        },
        "average_quality_score": round(
            sum(s["total_score"] for s in quality_scores.values()) / len(quality_scores),
            2
        ) if quality_scores else 0,
        "distribution": {
            "90_100": len([s for s in quality_scores.values() if s["total_score"] >= 90]),
            "80_89": len([s for s in quality_scores.values() if 80 <= s["total_score"] < 90]),
            "70_79": len([s for s in quality_scores.values() if 70 <= s["total_score"] < 80]),
            "60_69": len([s for s in quality_scores.values() if 60 <= s["total_score"] < 70]),
            "below_60": len([s for s in quality_scores.values() if s["total_score"] < 60])
        }
    }
}

# JSON レポート保存
report_json_path = OUTPUT_DIR / "phase2_1_final_report.json"
with open(report_json_path, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"✅ JSON レポート保存: {report_json_path}")

# CSV レポート保存
csv_path = OUTPUT_DIR / "keyword_quality_final.csv"
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "keyword", "total_score", "content_frequency", "element_count",
        "average_purity", "content_score", "element_score", "trust_score", "quality_level"
    ])
    
    for kw, score in sorted(quality_scores.items(), key=lambda x: x[1]["total_score"], reverse=True):
        quality_level = "🟢 HIGH" if score["total_score"] >= 70 else "🟡 MEDIUM" if score["total_score"] >= 50 else "🔴 LOW"
        writer.writerow([
            kw,
            score["total_score"],
            score["content_frequency"],
            score["element_count"],
            score["average_purity"],
            score["content_score"],
            score["element_score"],
            score["trust_score"],
            quality_level
        ])

print(f"✅ CSV レポート保存: {csv_path}")

# =====================================
# 最終サマリー
# =====================================
print("\n" + "=" * 80)
print("✅ Phase 2.1 最終改善版 完了")
print("=" * 80)

summary = f"""
🎯 検証結果:
  - 要素数: {report['data_summary']['total_elements']}
  - テキスト長: {report['data_summary']['content_text_length']} 文字
  - 抽出キーワード: {report['keyword_extraction']['total_keywords']} 個
  - 高品質キーワード: {report['keyword_extraction']['high_quality_count']} 個
  - 平均品質スコア: {report['quality_assessment']['average_quality_score']}/100

📊 品質分布:
  - 優秀（90-100）: {report['quality_assessment']['distribution']['90_100']} 個
  - 良好（80-89）: {report['quality_assessment']['distribution']['80_89']} 個
  - 合格（70-79）: {report['quality_assessment']['distribution']['70_79']} 個
  - 要改善（60-69）: {report['quality_assessment']['distribution']['60_69']} 個
  - 不合格（<60）: {report['quality_assessment']['distribution']['below_60']} 個

✨ 改善点:
  ✅ OCR ノイズを完全排除（content のみ使用）
  ✅ JANOME で形態素解析（精度向上）
  ✅ 強化された stopwords フィルタ
  ✅ 要素の純度スコアを品質計算に反映

📁 出力ファイル:
  - JSON: {report_json_path}
  - CSV: {csv_path}

🚀 次のステップ:
  1. CSV で高品質キーワードを確認
  2. Phase 2.2（YouTube Analytics API）へ進行
"""

print(summary)
