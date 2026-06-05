import os
import pytest
from streamlit_app.env_loader import is_demo_mode

def test_is_demo_mode_no_keys():
    """API キーがない場合、デモモード判定"""
    os.environ.pop("YOUTUBE_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("DEMO_MODE", None)
    assert is_demo_mode() == True

def test_is_demo_mode_with_keys():
    """API キーがある場合、通常モード判定"""
    os.environ["YOUTUBE_API_KEY"] = "test_key"
    os.environ["GEMINI_API_KEY"] = "test_key"
    os.environ.pop("DEMO_MODE", None)
    assert is_demo_mode() == False

def test_is_demo_mode_explicit_flag():
    """DEMO_MODE フラグが指定されている場合"""
    os.environ.pop("YOUTUBE_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ["DEMO_MODE"] = "1"
    assert is_demo_mode() == True

