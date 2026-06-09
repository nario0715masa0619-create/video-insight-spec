# video-insight-spec

YouTube 動画の洞察・競合分析システム。動画視聴データを構造化し、経営判断に直結したレポートを自動生成・配信する SaaS サービスの基盤。

## 1. プロダクト概要

本システムは、YouTube動画の center_pin（学習ポイント）や各種エンゲージメントメトリクス、心理フェーズを構造化した3層JSONデータを生成し、経営陣やコンテンツプランナー向けに価値ある示唆を提供するシステムです。

ビジネスの意思決定を支援するため、**「コマンドライン（CLI）によるバッチレポート生成」**と**「対話的（GUI）な Web ダッシュボードによる多角的な分析」**の2つの利用経路をサポートしています。

---

## 2. 環境構成

本プロジェクトは以下の2つの環境で運用されています。

1. **本番安定版（Git 親リポジトリ）**: `D:\AI_スクリプト成果物\video-insight-spec`
   - `main` ブランチの最新安定版が稼働する本番ディレクトリです。
   - アプリケーションの起動には `run_prod.bat` または `streamlit run streamlit_app/app.py` を使用します。
2. **開発環境（Worktree）**: `D:\AI_スクリプト成果物\video-insight-spec-dev`
   - 新規機能開発やバグ修正を行うための作業ディレクトリです。

---

## 3. システムエントリポイント一覧

システムには以下の2つの主要な実行エントリポイントが存在します。用途に応じて使い分けてください。

| エントリポイント | 実行環境 | 役割・責務 | 主な出力物 |
| :--- | :--- | :--- | :--- |
| `competitor_analytics_generator.py` | CLI (バッチ) | 講座動画データから統計情報を算出し、HTML/Textのレポートファイル群を自動生成する。 | JSON/HTML/Text フルレポート |
| `streamlit_app/app.py` | Web GUI (対話的) | 生成済みの各種統計 JSON や DB からデータをロードし、多角的なグラフ表示、AIによる解説・改善提案、およびPDFレポートをダウンロード可能にする。 | ブラウザ上のダッシュボード UI / PDF レポート |

---

## 3. クイックスタート

### 必要な要件
- **Python 3.8+**
- 依存関係のインストール（「8. 依存関係の構成」を参照）

### 環境変数の設定
セキュリティと運用の観点から、秘密情報（APIキー等）の正本はユーザーのホームディレクトリ配下に配置する構成となっています。

1. **正本 .env のセットアップ（初回のみ）**
   Windows の場合は以下の補助スクリプトを実行してください。
   ```powershell
   .\scripts\bootstrap_user_env.ps1
   ```
   これにより、`%USERPROFILE%\.video-insight-spec\.env` が作成されます。

2. **APIキーの設定**
   作成された正本 `.env` をメモ帳等で開き、必要なキーを設定してください（詳細は `docs/ENVIRONMENT_SETUP.md` 参照）。

3. **設定の確認**
   以下のスクリプトを実行することで、必要な環境変数が正しく認識されているか確認できます。
   ```bash
   python scripts/check_environment.py
   ```
   
> [!NOTE]
> リポジトリ直下の `.env` はフォールバックとして動作しますが、誤って Git コミットしてしまうリスクを避けるため、原則としてホームディレクトリ側の `.env` を使用してください。

---

## 4. バッチレポート自動生成 (CLI 経路)

### 概要
コマンドラインから講座動画のIDやデータディレクトリを指定し、競合分析の構造化データ（生JSON）および人間が読みやすいHTML/Textレポートを自動生成します。

### 実行コマンド
```bash
python competitor_analytics_generator.py --lecture-ids "01,02,03,04,05" --archive-dir "D:/AI_Data/video-insight-spec/archive" --output-dir "reports/competitor_analytics"
```

### 処理プロセス
1. `InsightSpecRepository` を介してアーカイブディレクトリから講座データをロード。
2. `PortfolioViewService` などの各種サービスを通じて統計データを生成。
3. `ReportGenerator` を呼び出し、レスポンシブHTMLレポート（`reports/html/` 配下）およびMarkdown互換のテキストレポート（`reports/text/` 配下）を自動出力。

---

## 5. 対話的 Web ダッシュボード (Web GUI 経路)

### 概要
すでに生成・蓄積されている JSON や DB データを読み込み、Streamlit を用いて直感的かつグラフィカルに可視化・分析します。

### 実行コマンド
```bash
streamlit run streamlit_app/app.py
```

### 主要機能
- **チャンネル全体分析**: KPI メトリクス表示、テーマ分布の可視化グラフ、品質スコアランキング、PDFレポートの生成とダウンロード。
- **個別動画分析**:
  - **黄金の組み合わせ**: 高反応パターン（ファネルステージ×コンテンツタイプ×テーマ）の特定。
  - **隠れた弱点**: 品質が高いにもかかわらずエンゲージメントが低い要素の検出。
  - **心理ロードマップ**: 視聴者のフェーズ別心理変化と最適コンテンツ。
  - **競争優位性**: テーマ多様性や初心者適合度などの総合評価スコア。
  - **次のステップ提案**: 次に進むべきファネルと推奨テーマの自動提示。

### 最小実行（CLI）との違い
- バッチ経路（CLI）は**新規データの処理と固定レポートファイルの生成**に特化しています。
- ダッシュボード経路は**既存データを用いた対話的な多角分析・シミュレーションおよびPDFダウンロード**に特化しています。

### AI言語化エンジンの挙動
- `.env` に `OPENAI_API_KEY` が設定されている場合、GPT-4o（`gpt-4o`）を使用した言語化エンジン（`NarrativeEngine`）による詳細な自動分析テキストがダッシュボード上に動的に表示されます。
- **未設定の場合**: 起動時に「⚠️ 分析エンジン初期化エラー」という警告が表示されますが、ダッシュボード自体は停止せず、**グラフやスコアテーブル、PDF生成などの基本機能は sample data で正常に動作**します。

---

## 6. Executive Summary の位置付け

本システムにおける「経営者向けサマリー（Executive Summary）」は、**`converter/executive_summary_formatter.py` を唯一の正本（シングルソース）**として一本化し、CLIバッチレポート生成経路と Streamlit Web ダッシュボード経路の双方から共通利用されています。

### フォーマッタの統合状況 (`converter/executive_summary_formatter.py`)
- **状態**: **完全統合済み**。バッチ（CLI）実行時に `reports/executive_summary/` 配下へ HTML / Text 形式のサマリーファイルが自動出力・保存されます。
- **ダッシュボードへの連携**: Web ダッシュボード上の新設タブ「🎯 競合分析サマリー」において、共通ロジックをそのまま使用して HTML レポートが美しく画面上に動的描画されます。

### PDFおよびテキストダウンロード
- **状態**: ダッシュボードの「🎯 競合分析サマリー」タブにおいて、共通ロジックから生成されたマークダウンテキストデータを元に PDF およびテキストファイルを動的に生成し、その場でダウンロードできる機能が共通ロジックをベースに完結して提供されています。

---

## 7. 納品データとAI活用

本システムから出力されるデータ群（`archive/` ディレクトリ配下）は、単にダッシュボードやバッチレポートで描画されるだけでなく、**「AI接続前提の構造化動画データベース」**として高度に設計されています。

### AI活用の中心となる「最終正本」
- **`insight_spec_{id}.json`**: メタデータ、難易度、ビジネステーマ分類、購買ファネルステージ（認知・教育・クロージング等）の分類ラベルが Gemini LLM により完全付与されており、AI（ChatGPT や Gemini 等）にそのまま読み込ませることで「バズる解説の傾向抽出」「テーマ網羅性の評価」「新企画の自動提案」などのインサイトを極めて高精度に引き出すことができます。

### 補助データと現状の制約
- **`Mk2_Sidecar_{id}.db` (SQLite)**: 要素の出現時間を記録するエビデンスDBですが、現行の実データ上の仕様として、ミリ秒時間情報（`start_ms`/`end_ms`）は一律で `(0, 0)` のプレースホルダー値として記録されています。そのため、「動画の何分何秒で話されているか」という秒単位の厳密な検索・質問には現段階では対応しておりません（動画・講座単位での質問を推奨）。

> [!TIP]
> 納品データ資産のより詳しい構造や AI を活用した具体的な実戦ノウハウについては、以下の各種ドキュメントを併せてご参照ください。
> - **技術・社内向け詳細ガイド**: [DATA_DELIVERABLES_AND_AI_USECASE_GUIDE.md](docs/DATA_DELIVERABLES_AND_AI_USECASE_GUIDE.md) （実データ構造、コード裏付け、制約事項などの詳細）
> - **営業・提案者向けガイド**: [SALES_ENABLEMENT_AI_DELIVERABLES.md](docs/SALES_ENABLEMENT_AI_DELIVERABLES.md) （刺さる価値、想定問答、説明手順）
> - **顧客向け紹介資料 (A4 1枚)**: [CLIENT_ONEPAGER_AI_DATASET.md](docs/CLIENT_ONEPAGER_AI_DATASET.md) （非技術者向けの分かりやすい価値訴求）
> - **顧客向け AI プロンプトカタログ**: [CLIENT_AI_USECASE_PROMPTS.md](docs/CLIENT_AI_USECASE_PROMPTS.md) （実務でコピペして使える30個のAI質問例）

---

## 8. ディレクトリ構造

```text
video-insight-spec/
├── docs/                             # プロジェクトドキュメント
│   ├── specs/                        # スキーマ・View設計書
│   ├── phases/                       # フェーズごとの設計・計画書
│   ├── DATA_DELIVERABLES_AND_AI_USECASE_GUIDE.md # 納品データとAI活用詳細ガイド
│   ├── SALES_ENABLEMENT_AI_DELIVERABLES.md # 営業・提案用実戦ガイド
│   ├── CLIENT_ONEPAGER_AI_DATASET.md     # 顧客向け1枚資料
│   └── CLIENT_AI_USECASE_PROMPTS.md      # 顧客向け AI プロンプトカタログ
├── converter/                        # レポート生成・整形ロジック (バッチ共通)
│   ├── text_formatter.py
│   ├── html_formatter.py
│   ├── report_generator.py           # HTML/Text バッチレポート生成
│   └── executive_summary_formatter.py # (統合済み) 唯一の正本サマリー生成
├── streamlit_app/                    # Web ダッシュボード (ローカル実装/反映前提)
│   ├── app.py                        # メインエントリポイント
│   ├── config.py                     # ダッシュボード設定・配色
│   ├── data_loader.py                # キャッシング・データ読み込み
│   ├── analytics_engine.py           # 分析エンジン
│   ├── advanced_analytics_engine.py  # 唯一無二の複合分析ロジック
│   ├── narrative_engine.py           # GPT-4o 言語化エンジン
│   └── requirements.txt              # ダッシュボード専用の依存関係
├── data/                             # 集計済み JSON 等 of 置き場
│   └── final_statistics_report.json
├── competitor_analytics_generator.py # バッチレポート生成メイン
├── requirements-dev.txt              # 開発用依存関係
├── README.md                         # 本ファイル
└── .env                              # 環境変数設定ファイル (トラック非対象)
```

---

## 9. 依存関係の構成

本システムは、CLIバッチの動作環境とリッチなWebダッシュボードの動作環境で依存関係を明確に分けて管理しています。これにより不要なライブラリが競合するのを防ぎます。

### ルート（バッチ・共通環境）
バッチによるレポート生成や共通のロジック実行に必要な最小限のライブラリ（`pandas`, `numpy` 等）は、開発環境の `requirements-dev.txt` などに整備されています。
- **営業利用の最小導線**: 商談時の無料1本解析については、専用の運用ガイド [FREE_TRIAL_ONE_VIDEO_OPERATION.md](docs/FREE_TRIAL_ONE_VIDEO_OPERATION.md) を参照してください。

### ダッシュボード専用環境 (`streamlit_app/requirements.txt`)
Web ダッシュボードおよび高度な AI 分析・可視化を動作させるために必要なパッケージが定義されています。ダッシュボードを起動する際は、必ず本ファイルを指定してインストールを行ってください。

**主要な依存関係**:
- `streamlit`: ダッシュボードフレームワーク
- `pandas` / `numpy` / `plotly`: データ処理およびグラフ描画
- `openai`: GPT-4o を用いた言語化分析（`NarrativeEngine` 用）
- `fpdf2`: PDF レポートの動的生成およびダウンロード用

**インストールコマンド**:
```bash
pip install -r streamlit_app/requirements.txt
```

> [!TIP]
> Python 3.12 や 3.13 などの新しい Python 環境では、古いバージョン指定によるソースビルド時にエラーが発生することがあります。その場合は、以下のようにバージョン指定を省略して最新パッケージをインストールしてください：
> ```bash
> pip install streamlit openai fpdf2 pandas numpy plotly reportlab PyPDF2
> ```

### 開発用の自動 CI テスト (GitHub Actions)
プロジェクト全体の品質を維持するため、以下の 2 つの自動テストが CI にて毎コミット実行されます：
1. **CLI バッチテスト (`smoke-test.yml`)**: サンプルデータを用いたレポートの自動生成とファイル出力の完全性を検証。
2. **Streamlit ダッシュボード起動テスト (`streamlit-smoke-test.yml`)**: 依存パッケージの解決、構文チェック、およびヘッドレスでの起動健全性（ポート 8501 への正常応答）を自動検証。
   - ※ 本テストは OpenAI の秘密鍵 (`OPENAI_API_KEY`) が未設定の環境でも、警告表示モードで正常にパスするよう堅牢に設計されています。

---

## 10. 開発ロードマップ & 進捗状況

### フェーズの進捗

| フェーズ | タイトル | 状態 | 実装実態と成果物 |
| :--- | :--- | :--- | :--- |
| **4.2** | データ仕様設計 | ✅ 完了 | portfolio_view, growth_view, theme_view の3層JSON構造の設計 |
| **4.3** | HTML/Text フォーマッタ | ✅ 完了 | `html_formatter.py`, `text_formatter.py`, `ReportGenerator` によるバッチ自動化 |
| **5.1** | 経営者向けサマリー | ✅ 完了 | `executive_summary_formatter.py` を唯一の正本として CLI / Streamlit へ完全統合完了 |
| **6** | PoC・営業支援 | ✅ 完了 | LPメッセージング、サンプルレポート、見積自動化等 |
| **7** | プロダクト拡張 | ✅ 完了 | Webダッシュボード（`streamlit_app/`）の実装および公開 `main` ブランチへの統合完了。 |

---

## 11. セキュリティ & コンプライアンス

- **API キー管理**: `YOUTUBE_API_KEY` および `OPENAI_API_KEY` は `.env` ファイルでローカルに管理し、Git には絶対にコミットしません。
- **PII（個人情報）の保護**: GDPR および個人情報保護基準に従い、生成されるすべての公開用レポートおよび JSON 統計データは匿名化処理が施されており、個人を特定できるデータは含まれていません。
- **データ分離**: クライアントごとの視聴ログとチャンネル統計データは厳密に論理分離され、セキュリティが担保されています。
