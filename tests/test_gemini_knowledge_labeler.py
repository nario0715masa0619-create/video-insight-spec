# -*- coding: utf-8 -*-
"""
Phase 3: Tests for GeminiKnowledgeLabeler
"""

import pytest, json, os
from unittest.mock import Mock, patch, MagicMock
from converter.gemini_knowledge_expander import GeminiKnowledgeLabeler

@pytest.fixture
def sample_center_pin():
    return {
        "element_id": "BRAIN_CENTERPIN_001",
        "type": "FACT",
        "content": "量産思考",
        "base_purity_score": 90.0,
        "occurrence_count": 3,
        "importance_score": 3.0
    }

@pytest.fixture
def sample_insight_spec():
    return {
        "video_meta": {
            "video_id": "b8u2CQLQBVU",
            "title": "Lecture 01"
        },
        "knowledge_core": {
            "center_pins": [
                {"element_id": "PIN_001", "type": "FACT", "content": "概念A", "importance_score": 5.0},
                {"element_id": "PIN_002", "type": "LOGIC", "content": "概念B", "importance_score": 4.0},
                {"element_id": "PIN_003", "type": "SOP", "content": "概念C", "importance_score": 3.0},
                {"element_id": "PIN_004", "type": "CASE", "content": "概念D", "importance_score": 2.0},
                {"element_id": "PIN_005", "type": "FACT", "content": "概念E", "importance_score": 1.0},
            ]
        }
    }

@pytest.fixture
def mock_labeler(monkeypatch):
    with patch("converter.gemini_knowledge_expander.genai"):
        labeler = GeminiKnowledgeLabeler(api_key="test_key")
        labeler.gen_model = Mock()
        yield labeler

class TestGeminiKnowledgeLabeler:
    
    def test_init_with_api_key(self, monkeypatch):
        """API キーが設定されている場合の初期化"""
        with patch("converter.gemini_knowledge_expander.genai"):
            labeler = GeminiKnowledgeLabeler(api_key="test_key")
            assert labeler.api_key == "test_key"
            assert labeler.model_id == "gemini-3-pro-preview"
    
    def test_init_without_api_key(self, monkeypatch):
        """API キーが設定されていない場合はエラー"""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with patch("converter.gemini_knowledge_expander.genai"):
            with pytest.raises(ValueError):
                GeminiKnowledgeLabeler(api_key=None)
    
    def test_build_labeling_prompt_without_visual_text(self, mock_labeler, sample_center_pin):
        """visual_text なしのプロンプト構築"""
        prompt = mock_labeler._build_labeling_prompt(sample_center_pin, visual_text_excerpt=None)
        assert "量産思考" in prompt
        assert "business_theme" in prompt
        assert "funnel_stage" in prompt
        assert "difficulty" in prompt
        assert "JSON" in prompt
    
    def test_build_labeling_prompt_with_visual_text(self, mock_labeler, sample_center_pin):
        """visual_text ありのプロンプト構築"""
        visual_text = "量産思考とは、完璧を目指さず高速で市場投入する考え方"
        prompt = mock_labeler._build_labeling_prompt(sample_center_pin, visual_text_excerpt=visual_text)
        assert "量産思考" in prompt
        assert "参考情報" in prompt
        assert visual_text in prompt
    
    def test_validate_labels_valid(self, mock_labeler):
        """有効なラベルの検証"""
        labels = {
            "business_theme": ["マーケティング", "スケール戦略"],
            "funnel_stage": "教育",
            "difficulty": "intermediate"
        }
        assert mock_labeler._validate_labels(labels) is True
    
    def test_validate_labels_invalid_business_theme_count(self, mock_labeler):
        """business_theme が 4 個以上の場合は無効"""
        labels = {
            "business_theme": ["A", "B", "C", "D"],
            "funnel_stage": "教育",
            "difficulty": "intermediate"
        }
        assert mock_labeler._validate_labels(labels) is False
    
    def test_validate_labels_invalid_difficulty(self, mock_labeler):
        """difficulty が有効値でない場合は無効"""
        labels = {
            "business_theme": ["マーケティング"],
            "funnel_stage": "教育",
            "difficulty": "expert"
        }
        assert mock_labeler._validate_labels(labels) is False
    
    def test_label_center_pin_success(self, mock_labeler, sample_center_pin):
        """中心ピンのラベル付与成功"""
        expected_response = {
            "labels": {
                "business_theme": ["マーケティング"],
                "funnel_stage": "教育",
                "difficulty": "intermediate"
            }
        }
        mock_labeler.gen_model.generate_content.return_value = Mock(text=json.dumps(expected_response))
        
        result = mock_labeler.label_center_pin(sample_center_pin)
        
        assert "labels" in result
        assert result["labels"]["business_theme"] == ["マーケティング"]
        assert result["labels"]["funnel_stage"] == "教育"
        assert result["labels"]["difficulty"] == "intermediate"
    
    def test_label_center_pin_json_parse_error(self, mock_labeler, sample_center_pin):
        """JSON パースエラーの場合、元の pin を返す"""
        mock_labeler.gen_model.generate_content.return_value = Mock(text="invalid json")
        
        result = mock_labeler.label_center_pin(sample_center_pin)
        
        assert result == sample_center_pin
        assert "labels" not in result
    
    def test_label_center_pin_validation_error(self, mock_labeler, sample_center_pin):
        """バリデーションエラーの場合、元の pin を返す"""
        invalid_response = {
            "labels": {
                "business_theme": [],  # 空配列は無効
                "funnel_stage": "教育",
                "difficulty": "intermediate"
            }
        }
        mock_labeler.gen_model.generate_content.return_value = Mock(text=json.dumps(invalid_response))
        
        result = mock_labeler.label_center_pin(sample_center_pin)
        
        assert result == sample_center_pin
        assert "labels" not in result
    
    def test_call_gemini_with_retry_success(self, mock_labeler):
        """API 呼び出し成功"""
        response_text = '{"labels": {"business_theme": ["A"], "funnel_stage": "教育", "difficulty": "beginner"}}'
        mock_labeler.gen_model.generate_content.return_value = Mock(text=response_text)
        
        result = mock_labeler._call_gemini_with_retry("test prompt")
        
        assert result == response_text
    
    def test_call_gemini_with_retry_failure(self, mock_labeler):
        """API 呼び出し失敗（最大リトライ超過）"""
        mock_labeler.gen_model.generate_content.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            mock_labeler._call_gemini_with_retry("test prompt", max_retries=1)
    
    def test_label_insight_spec(self, mock_labeler, sample_insight_spec, tmp_path):
        """insight_spec のラベル付与（TOP N）"""
        # テンポラリファイルに JSON を保存
        input_file = tmp_path / "insight_spec_01.json"
        input_file.write_text(json.dumps(sample_insight_spec), encoding='utf-8')
        
        # Gemini の返答をモック
        expected_response = {
            "labels": {
                "business_theme": ["マーケティング"],
                "funnel_stage": "教育",
                "difficulty": "intermediate"
            }
        }
        mock_labeler.gen_model.generate_content.return_value = Mock(text=json.dumps(expected_response))
        
        # ラベル付与処理（TOP 2）
        result = mock_labeler.label_insight_spec(str(input_file), top_n=2)
        
        # TOP 2 のピンにはラベルが付いているはず
        assert "labels" in result["knowledge_core"]["center_pins"][0]
        assert "labels" in result["knowledge_core"]["center_pins"][1]
        # TOP 2 外のピンにはラベルがない
        assert "labels" not in result["knowledge_core"]["center_pins"][2]
    
    def test_label_insight_spec_invalid_structure(self, mock_labeler, tmp_path):
        """不正な JSON 構造の場合はエラー"""
        invalid_spec = {"invalid": "structure"}
        input_file = tmp_path / "invalid.json"
        input_file.write_text(json.dumps(invalid_spec), encoding='utf-8')
        
        with pytest.raises(ValueError):
            mock_labeler.label_insight_spec(str(input_file))
    
    def test_save_insight_spec(self, mock_labeler, sample_insight_spec, tmp_path):
        """ラベル付与済み JSON の保存"""
        output_file = tmp_path / "insight_spec_labeled.json"
        
        result = mock_labeler.save_insight_spec(sample_insight_spec, str(output_file))
        
        assert result is True
        assert output_file.exists()
        
        # 保存内容を確認
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == sample_insight_spec
