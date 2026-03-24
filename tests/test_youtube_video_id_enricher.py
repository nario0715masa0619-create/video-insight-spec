"""
YouTube Video ID Enricher テスト
"""

import pytest
import json
import pathlib
from unittest.mock import Mock, patch, MagicMock
from converter.youtube_video_id_enricher import YouTubeVideoIDEnricher


@pytest.fixture
def sample_insight_spec_json(tmp_path):
    """テスト用 insight_spec_XX.json フィクスチャ"""
    json_file = tmp_path / "insight_spec_01.json"
    data = {
        "video_meta": {
            "video_id": "01",
            "channel_id": None,
            "title": "【超重要！】コンテンツ販売必須の基礎知識",
            "url": None,
            "published_at": None
        },
        "knowledge_core": {
            "center_pins": []
        },
        "views": {}
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_file


@pytest.fixture
def enricher():
    """YouTube API キー付き Enricher（モック）"""
    with patch('converter.youtube_video_id_enricher.build'):
        return YouTubeVideoIDEnricher(api_key='test_key')


def test_search_video_by_title(enricher):
    """search_video_by_title メソッドをテスト"""
    with patch.object(enricher, 'youtube') as mock_youtube:
        mock_search = MagicMock()
        mock_youtube.search.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": {"videoId": "test_video_id_123"},
                    "snippet": {"title": "Test Video"}
                }
            ]
        }
        enricher.youtube = mock_youtube
        
        result = enricher.search_video_by_title("Test Video")
        assert result == "test_video_id_123"


def test_search_video_not_found(enricher):
    """動画が見つからない場合をテスト"""
    with patch.object(enricher, 'youtube') as mock_youtube:
        mock_youtube.search.return_value.list.return_value.execute.return_value = {
            "items": []
        }
        enricher.youtube = mock_youtube
        
        result = enricher.search_video_by_title("NonExistent Video")
        assert result is None


def test_enrich_insight_spec_json(enricher, sample_insight_spec_json):
    """JSON ファイルを video_id で補充するテスト"""
    with patch.object(enricher, 'search_video_by_title') as mock_search:
        mock_search.return_value = "enriched_video_id_456"
        
        result = enricher.enrich_insight_spec_json(str(sample_insight_spec_json))
        
        assert result["status"] == "success"
        assert result["video_id"] == "enriched_video_id_456"
        
        # ファイルが更新されたか確認
        with open(sample_insight_spec_json, "r", encoding="utf-8") as f:
            updated_data = json.load(f)
        
        assert updated_data["video_meta"]["video_id"] == "enriched_video_id_456"


def test_enrich_insight_spec_json_already_exists(enricher, sample_insight_spec_json):
    """video_id が既に YouTube ID である場合（lecture_id でない）をテスト"""
    # YouTube video_id に変更（11文字以上または英数混在）
    with open(sample_insight_spec_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["video_meta"]["video_id"] = "dQw4w9WgXcQ"
    with open(sample_insight_spec_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    result = enricher.enrich_insight_spec_json(str(sample_insight_spec_json))
    
    assert result["status"] == "already_exists"
    assert result["video_id"] == "dQw4w9WgXcQ"


def test_search_cache(enricher):
    """キャッシュ機能をテスト"""
    with patch.object(enricher, 'youtube') as mock_youtube:
        mock_youtube.search.return_value.list.return_value.execute.return_value = {
            "items": [{"id": {"videoId": "cached_id"}}]
        }
        enricher.youtube = mock_youtube
        
        # 1回目の検索
        result1 = enricher.search_video_by_title("Test Cache")
        assert result1 == "cached_id"
        
        # 2回目の検索（キャッシュから）
        enricher.youtube.search.reset_mock()
        result2 = enricher.search_video_by_title("Test Cache")
        assert result2 == "cached_id"
        
        # API が呼ばれていないことを確認（キャッシュ使用）
        enricher.youtube.search.assert_not_called()
