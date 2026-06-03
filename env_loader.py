import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    r"""
    環境変数/secretsを以下の順序で読み込む。
    1. OS 環境変数 (既に設定されている場合は上書きしない)
    2. %USERPROFILE%\.video-insight-spec\.env (ユーザーホームの正本)
    3. ./.env (リポジトリ直下のフォールバック)
    """
    # OS環境変数は load_dotenv 実行時にデフォルトで上書きされない(override=False)

    # 1. ユーザーホームの正本 .env を読み込む
    user_home_env = Path.home() / ".video-insight-spec" / ".env"
    if user_home_env.exists():
        load_dotenv(dotenv_path=user_home_env)

    # 2. リポジトリ直下のフォールバック .env を読み込む
    repo_root_env = Path(__file__).resolve().parent / ".env"
    if repo_root_env.exists():
        load_dotenv(dotenv_path=repo_root_env)

# モジュールインポート時に自動的に環境変数を読み込む（任意だが明示的に呼ぶ方針の場合は削除）
# 今回は既存コードの置換のため、load_env() を提供するだけにして各所で明示的に呼び出す。
