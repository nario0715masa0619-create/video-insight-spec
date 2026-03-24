import sqlite3
import pathlib

db_path = pathlib.Path('D:/Knowledge_Base/Brain_Marketing/archive/Mk2_Sidecar_01.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# テーブルスキーマを確認
cursor.execute("PRAGMA table_info(evidence_index)")
columns = {row[1] for row in cursor.fetchall()}
print(f"現在のカラム: {columns}")

# カラムがなければ追加
if 'occurrence_count' not in columns:
    cursor.execute("ALTER TABLE evidence_index ADD COLUMN occurrence_count INTEGER DEFAULT 0")
    print("✅ occurrence_count カラム追加")

if 'importance_score' not in columns:
    cursor.execute("ALTER TABLE evidence_index ADD COLUMN importance_score REAL DEFAULT 0.0")
    print("✅ importance_score カラム追加")

conn.commit()
conn.close()
print("✅ スキーマ更新完了")
