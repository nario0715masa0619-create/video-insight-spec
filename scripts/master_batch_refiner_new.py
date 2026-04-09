#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# メイン処理
if __name__ == "__main__":
    # ===== 入力パス処理 =====
    if len(sys.argv) > 1:
        input_arg = sys.argv[1]
        input_path = Path(input_arg).resolve()  # 絶対パスに変換
        
        if not input_path.exists():
            print(f"エラー: パスが存在しません: {input_path}")
            sys.exit(1)
        
        # ディレクトリかファイルかで分岐
        if input_path.is_dir():
            video_files = sorted(input_path.glob("**/*.mp4"))
            video_dir = input_path
        elif input_path.is_file() and input_path.suffix.lower() == ".mp4":
            video_files = [input_path]
            video_dir = input_path.parent
        else:
            print(f"エラー: MP4ファイルではありません: {input_path}")
            sys.exit(1)
    else:
        # デフォルト: VIDEOS_INPUT_DIR を使用
        from dotenv import load_dotenv
        import os
        load_dotenv()
        videos_dir = os.getenv("VIDEOS_INPUT_DIR", r"D:\AI_Data\video-insight-spec\downloaded_videos")
        video_dir = Path(videos_dir).resolve()
        video_files = sorted(video_dir.glob("**/*.mp4"))
    
    # ===== 出力ディレクトリ設定 =====
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    archive_base = Path(os.getenv("ARCHIVE_OUTPUT_DIR", "./archive")).resolve()
    logs_base = Path(os.getenv("LOGS_DIR", "./logs")).resolve()
    
    # サブフォルダ名（ビデオディレクトリの最後の部分）
    subfolder_name = video_dir.name
    
    archive_dir = archive_base / subfolder_name
    logs_dir = logs_base / subfolder_name
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"入力: {video_dir}")
    print(f"出力: {archive_dir}")
    print(f"ログ: {logs_dir}")
    print(f"処理ファイル数: {len(video_files)}")
    
    # ===== ここからメイン処理を実行 =====
    # (以下は元のコードを使用)
