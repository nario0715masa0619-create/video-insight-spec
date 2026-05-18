# video-insight-spec

YouTube 動画の洞察・競合分析システム。動画視聴データを構造化し、経営判断に直結したレポートを自動生成・配信する SaaS サービスの基盤です。

---

## 1. プロジェクト概要
本プロジェクトは、YouTube動画から抽出されたメタデータや知識構造（JSON形式の `insight_spec`）を入力とし、各種分析ビュー（ポートフォリオビュー、成長推移ビュー、テーマ別ビュー）を生成して、人間が読みやすい形式（HTML/Text）のレポートとして自動出力するシステムです。

## 2. 実装済みのこと / 未実装のこと
コードの解析結果に基づき、現在の実装状況は以下の通りとなっています。

- **実装済みのこと**:
  - 事前に処理された JSON データ（`insight_spec`）からの各種分析ビュー（Portfolio / Growth / Theme View）の生成ロジック。
  - HTML（レスポンシブデザイン対応）および テキスト（Markdown互換）形式での競合分析レポート自動生成。
  - 最小実行用のサンプルデータ（`sample_archive/` 配下に同梱）。
- **未実装のこと（将来計画 / フェーズ7以降）**:
  - **Webダッシュボード機能 (`app.py` 等)**: 現在、リポジトリ内に `app.py` や Streamlit/Flask 等を用いたダッシュボード用の実装コード・起動スクリプトは**存在しません**（ビジョン・計画段階です）。
  - **REST API / Slack統合**: APIによるデータ公開機能やSlack自動通知機能は未実装です。
  - **AIによる自動提案生成**: フェーズ8以降での実装計画となっています。

## 3. 起動方法の全体像
本リポジトリにおける主要な実行経路の全体像です。

| 実行モード | エントリポイント | 必要データ | 必要な環境変数/`.env` | 現状のステータス |
| :--- | :--- | :--- | :--- | :--- |
| **バッチレポート生成** | `competitor_analytics_generator.py` | `insight_spec_*.json` | **不要** (最小実行時) | **実装済み・即時実行可能** |
| **Webダッシュボード** | `app.py` (※未存在) | - | - | **未実装 (将来予定)** |

> [!IMPORTANT]
> リポジトリ内には現在 `app.py` は存在せず、Webダッシュボードを起動する手段はありません。現行バージョンでの主要な使い方は、`competitor_analytics_generator.py` を用いた「バッチレポート生成」となります。

## 4. 最小実行
「最小実行」とは、本リポジトリに付属している「処理済みダミーデータ」を用いて、レポート生成スクリプトを単独で動かすことを指します。このモードでは環境変数 `.env`（および `YOUTUBE_API_KEY`）は**不要**です。

### 最小実行手順:
1. **依存関係のインストール**:
   ```bash
   pip install -r requirements.txt
   ```
2. **サンプルデータでの実行**:
   ```bash
   python competitor_analytics_generator.py --lecture-ids "01,02" --archive-dir "sample_archive"
   ```
   ※ Windows環境で絵文字等の文字化けや `UnicodeEncodeError` が発生する場合は、以下のように UTF-8 モードを有効にして実行してください。
   ```powershell
   $env:PYTHONUTF8=1; python competitor_analytics_generator.py --lecture-ids "01,02" --archive-dir "sample_archive"
   ```

## 5. ダッシュボード起動手順
- **ステータス: 未実装（将来予定）**
- **詳細**: プロジェクト計画（`docs/PROJECT_OVERVIEW.md`）にある「Webダッシュボード（リアルタイム可視化）」は将来の拡張機能（フェーズ7）であり、現在は起動スクリプト（`app.py` など）や関連するダッシュボード用パッケージは実装されていません。そのため、現時点でダッシュボードを起動する手順はありません。

## 6. バッチ生成手順
本番データまたは任意の解析データからバッチレポートを生成する手順です。

### 実行方法:
```bash
python competitor_analytics_generator.py --lecture-ids "<対象ID(カンマ区切り)>" --archive-dir "<データ格納ディレクトリ>"
```
- **必須引数**:
  - `--lecture-ids`: 解析対象となるレクチャーID（例: `"01,02"`）。
  - `--archive-dir`: `insight_spec_{lecture_id}.json` が格納されているディレクトリパス。

## 7. Executive Summary の位置付け
- **現状の実態**: `converter/executive_summary_formatter.py` という経営者向けサマリーのジェネレーターコード自体は実装されています。
- **連携状況**: 現在、主実行経路である `competitor_analytics_generator.py`（および `ReportGenerator`）は、この Executive Summary フォーマッタを呼び出しておらず、**バッチ処理の自動出力パイプラインには未統合**の状態です。
- **出力されるもの**: バッチ処理で実際に出力されるのは、`reports/html/` および `reports/text/` 配下のフルレポート（HTML/Text）のみとなります。

## 8. 入出力データ
- **入力データ仕様**:
  - `--archive-dir` で指定したフォルダ内にある `insight_spec_{lecture_id}.json`。
  - 内部に `video_meta`（動画基本情報）、`knowledge_core`（テーマ・難易度など）、`views.competitive.snapshot_history`（エンゲージメント推移）が必要です。
- **出力物**:
  - `reports/competitor_analytics/competitor_analytics_YYYYMMDD.json`
  - `reports/html/competitor_analytics_YYYYMMDD.html` (フルHTMLレポート)
  - `reports/text/competitor_analytics_YYYYMMDD.txt` (Markdown互換テキスト)

## 9. 依存関係
本リポジトリの依存関係は、本番（runtime）用と開発・テスト（dev）用に分離して定義されています。

- **`requirements.txt` (本番実行用)**:
  - `google-api-python-client` / `google-auth` (将来的なAPI取得/拡張処理用)
  - `python-dotenv` (環境変数ロード用)
  - `janome` (NLP / キーワード抽出用として `converter/keyword_extractor.py` が内部使用するため**必須**)
- **`requirements-dev.txt` (開発・テスト用)**:
  - `pytest` / `pytest-cov` (単体テスト実行用)

## 10. 既知の制約
- **`.env` ファイルの自動ロードについて**: 
  現在、主要なバッチ実行エントリポイントである `competitor_analytics_generator.py` は、内部で `.env` を自動ロード（`load_dotenv`）していません。APIを利用する取得系スクリプト等で `YOUTUBE_API_KEY` を参照させる場合は、OS側やシェル側で環境変数を明示的にロードするか、呼び出し時に環境変数を引き渡す必要があります。
- **成長推移（Growth View）の生成条件**:
  入力データ内の `snapshot_history` が2件未満である場合、成長率が計算できないため、Growth View からそのレクチャーは自動的にスキップされます。最小実行の確認時は、`snapshot_history` が2件以上存在する `sample_archive` をご使用ください。
