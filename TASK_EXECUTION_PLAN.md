\# タスク実行計画書 (2026-03-24)



\## 現状サマリー

\- \*\*Lecture 01\*\*: MP4 → insight\_spec\_01.json + insight\_spec\_01\_labeled.json 完了

\- \*\*Lecture 02～21\*\*: MP4 ファイルは存在するが、insight\_spec\_XX.json がまだ生成されていない



\## ワークフロー（確認済み）



\### 【未実装】Step 0: YouTube からのMP4ダウンロード

\- \*\*スクリプト\*\*: 不明（video-scraper の video\_downloader.py は UTAGE 用）

\- \*\*入力\*\*: YouTube URL

\- \*\*出力\*\*: MP4 ファイル

\- \*\*現状\*\*: MP4 ファイルは D:\\Knowledge\_Base\\Brain\_Marketing\\videos\\downloaded\_videos に既に存在



\### 【未実装】Step 1: MP4 → Mk2\_Core\_XX.json + Mk2\_Sidecar\_XX.db 生成

\- \*\*スクリプト\*\*: 不明

\- \*\*依存\*\*: Whisper (音声認識)、OCR (画面テキスト抽出)、Gemini 3 Pro (センターピン生成)

\- \*\*出力\*\*: Mk2\_Core\_XX.json (Lecture 02～21分は存在するがテスト用ダミー)



\### 【実装済み】Step 2: Mk2\_Core\_XX.json → insight\_spec\_XX.json 変換

\- \*\*スクリプト\*\*: `convert\_to\_insight\_spec\_phase1.py`

\- \*\*実行例\*\*: `python convert\_to\_insight\_spec\_phase1.py --lecture-id 01`

\- \*\*出力\*\*: insight\_spec\_XX.json



\### 【実装済み】Step 3: insight\_spec\_XX.json にラベル付与

\- \*\*スクリプト\*\*: `expand\_insight\_spec\_with\_gemini.py`

\- \*\*実行例\*\*: `python expand\_insight\_spec\_with\_gemini.py --lecture-id 01 --top-n 5`

\- \*\*出力\*\*: insight\_spec\_01\_labeled.json



\## 直近のアクション



\### \*\*優先1: Step 1 スクリプトを確認する\*\*

\- video-scraper リポジトリで MP4 → Mk2\_Core を生成するスクリプトを特定

\- または、このリポジトリ内で実装されているか確認



\### \*\*優先2: Lecture 02～21 の Mk2\_Core\_XX.json + Mk2\_Sidecar\_XX.db を生成\*\*

\- Step 1 のスクリプトを使用して一括生成



\### \*\*優先3: Lecture 02～21 の insight\_spec\_XX.json を生成\*\*

\- `convert\_to\_insight\_spec\_phase1.py` を使用して一括生成



\### \*\*優先4: Lecture 02～21 にラベル付与\*\*

\- `batch\_label\_lectures\_02\_21.ps1` を実行



\## 未解決の質問



1\. \*\*MP4 → Mk2\_Core\_XX.json + Mk2\_Sidecar\_XX.db を生成するスクリプトはどこにあるのか？\*\*

&#x20;  - video-scraper の `master\_batch\_refiner.py` か？

&#x20;  - または、別のスクリプトか？



2\. \*\*Lecture 01 の Mk2\_Core\_01.json と Mk2\_Sidecar\_01.db はどのように生成されたのか？\*\*

&#x20;  - 実行コマンドは？



\---



\*\*この情報を確認してから、一括実行スクリプトを作成します。\*\*



