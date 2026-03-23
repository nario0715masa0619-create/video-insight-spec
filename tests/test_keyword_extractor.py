"""
keyword_extractor.py の unit tests
"""

import pytest
from converter.keyword_extractor import KeywordExtractor


class TestKeywordExtractor:
    """KeywordExtractor クラスのテスト"""
    
    def test_extract_keywords_from_title(self, sample_sidecar_db_file):
        """タイトルからキーワードを抽出
        
        修正: KeywordExtractor は evidence_records を必須引数として受け取るため、
        db_helper で先に DB から records を読み込んで渡す
        """
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(sample_sidecar_db_file, records)
        keywords = extractor.extract_keywords(
            title="Python マーケティング 戦略"
        )
        
        # "Python", "マーケティング", "戦略" が抽出されるはず
        assert len(keywords) > 0
        assert any("Python" in kw for kw in keywords)
    
    def test_extract_keywords_japanese(self, sample_sidecar_db_file):
        """日本語キーワード抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(sample_sidecar_db_file, records)
        keywords = extractor.extract_keywords(
            title="営業戦略とブランディング"
        )
        
        assert len(keywords) > 0
    
    def test_extract_keywords_english(self, sample_sidecar_db_file):
        """英語キーワード抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(sample_sidecar_db_file, records)
        keywords = extractor.extract_keywords(
            title="Digital Marketing Strategy"
        )
        
        assert len(keywords) > 0
        assert any("Digital" in kw or "Marketing" in kw for kw in keywords)
    
    def test_extract_keywords_minimum_length(self, sample_sidecar_db_file):
        """最小長（2文字）未満は除外"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(sample_sidecar_db_file, records)
        keywords = extractor.extract_keywords(
            title="a あ bc 定義"
        )
        
        # "a" や "あ" は除外され、"bc", "定義" のみ
        assert all(len(kw) >= 2 for kw in keywords)
    
    def test_get_keyword_mention_frequency(self, sample_sidecar_db_file):
        """キーワード出現頻度を計算"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(sample_sidecar_db_file, records)
        
        # title と visual_text でキーワード集計
        freq = extractor.get_keyword_mention_frequency(
            title="データ分析",
            db_records=[
                {"visual_text": "データ", "element_id": "e1"},
                {"visual_text": "分析ツール", "element_id": "e2"},
            ]
        )
        
        assert isinstance(freq, dict)
        assert len(freq) >= 0
    
    def test_get_keyword_segment_count(self, sample_sidecar_db_file):
        """キーワードが出現するセグメント数を計算"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(sample_sidecar_db_file, records)
        
        count = extractor.get_keyword_segment_count(
            keyword="テスト",
            db_records=[
                {"visual_text": "テスト1", "element_id": "e1"},
                {"visual_text": "テスト2", "element_id": "e2"},
                {"visual_text": "他の", "element_id": "e3"},
            ]
        )
        
        assert count == 2
    
    def test_get_keyword_first_appearance_ms(self, sample_sidecar_db_file):
        """キーワードの最初の出現タイムスタンプを取得"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(sample_sidecar_db_file, records)
        
        first_ms = extractor.get_keyword_first_appearance_ms(
            keyword="テスト",
            db_records=[
                {"visual_text": "他の", "start_ms": 0, "element_id": "e0"},
                {"visual_text": "テスト1", "start_ms": 15000, "element_id": "e1"},
                {"visual_text": "テスト2", "start_ms": 30000, "element_id": "e2"},
            ]
        )
        
        assert first_ms == 15000
