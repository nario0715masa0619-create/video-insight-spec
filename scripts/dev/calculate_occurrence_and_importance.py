import sqlite3
import pathlib
from collections import Counter

db_path = pathlib.Path('D:/Knowledge_Base/Brain_Marketing/archive/Mk2_Sidecar_01.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 1: クリーニング済みの visual_text を全て取得
cursor.execute("""
    SELECT element_id, visual_text
    FROM evidence_index
    WHERE visual_text IS NOT NULL AND visual_text != ''
    ORDER BY element_id
""")
rows = cursor.fetchall()

print(f"処理対象レコード数: {len(rows)}")

# テキストごとに occurrence_count を集計
text_counter = Counter(row[1] for row in rows)

print(f"ユニークなテキスト数: {len(text_counter)}")

# Step 2: 各レコードの occurrence_count と importance_score を更新
for element_id, visual_text in rows:
    occurrence = text_counter[visual_text]
    importance = float(occurrence)  # importance_score = occurrence_count
    
    cursor.execute("""
        UPDATE evidence_index
        SET occurrence_count = ?,
            importance_score = ?
        WHERE element_id = ?
    """, (occurrence, importance, element_id))

conn.commit()

# Step 3: 結果を確認（サンプル）
cursor.execute("""
    SELECT element_id, visual_text, occurrence_count, importance_score
    FROM evidence_index
    WHERE visual_text IS NOT NULL AND visual_text != ''
    ORDER BY importance_score DESC
    LIMIT 10
""")

print("\n=== occurrence_count & importance_score TOP 10 ===")
print(f"{'element_id':<25} {'occurrence_count':<15} {'importance_score':<15} {'visual_text':<50}")
print("-" * 110)

for row in cursor.fetchall():
    element_id, visual_text, occ_count, imp_score = row
    text_display = (visual_text[:45] + '...') if len(visual_text) > 45 else visual_text
    print(f"{element_id:<25} {occ_count:<15} {imp_score:<15.2f} {text_display:<50}")

# 統計情報
cursor.execute("SELECT COUNT(*), AVG(occurrence_count), MAX(occurrence_count) FROM evidence_index WHERE occurrence_count > 0")
count, avg_occ, max_occ = cursor.fetchone()
print(f"\n=== 統計 ===")
print(f"総レコード数（occurrence > 0）: {count}")
print(f"平均 occurrence_count: {avg_occ:.2f}")
print(f"最大 occurrence_count: {max_occ}")

conn.close()
print("\n✅ occurrence_count & importance_score 更新完了")
