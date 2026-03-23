"""
pytest の共有フィクスチャを定義。
lecture_id 01 の実データとダミーデータを管理。
"""

import os
import json
import sqlite3
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import pytest
import sys
from pathlib import Path

# リポジトリルートを PYTHONPATH に追加
sys.path.insert(0, str(Path(__file__).parent.parent))


# .env.test を読み込み
load_dotenv("tests/.env.test")

# テスト用の基本定数
TEST_LECTURE_ID = "01"
REAL_CORE_JSON_PATH = os.getenv("REAL_CORE_JSON_PATH")
REAL_SIDECAR_DB_PATH = os.getenv("REAL_SIDECAR_DB_PATH")
TEST_OUTPUT_DIR = os.getenv("TEST_OUTPUT_DIR", "./test_output")


@pytest.fixture(scope="session")
def test_output_dir():
    """テスト出力用のディレクトリを作成・提供"""
    output_path = Path(TEST_OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    yield str(output_path)


@pytest.fixture(scope="session")
def real_core_json_path():
    """実データの Mk2_Core_XX.json パス"""
    if not os.path.exists(REAL_CORE_JSON_PATH):
        pytest.skip(f"Real core JSON not found: {REAL_CORE_JSON_PATH}")
    return REAL_CORE_JSON_PATH


@pytest.fixture(scope="session")
def real_sidecar_db_path():
    """実データの Mk2_Sidecar_XX.db パス"""
    if not os.path.exists(REAL_SIDECAR_DB_PATH):
        pytest.skip(f"Real sidecar DB not found: {REAL_SIDECAR_DB_PATH}")
    return REAL_SIDECAR_DB_PATH


@pytest.fixture
def sample_core_json_data():
    """最小構成のダミー Mk2_Core_XX.json データ"""
    return {
        "center_pins": [
            {
                "element_id": "elem_001",
                "type": "FACT",
                "content": "テスト事実データ",
                "base_purity_score": 95
            },
            {
                "element_id": "elem_002",
                "type": "LOGIC",
                "content": "テスト論理データ",
                "base_purity_score": 85
            },
            {
                "element_id": "elem_003",
                "type": "SOP",
                "content": "テストSOPデータ",
                "base_purity_score": 75
            }
        ]
    }


@pytest.fixture
def sample_core_json_file(tmp_path, sample_core_json_data):
    """ダミー JSON ファイルを tmp_path に作成して提供"""
    json_file = tmp_path / "Mk2_Core_test.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_core_json_data, f, ensure_ascii=False, indent=2)
    return str(json_file)



import sqlite3


import sqlite3


import sqlite3

@pytest.fixture
def sample_sidecar_db_file(tmp_path):
    """Sidecar DB with evidence_index table"""
    db_file = tmp_path / "Mk2_Sidecar_test.db"
    conn = sqlite3.connect(str(db_file))
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
    
    test_data = [
        ("elem_001", 0, 5000, "テスト1", 0.95, "path/to/video1.mp4"),
        ("elem_002", 5000, 10000, "テスト2", 0.90, "path/to/video2.mp4"),
        ("elem_003", 10000, 15000, "テスト3", 0.85, "path/to/video3.mp4"),
    ]
    
    for data in test_data:
        cursor.execute("""
            INSERT INTO evidence_index 
            (element_id, start_ms, end_ms, visual_text, visual_score, source_video_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
    
    conn.commit()
    conn.close()
    
    yield str(db_file)
    if db_file.exists():
        db_file.unlink()

@pytest.fixture
def temp_output_file(tmp_path):
    """テスト出力用の一時ファイルパスを提供"""
    return str(tmp_path / "output_insight_spec.json")


@pytest.fixture
def lecture_id():
    """テスト用 lecture_id"""
    return TEST_LECTURE_ID

import pytest
import sqlite3

@pytest.fixture
def sidecar_db():
    """一時 evidence_index テーブルを作成"""
    db_path = ":memory:"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE evidence_index (
            element_id TEXT PRIMARY KEY,
            start_ms INTEGER,
            end_ms INTEGER,
            visual_text TEXT,
            visual_score REAL,
            source_video_path TEXT
        )
    """)
    conn.execute("INSERT INTO evidence_index VALUES (?, ?, ?, ?, ?, ?)",
                 ("BRAIN_CENTERPIN_001", 0, 4920, "Sample visual text", 0.9, "path/to/video.mp4"))
    conn.commit()
    yield conn
    conn.close()
