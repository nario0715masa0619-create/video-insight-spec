# バッチ実行ガイド (BATCH EXECUTION)

## 1. 概要
本プロジェクトのバッチパイプラインは、動画ファイルを入力として Whisper、EasyOCR、Gemini などを駆使し、分析の正本となる `insight_spec_{id}.json` を生成・補完することを目的としています。
各処理は独立したスクリプトとして構成されており、新規動画を処理する「通常モード」と、既存の JSON から軽量に再集計のみを実行する「軽量モード」を使い分けることができます。

## 2. バッチスクリプト一覧

| スクリプト名 | 目的 | 必須引数 / 必須環境変数 | オプション引数 | デフォルト値 / 補足 |
|---|---|---|---|---|
| `enrich_insight_spec_with_youtube_metadata.py` | YouTube API からメタデータを取得し `insight_spec` を補完 | `--archive-dir` (`ARCHIVE_OUTPUT_DIR`),<br>`--csv-path`,<br>`--api-key` (`YOUTUBE_API_KEY`) | `--lecture-ids` | `archive-dir`: `./archive`<br>`csv-path`: `phase2_2_output/video_mapping.csv`<br>`lecture-ids`: `01,02,03,04,05`<br>`api-key`: 未指定時エラー |
| `expand_insight_spec_with_gemini.py` | `insight_spec` の `center_pins` に Gemini でナレッジラベルを付与 | `--lecture-id`,<br>`--archive-dir` (`ARCHIVE_OUTPUT_DIR`) | `--top-n`,<br>`--api-key` (`GEMINI_API_KEY`) | `archive-dir`: `./archive`<br>`top-n`: 全件対象<br>`api-key`: `GEMINI_API_KEY` |
| `master_batch_refiner.py` | 複数動画ファイルを対象とした文字起こしと構造化の全体バッチ処理 | (なし) | `[video_files...]`,<br>`--skip-whisper` | `video_files`: `VIDEOS_INPUT_DIR` の全 MP4<br>`skip-whisper`: 指定時 `ARCHIVE_OUTPUT_DIR` の既存 JSON を集計 |

## 3. 各スクリプトの詳細

### 【スクリプト】`enrich_insight_spec_with_youtube_metadata.py`
- **目的**: YouTube API から再生数等のメタデータを取得し、`insight_spec` を補完する
- **前提条件**:
  - `YOUTUBE_API_KEY` が設定されていること
  - `insight_spec_*.json` が `ARCHIVE_OUTPUT_DIR` に存在すること
- **実行方法**:
  ```bash
  python scripts/enrich_insight_spec_with_youtube_metadata.py --lecture-ids 01
  ```
- **または環境変数経由**:
  ```bash
  $env:ARCHIVE_OUTPUT_DIR="D:\AI_Data\video-insight-spec\archive"
  python scripts/enrich_insight_spec_with_youtube_metadata.py --lecture-ids 01
  ```
- **出力物**: YouTube メタデータ補完後の `insight_spec_*.json`
- **所要時間**: 数秒～数分（API 呼び出し回数に依存）

---

### 【スクリプト】`expand_insight_spec_with_gemini.py`
- **目的**: 既存の `insight_spec` の `center_pins` に対して、Gemini を用いてビジネステーマ・ファネル・難易度等のナレッジラベルを付与する
- **前提条件**:
  - `GEMINI_API_KEY` が設定されていること
  - 対象の `insight_spec_{id}.json` が `ARCHIVE_OUTPUT_DIR` に存在すること
- **実行方法**:
  ```bash
  python scripts/expand_insight_spec_with_gemini.py --lecture-id 01
  ```
- **出力物**: ラベル情報補完後の `insight_spec_*.json`
- **所要時間**: 1講座あたり数十秒～数分

---

### 【スクリプト】`master_batch_refiner.py`
- **目的**: MP4 動画ファイル群を入力とし、Whisper → EasyOCR → Gemini のパイプラインを回して初期の分析データを生成する。または既存データの再集計を行う。
- **前提条件**:
  - 各種 API キーが揃っていること
  - （通常モードの場合）動画が `VIDEOS_INPUT_DIR` に配置されていること
- **実行方法**:
  ```bash
  python scripts/master_batch_refiner.py
  ```
- **出力物**: `insight_spec`（及びその中間生成物）と実行ログ
- **所要時間**:
  - 通常モード: 数時間（動画数と長さに大きく依存。テスト環境では非推奨）
  - 軽量モード: 数秒

## 4. 実行フロー例

**シナリオ A: 既存 JSON を軽く再集計したい**
すでに Whisper や Gemini による重い処理が終わっており、ダッシュボード用の動的集計をローカルで通しテストしたい場合。
```bash
python scripts/master_batch_refiner.py --skip-whisper
```

**シナリオ B: 新しい動画から一通り処理したい**
新規の動画データが届き、ゼロから文字起こし〜JSON構造化までを行いたい場合。
```bash
python scripts/master_batch_refiner.py
```
> [!CAUTION]
> 通常モードは動画1本あたり数十分〜の処理時間を要します。テストやデバッグ時には `--skip-whisper` を使うか、短いサンプル動画を指定して実行してください。

**シナリオ C: YouTube メタデータだけを補完したい**
再生回数や公開日などの最新の YouTube API メタデータのみを JSON に反映させたい場合。
```bash
python scripts/enrich_insight_spec_with_youtube_metadata.py --lecture-ids 01
```
