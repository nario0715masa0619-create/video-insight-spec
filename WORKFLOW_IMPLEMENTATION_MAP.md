# ワークフロー実装マップ (2026-03-24)

## プロジェクト構成

D:\AI_スクリプト成果物/ ├── video-insight-spec/ ← 【このリポジトリ】スキーマ・仕様・Phase実装 ├── video-scraper/ ← 動画処理・Mk2ファイル生成（別リポジトリ） ├── 営業自動化プロジェクト/ └── 動画スクレイピングプロジェクト/


---

## 完全なワークフロー (MP4 → insight_spec_XX_labeled.json)

### **【Step 0】YouTube からMP4ダウンロード**
- **担当**: video-scraper / video_downloader.py
- **役割**: UTAGE コースから動画をダウンロード（本プロジェクトではYouTubeからの直接ダウンロード対応予定）
- **入力**: YouTube URL または YouTube チャンネルURL
- **出力**: MP4 ファイル → `D:\Knowledge_Base\Brain_Marketing\videos\downloaded_videos\{lectureid}_{title}.mp4`
- **状態**: ✅ MP4 ファイル既に存在（01～21）
- **実行方法**: 不明（確認要）

---

### **【Step 1】MP4 → Mk2_Core_XX.json + Mk2_Sidecar_XX.db 生成**
- **担当**: video-scraper / `master_batch_refiner.py`
- **役割**: 
  - Whisper で音声認識（音声 → テキスト）
  - FFmpeg + EasyOCR で画面テキスト抽出（OCR）
  - Gemini 3 Pro でセンターピン生成（FACT / LOGIC / SOP / CASE タグ付き）
  - SQLite Sidecar DB に visual_text インデックス化
- **入力**: MP4 ファイル（`D:\Knowledge_Base\Brain_Marketing\videos\downloaded_videos\*.mp4`）
- **出力**: 
  - `{ARCHIVE_DIR}/Mk2_Core_{lectureid}.json`
  - `{ARCHIVE_DIR}/Mk2_Sidecar_{lectureid}.db`
  - `{ARCHIVE_DIR}/Mk2_OCR_{lectureid}.txt`（中間ファイル）
- **状態**: 
  - ✅ Mk2_Core_01.json ～ 21.json 存在（テストデータ？）
  - ✅ Mk2_Sidecar_01.db ～ 21.db 存在（テストデータ？）
  - 確認: 実際のデータか、ダミーか不明
- **実行方法**:
  ```powershell
  # 全ての未処理MP4を処理（既に処理済みはスキップ）
  cd D:\AI_スクリプト成果物\video-scraper
  python master_batch_refiner.py
  
  # または、特定のMP4のみ処理
  python master_batch_refiner.py "02_【超重要！】コンテンツ販売必須の基礎知識.mp4"
環境変数:
VIDEOS_INPUT_DIR=D:\Knowledge_Base\Brain_Marketing\videos\downloaded_videos
ARCHIVE_OUTPUT_DIR=D:\Knowledge_Base\Brain_Marketing\archive
GEMINI_API_KEY=<API キー>
GEMINI_MODEL_ID=gemini-3-pro-preview
WHISPER_MODEL_SIZE=small
WHISPER_DEVICE=cpu
EASYOCR_GPU=false
EASYOCR_LANGUAGES=ja,en
処理フロー:
Whisper で音声文字起こし（segments_data 生成）
FFmpeg でシーン抽出（フレーム JPG 生成）
EasyOCR で各フレームから visual_text 抽出
Gemini API で OFLOOP 原子分解（FACT / LOGIC / SOP / CASE）
出力ファイル検証（JSON 妥当性チェック）
Sidecar DB へエビデンス登録
処理結果 JSON を logs に保存
出力ログ:
logs/antigravity_YYYYMMDD_HHMMSS.log
logs/processing_results_YYYYMMDD_HHMMSS.json
logs/retry_targets_YYYYMMDD_HHMMSS.txt（失敗時）
【Step 2】Mk2_Core_XX.json → insight_spec_XX.json 変換
担当: video-insight-spec / convert_to_insight_spec_phase1.py
役割: JSON_SPEC.md のスキーマに準拠した最終 JSON に変換
依存モジュール:
converter/db_helper.py - Sidecar DB 読み込み
converter/json_extractor.py - Mk2_Core_XX.json パース
converter/knowledge_analyzer.py - ノウハウ分析
converter/keyword_extractor.py - キーワード抽出
converter/views_competitive_builder.py - views.competitive ビュー構築
converter/insights_converter.py - 最終 JSON 生成
入力:
Mk2_Core_{lectureid}.json
Mk2_Sidecar_{lectureid}.db
出力: {ARCHIVE_DIR}/insight_spec_{lectureid}.json
状態: ✅ 実装済み・動作確認済み（Lecture 01）
実行方法:
Copypython convert_to_insight_spec_phase1.py --lecture-id 01
パラメータ:
--lecture-id (必須): Lecture ID (e.g., "01")
--core-json (オプション): Mk2_Core パス（自動検出）
--sidecar-db (オプション): Sidecar DB パス（自動検出）
--output (オプション): 出力パス（デフォルト: archive ディレクトリ）
--archive-dir: アーカイブディレクトリ（デフォルト: D:\Knowledge_Base\Brain_Marketing\archive）
【Step 3】Phase 2: YouTube API 統合（未実装）
担当: video-insight-spec / phase2_2_antigravity_full.py
役割: YouTube API で動画メタデータ取得
出力: views.competitive に view_count, like_count, comment_count 追加
状態: ⚠️ 部分実装（テストのみ）
【Step 4】Phase 3: Gemini ラベル付与
担当: video-insight-spec / expand_insight_spec_with_gemini.py
役割: Gemini 3 Pro で center_pins にラベルを自動付与
labels.business_theme: マーケティング、セールス、プロダクト等（1～3個）
labels.funnel_stage: 認知、興味、教育、比較検討、クロージング、継続・LTV
labels.difficulty: beginner / intermediate / advanced
依存: converter/gemini_knowledge_expander.py (GeminiKnowledgeLabeler クラス)
入力: insight_spec_{lectureid}.json
出力: insight_spec_{lectureid}_labeled.json
状態: ✅ 実装済み・テスト 15/15 PASS
実行方法:
Copypython expand_insight_spec_with_gemini.py --lecture-id 01 --top-n 5
パラメータ:
--lecture-id (必須): Lecture ID
--top-n (デフォルト: 5): ラベル付与対象の上位N件
--output (オプション): 出力ファイルパス
--archive-dir: アーカイブディレクトリ
ファイル構成（video-insight-spec）
video-insight-spec/
├── converter/
│   ├── __init__.py
│   ├── db_helper.py                    ← SQLite Sidecar DB 読み込み
│   ├── db_cleaner.py                   ← テスト用 DB クリーナー
│   ├── json_extractor.py               ← Mk2_Core_XX.json パース
│   ├── knowledge_analyzer.py           ← ノウハウ分析
│   ├── keyword_extractor.py            ← キーワード抽出
│   ├── views_competitive_builder.py    ← views.competitive ビュー構築
│   ├── insights_converter.py           ← 最終 JSON 生成（Phase 1）
│   ├── ocr_text_cleaner.py             ← OCR テキストクリーニング（Phase 2.2.2）
│   ├── youtube_video_id_enricher.py    ← YouTube Video ID 補充（Phase 2.2.3）
│   └── gemini_knowledge_expander.py    ← Gemini ラベル付与（Phase 3）
│
├── tests/
│   ├── test_*.py                       ← 各モジュールのテスト
│   └── TEST_IMPROVEMENT_PLAN.md        ← テスト改善計画
│
├── analysis/
│   └── （将来用）
│
├── convert_to_insight_spec_phase1.py   ← 【メインスクリプト】Step 2 実行
├── expand_insight_spec_with_gemini.py  ← 【メインスクリプト】Step 4 実行
├── batch_label_lectures_02_21.ps1      ← Step 4 の一括実行スクリプト
│
├── JSON_SPEC.md                        ← スキーマ定義（入出力形式）
├── AGENTS.md                           ← プロジェクト概要
├── WORKFLOW_IMPLEMENTATION_MAP.md      ← 【このファイル】
├── PHASE3_IMPROVEMENT_ROADMAP.md       ← Phase 3.1～3.3 改善計画
│
└── logs/
    └── phase3_batch_*.log              ← 実行ログ
現在の状態
Lecture	Mk2_Core	Mk2_Sidecar	insight_spec	labeled	状態
01	✅	✅	✅	✅	完了
02～21	✅	✅	❌	❌	要処理
⚠️ Mk2_Core_02～21 は実テストデータか確認が必要

今後のアクション
【優先度 1】Lecture 02～21 の一括処理（Step 1）
Mk2_Core_02～21.json + Mk2_Sidecar_02～21.db が実テストデータか確認してから、必要に応じて再生成

【優先度 2】Lecture 02～21 の一括処理（Step 2 + Step 4）
convert_to_insight_spec_phase1.py を使用して insight_spec_02～21.json を生成
batch_label_lectures_02_21.ps1 を使用して insight_spec_02～21_labeled.json を生成
【優先度 3】Phase 2.2～2.2.3 の実装と検証
環境変数（.env）
Copy# video-scraper 用
VIDEOS_INPUT_DIR=D:\Knowledge_Base\Brain_Marketing\videos\downloaded_videos
ARCHIVE_OUTPUT_DIR=D:\Knowledge_Base\Brain_Marketing\archive
GEMINI_API_KEY=<API キー>
GEMINI_MODEL_ID=gemini-3-pro-preview
WHISPER_MODEL_SIZE=small
WHISPER_DEVICE=cpu
EASYOCR_GPU=false
EASYOCR_LANGUAGES=ja,en

# video-insight-spec 用
YOUTUBE_API_KEY=<YouTube API キー>（Phase 2 用）