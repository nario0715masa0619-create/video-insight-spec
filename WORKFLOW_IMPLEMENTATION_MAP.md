\# ワークフロー実装マップ (2026-03-24)



\## プロジェクト構成



D:\\AI\_スクリプト成果物/ ├── video-insight-spec/ ← 【このリポジトリ】スキーマ・仕様・Phase実装 ├── video-scraper/ ← 動画処理・Mk2ファイル生成（別リポジトリ） ├── 営業自動化プロジェクト/ └── 動画スクレイピングプロジェクト/





\---



\## 完全なワークフロー (MP4 → insight\_spec\_XX\_labeled.json)



\### \*\*【Step 0】YouTube からMP4ダウンロード\*\*

\- \*\*担当\*\*: video-scraper / video\_downloader.py

\- \*\*役割\*\*: UTAGE コースから動画をダウンロード（本プロジェクトではYouTubeからの直接ダウンロード対応予定）

\- \*\*入力\*\*: YouTube URL または YouTube チャンネルURL

\- \*\*出力\*\*: MP4 ファイル → `D:\\Knowledge\_Base\\Brain\_Marketing\\videos\\downloaded\_videos\\{01d}\_{title}.mp4`

\- \*\*状態\*\*: ✅ MP4 ファイル既に存在（01～21）

\- \*\*実行方法\*\*: 不明（確認要）



\---



\### \*\*【Step 1】MP4 → Mk2\_Core\_XX.json + Mk2\_Sidecar\_XX.db 生成\*\*

\- \*\*担当\*\*: video-scraper / master\_batch\_refiner.py（推定）

\- \*\*役割\*\*: 

&#x20; - Whisper で音声認識（音声 → テキスト）

&#x20; - FFmpeg + EasyOCR で画面テキスト抽出（OCR）

&#x20; - Gemini 3 Pro でセンターピン生成（FACT / LOGIC / SOP タグ付き）

&#x20; - SQLite Sidecar DB に visual\_text インデックス化

\- \*\*入力\*\*: MP4 ファイル

\- \*\*出力\*\*: 

&#x20; - `{ARCHIVE\_DIR}/Mk2\_Core\_{lectureid}.json`

&#x20; - `{ARCHIVE\_DIR}/Mk2\_Sidecar\_{lectureid}.db`

\- \*\*状態\*\*: 

&#x20; - ✅ Mk2\_Core\_01.json ～ 21.json 存在（テストデータ？）

&#x20; - 確認: 実際のデータか、ダミーか不明

\- \*\*実行方法\*\*: 不明（確認要）



\---



\### \*\*【Step 2】Mk2\_Core\_XX.json → insight\_spec\_XX.json 変換\*\*

\- \*\*担当\*\*: video-insight-spec / `convert\_to\_insight\_spec\_phase1.py`

\- \*\*役割\*\*: JSON\_SPEC.md のスキーマに準拠した最終 JSON に変換

\- \*\*依存モジュール\*\*:

&#x20; - `converter/db\_helper.py` - Sidecar DB 読み込み

&#x20; - `converter/json\_extractor.py` - Mk2\_Core\_XX.json パース

&#x20; - `converter/knowledge\_analyzer.py` - ノウハウ分析

&#x20; - `converter/keyword\_extractor.py` - キーワード抽出

&#x20; - `converter/views\_competitive\_builder.py` - views.competitive ビュー構築

&#x20; - `converter/insights\_converter.py` - 最終 JSON 生成

\- \*\*入力\*\*: 

&#x20; - `Mk2\_Core\_{lectureid}.json`

&#x20; - `Mk2\_Sidecar\_{lectureid}.db`

\- \*\*出力\*\*: `{ARCHIVE\_DIR}/insight\_spec\_{lectureid}.json`

\- \*\*状態\*\*: ✅ 実装済み・動作確認済み（Lecture 01）

\- \*\*実行方法\*\*:

&#x20; ```powershell

&#x20; python convert\_to\_insight\_spec\_phase1.py --lecture-id 01

パラメータ:

\--lecture-id (必須): Lecture ID (e.g., "01")

\--core-json (オプション): Mk2\_Core パス（自動検出）

\--sidecar-db (オプション): Sidecar DB パス（自動検出）

\--output (オプション): 出力パス（デフォルト: archive ディレクトリ）

\--archive-dir: アーカイブディレクトリ（デフォルト: D:\\Knowledge\_Base\\Brain\_Marketing\\archive）

【Step 3】Phase 2: YouTube API 統合（未実装）

担当: video-insight-spec / phase2\_2\_antigravity\_full.py

役割: YouTube API で動画メタデータ取得

出力: views.competitive に view\_count, like\_count, comment\_count 追加

状態: ⚠️ 部分実装（テストのみ）

【Step 4】Phase 3: Gemini ラベル付与

担当: video-insight-spec / expand\_insight\_spec\_with\_gemini.py

役割: Gemini 3 Pro で center\_pins にラベルを自動付与

labels.business\_theme: マーケティング、セールス、プロダクト等（1～3個）

labels.funnel\_stage: 認知、興味、教育、比較検討、クロージング、継続・LTV

labels.difficulty: beginner / intermediate / advanced

依存: converter/gemini\_knowledge\_expander.py (GeminiKnowledgeLabeler クラス)

入力: insight\_spec\_{lectureid}.json

出力: insight\_spec\_{lectureid}\_labeled.json

状態: ✅ 実装済み・テスト 15/15 PASS

実行方法:

Copypython expand\_insight\_spec\_with\_gemini.py --lecture-id 01 --top-n 5

パラメータ:

\--lecture-id (必須): Lecture ID

\--top-n (デフォルト: 5): ラベル付与対象の上位N件

\--output (オプション): 出力ファイルパス

\--archive-dir: アーカイブディレクトリ

ファイル構成（video-insight-spec）

video-insight-spec/

├── converter/

│   ├── \_\_init\_\_.py

│   ├── db\_helper.py                    ← SQLite Sidecar DB 読み込み

│   ├── db\_cleaner.py                   ← テスト用 DB クリーナー

│   ├── json\_extractor.py               ← Mk2\_Core\_XX.json パース

│   ├── knowledge\_analyzer.py           ← ノウハウ分析

│   ├── keyword\_extractor.py            ← キーワード抽出

│   ├── views\_competitive\_builder.py    ← views.competitive ビュー構築

│   ├── insights\_converter.py           ← 最終 JSON 生成（Phase 1）

│   ├── ocr\_text\_cleaner.py             ← OCR テキストクリーニング（Phase 2.2.2）

│   ├── youtube\_video\_id\_enricher.py    ← YouTube Video ID 補充（Phase 2.2.3）

│   └── gemini\_knowledge\_expander.py    ← Gemini ラベル付与（Phase 3）

│

├── tests/

│   ├── test\_\*.py                       ← 各モジュールのテスト

│   └── TEST\_IMPROVEMENT\_PLAN.md        ← テスト改善計画

│

├── analysis/

│   └── （将来用）

│

├── convert\_to\_insight\_spec\_phase1.py   ← 【メインスクリプト】Step 2 実行

├── expand\_insight\_spec\_with\_gemini.py  ← 【メインスクリプト】Step 4 実行

├── batch\_label\_lectures\_02\_21.ps1      ← Step 4 の一括実行スクリプト

│

├── JSON\_SPEC.md                        ← スキーマ定義（入出力形式）

├── AGENTS.md                           ← プロジェクト概要

├── WORKFLOW\_IMPLEMENTATION\_MAP.md      ← 【このファイル】

├── PHASE3\_IMPROVEMENT\_ROADMAP.md       ← Phase 3.1～3.3 改善計画

│

└── logs/

&#x20;   └── phase3\_batch\_\*.log              ← 実行ログ







現在の状態

Lecture	Mk2\_Core	Mk2\_Sidecar	insight\_spec	labeled	状態

01	✅	✅	✅	✅	完了

02～21	✅	✅	❌	❌	要処理

❌ Mk2\_Core\_02～21 は実テストデータか確認が必要



今後のアクション

【優先度 1】Step 1 の実行方法を確認・ドキュメント化

video-scraper/master\_batch\_refiner.py の確認

YouTube からの MP4 ダウンロード + 処理の実行方法を記述

【優先度 2】Lecture 02～21 の一括処理

Mk2\_Core\_02～21.json + Mk2\_Sidecar\_02～21.db を生成（Step 1）

insight\_spec\_02～21.json を生成（Step 2）

insight\_spec\_02～21\_labeled.json を生成（Step 4）

【優先度 3】Phase 2.2～2.2.3 の実装と検証

環境変数（.env）

GEMINI\_API\_KEY=<API キー>

GEMINI\_MODEL\_ID=gemini-3-pro-preview

YOUTUBE\_API\_KEY=<YouTube API キー>（Phase 2 用）



\*\*では、これを Git にコミットします：\*\*



```powershell

cd D:\\AI\_スクリプト成果物\\video-insight-spec



\# ファイル作成

notepad WORKFLOW\_IMPLEMENTATION\_MAP.md

\# 上記を貼り付けて保存



\# Git コミット

git add WORKFLOW\_IMPLEMENTATION\_MAP.md

git commit -m "docs: WORKFLOW\_IMPLEMENTATION\_MAP.md - 完全なワークフロー仕様書を作成"

git push origin main



\# 確認

git log --oneline -3

