# 環境変数・Secrets 管理ガイド

本システムでは、APIキーなどの秘密情報や、ディレクトリパスなどの構成情報を環境変数（`.env`）を用いて管理します。

## 1. 設定ファイルの読み込み順序

セキュリティ向上と、リポジトリ再クローン時の再設定の手間を省くため、環境変数は以下の順序で読み込まれます（上位が優先）。

1. **OS の環境変数**: 既に設定されているシステム環境変数。
2. **正本 `.env`**: `%USERPROFILE%\.video-insight-spec\.env` （ユーザーホームディレクトリ）
3. **フォールバック `.env`**: `./.env` （リポジトリ直下。誤コミット防止のため非推奨）

## 2. セットアップ手順

1. リポジトリのルートで以下の PowerShell スクリプトを実行します。
   ```powershell
   .\scripts\bootstrap_user_env.ps1
   ```
   これにより、ユーザーのホームディレクトリに設定用の `.env` ファイルが作成されます。

2. 作成された `%USERPROFILE%\.video-insight-spec\.env` を開き、必要な値を入力します。

3. 設定が正しく反映されたか確認するため、以下のコマンドを実行します。
   ```bash
   python scripts/check_environment.py
   ```

## 3. 環境変数一覧表

### Secrets (API Keys)
| 変数名 | 用途 | 必須/任意 | 欠落時の挙動 |
| :--- | :--- | :--- | :--- |
| `OPENAI_API_KEY` | StreamlitダッシュボードでのAI分析（NarrativeEngine） | 任意 | AIによる文章での解説・提案機能が無効化されます（基本グラフ表示や既存データ閲覧は可能です） |
| `YOUTUBE_API_KEY` | 動画メタデータや統計情報の取得（バッチ処理） | バッチ時は必須 | API呼び出し時にエラー（YouTubeAPIError）が発生し、バッチ処理が失敗します |
| `GEMINI_API_KEY` | 音声認識後のテキストからセンターピンを抽出する処理等 | バッチ時は必須 | バッチ処理開始時にエラーとなり処理が停止します |

### Configuration (Directories & Paths)
主にバッチ処理の入出力先を指定します。デフォルト値が設定されているため、通常は変更不要です。
| 変数名 | 用途 | デフォルト値 / 推奨値 |
| :--- | :--- | :--- |
| `VIDEOS_INPUT_DIR` | ダウンロード済み動画の入力先 | `D:\AI_Data\video-insight-spec\downloaded_videos` |
| `ARCHIVE_OUTPUT_DIR` | 処理済み JSON / DB の出力先 | `D:\AI_Data\video-insight-spec\archive` |
| `TEMP_DIR` | 画像抽出等の一時作業ディレクトリ | `./batch_refine_work` |
| `LOGS_DIR` | ログファイルの出力先 | `./logs` |
| `REAL_CORE_JSON_PATH` | テスト用・開発用のコアJSONパス | 未設定 |
| `REAL_SIDECAR_DB_PATH` | テスト用・開発用のDBパス | 未設定 |
| `TEST_OUTPUT_DIR` | テスト結果の出力先 | `./test_output` |

### Configuration (Processing Settings)
AIモデルのパラメータや、ffmpeg、OCRなどのハードウェアリソース利用に関する設定です。
| 変数名 | 用途 | デフォルト値 |
| :--- | :--- | :--- |
| `GEMINI_MODEL_ID` | Gemini モデル名 | `gemini-3-pro-preview` |
| `WHISPER_MODEL_SIZE` | 音声認識 Whisper のモデルサイズ | `small` |
| `WHISPER_DEVICE` | Whisper の処理デバイス（cpu/cuda） | `cpu` |
| `EASYOCR_GPU` | 画面内テキスト抽出時の GPU 使用有無 | `false` |
| `EASYOCR_LANGUAGES` | EasyOCR 抽出対象言語 | `ja,en` |
| `FRAMES_PER_MINUTE` | 1分あたりの動画フレーム抽出枚数 | `3` |
| `FFMPEG_PATH` | ffmpeg コマンドのパス | `ffmpeg` |

## 4. APIキー欠落時の挙動（劣化モード）について

Streamlit ダッシュボードは、`OPENAI_API_KEY` が設定されていなくても起動し、システムクラッシュを回避するよう設計されています。
キーが未設定の場合、画面上に警告メッセージが表示されますが、既存の生成済みデータ（JSON, SQLite）の閲覧やグラフ生成、スコア確認などの基本機能はそのまま利用可能です。
