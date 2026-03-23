"""
db_helper.py の unit tests
"""

import sqlite3
import pytest
from converter.db_helper import SidecarDBHelper


class TestSidecarDBHelper:
    """SidecarDBHelper クラスのテスト"""
    
    def test_load_evidence_index_success(self, sample_sidecar_db_file):
        """正常な DB ファイルから evidence_index を読み込む"""
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        
        assert len(records) == 3
        assert records[0]["element_id"] == "elem_001"
        assert records[0]["start_ms"] == 0
        assert records[0]["end_ms"] == 10000
        assert records[0]["visual_score"] == 0.95
    
    def test_load_evidence_index_nonexistent_file(self):
        """存在しないファイルの処理"""
        records = SidecarDBHelper.load_evidence_index("/nonexistent/db.db")
        assert records == []
    
    def test_load_evidence_index_ordering(self, sample_sidecar_db_file):
        """start_ms でソートされていることを確認"""
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        
        start_times = [r["start_ms"] for r in records]
        assert start_times == sorted(start_times)
    
    def test_get_timestamp_for_element_exists(self, sample_sidecar_db_file):
        """存在する element_id のタイムスタンプを取得"""
        # Load records first to ensure DB is valid
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        assert len(records) > 0, "DB should have records"
        
        timestamp = SidecarDBHelper.get_timestamp_for_element(
            sample_sidecar_db_file, "elem_001"
        )
        
        assert timestamp is not None
        assert timestamp["start_ms"] == 0
        assert timestamp["end_ms"] == 10000
    
    def test_get_timestamp_for_element_not_exists(self, sample_sidecar_db_file):
        """存在しない element_id の処理"""
        timestamp = SidecarDBHelper.get_timestamp_for_element(
            sample_sidecar_db_file, "nonexistent_elem"
        )
        
        assert timestamp is None
    
    def test_get_visual_text_for_element_exists(self, sample_sidecar_db_file):
        """存在する element_id のvisual_text を取得"""
        visual_text = SidecarDBHelper.get_visual_text_for_element(
            sample_sidecar_db_file, "elem_002"
        )
        
        assert visual_text == "テスト2"
    
    def test_get_visual_text_for_element_not_exists(self, sample_sidecar_db_file):
        """存在しない element_id の処理"""
        visual_text = SidecarDBHelper.get_visual_text_for_element(
            sample_sidecar_db_file, "nonexistent_elem"
        )
        
        assert visual_text is None
    
    def test_get_high_confidence_records(self, sample_sidecar_db_file):
        """visual_score >= threshold のレコードをフィルタ
        
        注: 実装の get_high_confidence_records は threshold をキーワード引数ではなく
        ポジショナル引数で受け取るため、その形式で呼び出し
        """
        records = SidecarDBHelper.get_high_confidence_records(
            sample_sidecar_db_file, 0.80
        )
        
        assert len(records) == 2
        assert all(r["visual_score"] >= 0.80 for r in records)
    
    def test_get_high_confidence_records_empty(self, sample_sidecar_db_file):
        """閾値が高い場合は空の結果"""
        records = SidecarDBHelper.get_high_confidence_records(
            sample_sidecar_db_file, 0.99
        )
        
        assert len(records) == 0
    
    def test_get_coverage_duration(self, sample_sidecar_db_file):
        """総カバレッジ期間（ミリ秒）を計算"""
        duration_ms = SidecarDBHelper.get_coverage_duration(sample_sidecar_db_file)
        
        # 0-10000 + 15000-25000 + 30000-40000 = 10000 + 10000 + 10000 = 30000 ms
        assert duration_ms == 30000
    
    def test_get_coverage_duration_empty_db(self, tmp_path):
        """空の DB の場合は 0 を返す"""
        empty_db = tmp_path / "empty.db"
        conn = sqlite3.connect(str(empty_db))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE evidence_index (
                element_id TEXT,
                start_ms INTEGER,
                end_ms INTEGER,
                visual_text TEXT,
                visual_score REAL,
                source_video_path TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        duration_ms = SidecarDBHelper.get_coverage_duration(str(empty_db))
        assert duration_ms == 0
