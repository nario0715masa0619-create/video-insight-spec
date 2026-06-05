import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.env_loader import ensure_env_loaded
ensure_env_loaded()

import os
import sys
import io
from pathlib import Path

# Windows での cp932 エラー回避
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# リポジトリルートを sys.path に追加して env_loader を読み込む
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from env_loader import load_env

def check_env():
    print("="*50)
    print(" 環境変数チェック")
    print("="*50)

    # load_env で読み込み
    load_env()

    # 正本とフォールバックの確認
    user_home_env = Path.home() / ".video-insight-spec" / ".env"
    repo_root_env = repo_root / ".env"

    print("\n[設定ファイル状態]")
    if user_home_env.exists():
        print(f"✅ 正本ファイルが見つかりました: {user_home_env}")
    else:
        print(f"❌ 正本ファイルが見つかりません: {user_home_env}")
        print("   -> bootstrap_user_env.ps1 を実行して作成してください。")

    if repo_root_env.exists():
        print(f"ℹ️ フォールバックファイルが存在します: {repo_root_env}")
    else:
        print(f"ℹ️ フォールバックファイルはありません（推奨）: {repo_root_env}")

    # チェック対象のキー
    keys = {
        "Secrets (API Keys)": [
            "OPENAI_API_KEY",
            "YOUTUBE_API_KEY",
            "GEMINI_API_KEY"
        ],
        "Configuration": [
            "VIDEOS_INPUT_DIR",
            "TEMP_DIR",
            "ARCHIVE_OUTPUT_DIR",
            "LOGS_DIR",
            "GEMINI_MODEL_ID",
            "WHISPER_MODEL_SIZE",
            "WHISPER_DEVICE",
            "EASYOCR_GPU",
            "EASYOCR_LANGUAGES",
            "FRAMES_PER_MINUTE",
            "FFMPEG_PATH"
        ]
    }

    missing_secrets = False
    print("\n[環境変数の状態]")
    for group_name, group_keys in keys.items():
        print(f"\n--- {group_name} ---")
        for k in group_keys:
            val = os.getenv(k)
            if val:
                # Secret の場合はマスクして表示
                if "API_KEY" in k:
                    masked = val[:4] + "*" * (len(val)-8) + val[-4:] if len(val) > 8 else "***"
                    print(f"✅ {k}: {masked}")
                else:
                    print(f"✅ {k}: {val}")
            else:
                if "API_KEY" in k:
                    print(f"❌ {k}: 未設定")
                    missing_secrets = True
                else:
                    print(f"⚠️ {k}: 未設定（デフォルト値が使用されるかエラーになります）")

    if missing_secrets:
        print("\n⚠️ APIキーが未設定のものがあります。Streamlit は劣化モードで起動し、一部バッチ処理は失敗する可能性があります。")
    else:
        print("\n✅ すべての API キーが設定されています！")

if __name__ == "__main__":
    check_env()
