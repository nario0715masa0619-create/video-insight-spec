import pytest
import sqlite3
import pathlib
import tempfile
from converter.db_cleaner import SidecarDBCleaner


@pytest.fixture
def temp_db():
    """テスト用の一時 DB を作成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = pathlib.Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE evidence_index (
                element_id TEXT PRIMARY KEY,
                start_ms INTEGER,
                end_ms INTEGER,
                visual_text TEXT,
                visual_score REAL,
                source_video_path TEXT
            )
        """)
        
        # テストデータを挿入
        test_data = [
            ("elem_001", 0, 5000, "ウィンドウ zoom チャット Hello World", 0.9, "video.mp4"),
            ("elem_002", 5000, 10000, "アブリを使ってYoutubeで動画を見る", 0.85, "video.mp4"),
        ]
        
        for data in test_data:
            cursor.execute(
                """INSERT INTO evidence_index 
                   (element_id, start_ms, end_ms, visual_text, visual_score, source_video_path)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                data
            )
        
        conn.commit()
        conn.close()
        
        yield db_path


def test_clean_db(temp_db):
    """DB クリーニングの動作確認"""
    stats = SidecarDBCleaner.clean_db(str(temp_db), backup=False)
    
    assert stats["total_records"] == 2
    assert stats["cleaned_records"] == 2
    assert stats["avg_reduction_ratio"] > 0
    
    # クリーニング後の内容を確認
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT visual_text FROM evidence_index WHERE element_id = 'elem_001'")
    cleaned_text = cursor.fetchone()[0]
    
    # UI ノイズが除去されている
    assert "ウィンドウ" not in cleaned_text
    assert "zoom" not in cleaned_text
    assert "Hello World" in cleaned_text
    
    conn.close()


def test_backup_creation(temp_db):
    """バックアップ作成の確認"""
    SidecarDBCleaner.clean_db(str(temp_db), backup=True)
    
    backup_path = temp_db.with_suffix(".db.backup")
    assert backup_path.exists()
