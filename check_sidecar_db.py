import sqlite3

db_path = 'D:/Knowledge_Base/Brain_Marketing/archive/Mk2_Sidecar_01.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# テーブル一覧を表示
print('=== テーブル一覧 ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f'  - {table[0]}')

# 各テーブルのカラム情報を表示
print('\n=== カラム情報 ===')
for table in tables:
    table_name = table[0]
    cursor.execute(f'PRAGMA table_info({table_name});')
    columns = cursor.fetchall()
    print(f'\n{table_name}:')
    for col in columns:
        print(f'  - {col[1]} ({col[2]})')

# URL関連データサンプル
print('\n=== evidence_index のサンプルデータ（最初の1件） ===')
cursor.execute('SELECT * FROM evidence_index LIMIT 1;')
sample = cursor.fetchone()
if sample:
    cursor.execute('PRAGMA table_info(evidence_index);')
    cols = cursor.fetchall()
    for i, col in enumerate(cols):
        print(f'{col[1]}: {sample[i]}')

conn.close()
