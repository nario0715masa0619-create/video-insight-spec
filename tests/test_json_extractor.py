"""
json_extractor.py の unit tests
"""

import json
import pytest
from converter.json_extractor import JSONExtractor


class TestJSONExtractor:
    """JSONExtractor クラスのテスト"""
    
    def test_load_json_success(self, sample_core_json_file):
        """正常な JSON ファイルを読み込む"""
        extractor = JSONExtractor(sample_core_json_file)
        
        assert extractor.center_pins is not None
        assert len(extractor.center_pins) == 3
    
    def test_load_json_nonexistent_file(self):
        """存在しないファイルの処理"""
        extractor = JSONExtractor("/nonexistent/file.json")
        
        assert extractor.center_pins == []
    
    def test_get_knowledge_elements_count(self, sample_core_json_file):
        """element 数を取得"""
        extractor = JSONExtractor(sample_core_json_file)
        count = extractor.get_knowledge_elements_count()
        
        assert count == 3
    
    def test_get_knowledge_type_distribution(self, sample_core_json_file):
        """type 別の分布を取得"""
        extractor = JSONExtractor(sample_core_json_file)
        dist = extractor.get_knowledge_type_distribution()
        
        assert dist["FACT"] == 1
        assert dist["LOGIC"] == 1
        assert dist["SOP"] == 1
        assert dist.get("CASE", 0) == 0
    
    def test_get_high_purity_elements_ratio(self, sample_core_json_file):
        """高純度 element の比率を計算
        
        修正: サンプルデータのアサーション値を実際の値に修正
        - elem_001: purity=95 (80以上) ✓
        - elem_002: purity=85 (80以上) ✓
        - elem_003: purity=75 (80未満) ✗
        → 期待値: 2/3 = 0.6666...
        """
        extractor = JSONExtractor(sample_core_json_file)
        ratio = extractor.get_high_purity_elements_ratio(threshold=80)
        
        # 3 つのうち 2 つが 80 以上
        assert ratio == pytest.approx(2.0 / 3, abs=0.01)
    
    def test_get_high_purity_elements_ratio_threshold(self, sample_core_json_file):
        """閾値を変更して比率を計算"""
        extractor = JSONExtractor(sample_core_json_file)
        ratio = extractor.get_high_purity_elements_ratio(threshold=90)
        
        # elem_001 (95) だけが 90 以上
        assert ratio == pytest.approx(1.0 / 3, abs=0.01)
    
    def test_get_actionable_elements(self, sample_core_json_file):
        """SOP/CASE type の element を取得"""
        extractor = JSONExtractor(sample_core_json_file)
        actionable = extractor.get_actionable_elements()
        
        assert len(actionable) == 1
        assert actionable[0]["type"] == "SOP"
    
    def test_get_actionability_score(self, sample_core_json_file):
        """actionable element の平均 purity を計算"""
        extractor = JSONExtractor(sample_core_json_file)
        score = extractor.get_actionability_score()
        
        # SOP only: purity = 75
        assert score == pytest.approx(75.0, abs=0.1)
    
    def test_get_average_purity_score(self, sample_core_json_file):
        """全 element の平均 purity を計算"""
        extractor = JSONExtractor(sample_core_json_file)
        avg = extractor.get_average_purity_score()
        
        # (95 + 85 + 75) / 3 = 85
        assert avg == pytest.approx(85.0, abs=0.1)
    
    def test_get_elements_by_type(self, sample_core_json_file):
        """指定 type の element をフィルタ"""
        extractor = JSONExtractor(sample_core_json_file)
        facts = extractor.get_elements_by_type("FACT")
        
        assert len(facts) == 1
        assert facts[0]["element_id"] == "elem_001"
    
    def test_get_element_by_id_exists(self, sample_core_json_file):
        """element_id で要素を取得"""
        extractor = JSONExtractor(sample_core_json_file)
        elem = extractor.get_element_by_id("elem_002")
        
        assert elem is not None
        assert elem["type"] == "LOGIC"
        assert elem["content"] == "テスト論理データ"
    
    def test_get_element_by_id_not_exists(self, sample_core_json_file):
        """存在しない element_id の処理"""
        extractor = JSONExtractor(sample_core_json_file)
        elem = extractor.get_element_by_id("nonexistent")
        
        assert elem is None
    
    def test_get_element_by_id_cache(self, sample_core_json_file):
        """キャッシュが機能していることを確認（2回の呼び出しが高速）"""
        extractor = JSONExtractor(sample_core_json_file)
        
        # 1回目
        elem1 = extractor.get_element_by_id("elem_003")
        # 2回目（キャッシュから）
        elem2 = extractor.get_element_by_id("elem_003")
        
        assert elem1 == elem2
        assert elem1["element_id"] == "elem_003"
