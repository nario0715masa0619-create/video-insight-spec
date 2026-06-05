import os
from pathlib import Path
from dotenv import load_dotenv


def ensure_env_loaded():
    """環境変数をロード"""
    user_env = Path.home() / ".video-insight-spec" / ".env"
    project_env = Path(__file__).parent.parent / ".env"
    if user_env.exists():
        load_dotenv(user_env, override=False)
    if project_env.exists():
        load_dotenv(project_env, override=False)


def get_required_env(key_name):
    """必須環境変数を取得"""
    value = os.getenv(key_name)
    if value is None:
        raise EnvironmentError(
            f"'{key_name}' が未設定です"
        )
    return value


def get_optional_env(key_name, default=None):
    """オプション環境変数を取得"""
    return os.getenv(key_name, default)

def is_demo_mode() -> bool:
    """
    デモモード判定: API キーが不足している場合、または明示的に指定された場合
    """
    has_youtube = os.getenv("YOUTUBE_API_KEY")
    has_gemini = os.getenv("GEMINI_API_KEY")
    has_demo_flag = os.getenv("DEMO_MODE") == "1"
    
    return has_demo_flag or (not has_youtube and not has_gemini)
