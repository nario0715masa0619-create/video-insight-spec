import streamlit as st
import pytest

@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    st.cache_resource.clear()
    st.cache_data.clear()

@pytest.fixture
def sample_complete_insight_spec():
    return {
        "video_meta": {
            "title": "Sample Complete Lecture",
            "url": "https://youtube.com/watch?v=sample",
            "publish_date": "2026-01-01",
            "channel_name": "Test Channel"
        },
        "knowledge_core": {
            "center_pins": [
                {"label": "Concept A", "base_purity_score": 0.9},
                {"label": "Concept B", "base_purity_score": 0.8}
            ]
        },
        "views": {
            "competitive": {
                "metrics": {
                    "view_count": 1000,
                    "like_count": 100,
                    "comment_count": 10
                }
            },
            "self_improvement": {
                "business_theme_distribution": {
                    "Leadership": 50,
                    "Management": 50
                }
            }
        },
        "content_summary": "A complete lecture for testing."
    }

@pytest.fixture
def sample_minimal_insight_spec():
    return {
        "video_meta": {
            "title": "Minimal Lecture"
        },
        "knowledge_core": {
            "center_pins": []
        }
    }

@pytest.fixture
def sample_broken_insight_spec():
    return {
        "knowledge_core": "This should be a dict but it is a string",
        "video_meta": None
    }

@pytest.fixture
def sample_insight_specs_dict(sample_complete_insight_spec, sample_minimal_insight_spec):
    return {
        "01": sample_complete_insight_spec,
        "02": sample_minimal_insight_spec
    }

@pytest.fixture
def sample_empty_dir(tmp_path):
    return tmp_path

@pytest.fixture
def sample_json_files_dir(tmp_path, sample_complete_insight_spec, sample_minimal_insight_spec):
    import json
    file1 = tmp_path / "insight_spec_01.json"
    file2 = tmp_path / "insight_spec_02.json"
    file3 = tmp_path / "insight_spec_invalid.json"
    
    with open(file1, "w", encoding="utf-8") as f:
        json.dump(sample_complete_insight_spec, f)
        
    with open(file2, "w", encoding="utf-8") as f:
        json.dump(sample_minimal_insight_spec, f)
        
    with open(file3, "w", encoding="utf-8") as f:
        f.write("Not a JSON string")
        
    return tmp_path
