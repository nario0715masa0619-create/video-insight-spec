"""
Phase 2.1 最終改善版 v2
- 品詞コードを修正（「名詞」→「名」）
- content フィールドのみを使用
- JANOME による高品質キーワード抽出
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path.cwd()
ARCHIVE_DIR = Path("D:/Knowledge_Base/Brain_Marketing/archive")
OUTPUT_DIR = REPO_ROOT / "quality_validation_results"

LECTURE_ID = "01"
CORE_JSON_PATH = ARCHIVE_DIR / f"Mk2_Core_{LECTURE_ID}.json"

OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("🎯 Phase 2.1 最終改善版 v2（品詞コード修正）")
print("=" * 80)

# =====================================
# Step 1: データ読み込み
# =====================================
print("\n[Step 1] データを読み込み中...")

with open(CORE_JSON_PATH, "r", encoding="utf-8") as f:
    center_pins = json.load(f)

print(f"✅ 要素数: {len(center_pins)}")

# =====================================
# Step 2: content テキストを抽出
# =====================================
print("\n[Step 2] content テキストを抽出中...")

content_texts = [pin["content"] for pin in center_pins]
full_content = " ".join(content_texts)

print(f"✅ 合計テキスト長: {len(full_content)} 文字")

# =====================================
# Step 3: JANOME でキーワード抽出（修正版）
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
        "できる", "いった", "いう", "あった", "あるいは",
        
        # 英語汎用
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "of", "by", "for", "with", "from", "is", "are", "be", "have",
        "do", "does", "did", "will", "would", "could", "should",
        
        # 数字・記号系（除外対象）
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    }
    
    keywords = set()
    all_tokens_debug = []
    
    for token in tokenizer.tokenize(full_content):
        word = token.surface
        pos = token.part_of_speech[0]  # 「名」「動」「形」など
        
        all_tokens_debug.append((word, pos))
        
        # 修正: 品詞コードで判定（「名」「動」「形」）
        if pos in ("名", "動", "形"):
            # 長さチェック（2文字以上）
            if len(word) >= 2:
                # stopwords チェック
                if word not in stopwords and word.lower() not in stopwords:
                    keywords.add(word)
    
    keywords_list = sorted(list(keywords))
    
    print(f"✅ 抽出キーワード数: {len(keywords_list)}")
    print(f"\n   抽出されたキーワード:")
    for kw in keywords_list[:30]:
        print(f"   - {kw}")
    
except ImportError:
    print("❌ JANOME が見つかりません")
    sys.exit(1)
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =====================================
# Step 4: キーワード品質評価
# =====================================
print("\n[Step 4] キーワード品質を評価中...")

quality_scores = {}

for keyword in keywords_list:
    # 1. content での出現回数
    content_freq = full_content.count(keyword)
    content_score = min(content_freq * 20, 50)
    
    # 2. 複数の要素に出現するか
    element_count = sum(1 for pin in center_pins if keyword in pin["content"])
    element_score = min(element_count * 15, 30)
    
    # 3. 信頼度（要素の平均 purity）
    purity_scores = [pin["base_purity_score"] for pin in center_pins if keyword in pin["content"]]
    avg_purity = sum(purity_scores) / len(purity_scores) if purity_scores else 0
    trust_score = (avg_purity / 100) * 20
    
    total_score = min(100, content_score + element_score + trust_score)
    
    quality_scores[keyword] = {
        "total_score": round(total_score, 2),
        "content_frequency": content_freq,
        "element_count": element_count,
        "average_purity": round(avg_purity, 2)
    }

# 高品質キーワード（スコア >= 70）
high_quality = {kw: score for kw, score in quality_scores.items() if score["total_score"] >= 70}

print(f"✅ 高品質キーワード（スコア >= 70）: {len(high_quality)} 個")

if high_quality:
    print("\n   上位キーワード:")
    for kw, score in sorted(high_quality.items(), key=lambda x: x[1]["total_score"], reverse=True)[:15]:
        print(f"   [{score['total_score']:6.2f}] {kw} (出現: {score['content_frequency']}回, 要素: {score['element_count']}個)")
else:
    print("\n   ⚠️ 高品質キーワードがありません")

# =====================================
# Step 5: レポート生成
# =====================================
print("\n[Step 5] レポート生成中...")

report = {
    "metadata": {
        "validation_timestamp": datetime.now().isoformat(),
        "lecture_id": LECTURE_ID,
        "method": "JANOME (content-only, fixed POS codes)"
    },
    "keyword_extraction": {
        "total_keywords": len(keywords_list),
        "high_quality_count": len(high_quality),
        "keywords": keywords_list
    },
    "quality_assessment": {
        "high_quality_keywords": {
            kw: score for kw, score in sorted(high_quality.items(), key=lambda x: x[1]["total_score"], reverse=True)
        },
        "average_quality_score": round(sum(s["total_score"] for s in quality_scores.values()) / len(quality_scores), 2) if quality_scores else 0
    }
}

report_json_path = OUTPUT_DIR / "phase2_1_final_report_v2.json"
with open(report_json_path, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"✅ JSON レポート保存: {report_json_path}")

csv_path = OUTPUT_DIR / "keyword_quality_final_v2.csv"
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["keyword", "total_score", "content_frequency", "element_count", "average_purity"])
    
    for kw, score in sorted(quality_scores.items(), key=lambda x: x[1]["total_score"], reverse=True):
        writer.writerow([kw, score["total_score"], score["content_frequency"], score["element_count"], score["average_purity"]])

print(f"✅ CSV レポート保存: {csv_path}")

# =====================================
# 最終サマリー
# =====================================
print("\n" + "=" * 80)
print("✅ Phase 2.1 最終改善版 v2 完了")
print("=" * 80)

summary = f"""
🎯 検証結果:
  - 抽出キーワード: {len(keywords_list)} 個
  - 高品質キーワード（スコア >= 70）: {len(high_quality)} 個
  - 平均品質スコア: {report['quality_assessment']['average_quality_score']}/100

📁 出力ファイル:
  - JSON: {report_json_path}
  - CSV: {csv_path}

🚀 次のステップ:
  Phase 2.2（YouTube Analytics API）へ進行準備完了！
"""

print(summary)
