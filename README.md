# video-insight-spec

YouTube 動画の洞察・競合分析システム。動画視聴データを構造化し、経営判断に直結したレポートを自動生成・配信する SaaS サービスの基盤です。

---

## 1. プロジェクト概要
YouTube動画から抽出されたメタデータや知識構造（json）を入力とし、ポートフォリオビュー、成長推移ビュー、テーマ別ビューなどの分析結果をJSON/HTML/Text形式で自動生成します。

## 2. できること / まだできないこと
- **できること（実装済）**: 
  - 事前に処理された JSON データ（insight_spec）からの各種分析ビュー生成
  - 経営者向け1ページサマリー（Executive Summary）の出力
  - HTML（ブラウザ向け）/ テキスト（マークダウン互換）形式でのレポート生成
- **まだできないこと（将来予定）**: 
  - Webダッシュボードでのリアルタイム可視化
  - REST APIによるデータ公開
  - Slack等への自動通知・アラート
  - AIによる自動提案生成（Phase 8以降）

## 3. 最小実行に必要なもの
「最小実行」とは、本リポジトリに付属している「処理済みダミーデータ」を用いて、レポート生成スクリプト（`competitor_analytics_generator.py`）を単独で動かすことを指します。

- Python 3.8+
- 処理済みの JSON データを含むディレクトリ（本リポジトリに同梱されている `sample_archive/` を使用できます）
- ※ **注意**: 最小実行においては、環境変数 `.env`（および `YOUTUBE_API_KEY`）は**不要**です。スクリプトは既存のJSONファイルを読み込むだけで完結します。

## 4. 最小実行手順
1. **リポジトリをクローン**
   ```bash
   git clone <repository-url>
   cd video-insight-spec
   ```
2. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```
3. **サンプルデータでの実行**
   同梱されているダミーデータを使ってレポートを生成します。
   ```bash
   python competitor_analytics_generator.py --lecture-ids "01,02" --archive-dir "sample_archive"
   ```
   ※ Windows 環境で絵文字による `UnicodeEncodeError` 等の文字化けが出る場合は、UTF-8 モードで実行してください。
   ```powershell
   $env:PYTHONUTF8=1; python competitor_analytics_generator.py --lecture-ids "01,02" --archive-dir "sample_archive"
   ```

## 5. YouTube API を使う処理を行う場合の追加前提
新規のYouTube動画データからメタデータ取得・ビュー拡張（Phase 2/3 スクリプト）などを行う場合のみ、YouTube API キーが必要になります。

1. `.env.example` をコピーして `.env` を作成。
2. `.env` ファイルに `YOUTUBE_API_KEY=あなたのキー` を設定。
3. `google-api-python-client` などの関連ライブラリ（`requirements.txt` に記載済）を使用します。

## 6. ディレクトリ構成
```text
video-insight-spec/
├── docs/             # 仕様書、各フェーズのドキュメント
├── converter/        # コアロジック（JSON抽出、View生成、レポート出力）
├── sample_archive/   # 最小実行確認用のダミーJSONデータ
├── reports/          # 自動生成されたレポートの出力先（実行後に生成）
├── tests/            # テストコード
├── requirements.txt      # 実行に必要なパッケージ（最小実行用）
├── requirements-dev.txt  # 開発・テストに必要なパッケージ
├── competitor_analytics_generator.py # 競合分析レポート生成エントリポイント
└── .env.example      # 環境変数のテンプレート（API利用時のみ設定）
```

## 7. 入力データ仕様
スクリプトは `--archive-dir` で指定したフォルダ内にある `insight_spec_{lecture_id}.json` を読み込みます。

- **必須構造**: `video_meta`, `knowledge_core`, `views.competitive.snapshot_history` などの階層が必要です（詳細は `docs/specs/JSON_SPEC.md` を参照）。
- **`sample_archive` の役割**: 初期動作確認のためのモックデータです。実際の分析には実データを `--archive-dir` に配置してください。

## 8. 実行コマンド例
```bash
# サンプルデータでの最小実行
python competitor_analytics_generator.py --lecture-ids "01,02" --archive-dir "sample_archive"

# 実データでの実行例 (archive ディレクトリに insight_spec_01.json 等が存在する場合)
python competitor_analytics_generator.py --lecture-ids "01,02,03,04,05" --archive-dir "archive"
```

## 9. 出力物
実行後、以下のディレクトリに各種レポートが生成されます。
- `reports/competitor_analytics/competitor_analytics_YYYYMMDD.json`
- `reports/html/competitor_analytics_YYYYMMDD.html`
- `reports/text/competitor_analytics_YYYYMMDD.txt`

## 10. よくある失敗
- **`FileNotFoundError`**: `--archive-dir` の指定忘れ、または指定したディレクトリ内に該当する `insight_spec_*.json` が存在しない。
- **`UnicodeEncodeError`**: Windows コマンドプロンプト等で実行時、✅ や ❌ の文字が出力できずにクラッシュする（対策: `$env:PYTHONUTF8=1` を付加）。
- **スキップされる講座がある**: growth_view の生成には最低2回分の履歴（`snapshot_history` >= 2）が必要です。1件しかない場合はスキップされます。

## 11. セキュリティ注意
- **`.env` は絶対に Git にコミットしないでください**（`.gitignore` で除外されています）。
- 提供された `sample_archive/` には本番の個人情報やAPIキーは含まれていません。実データを扱う際は取り扱いに注意してください。

## 12. 既知の制約
- 現在、`competitor_analytics_generator.py` はスクリプト内部で `.env` を直接ロード（`load_dotenv`）していません。API を使用する別のスクリプトを実行する場合は、環境変数がOS側で正しくロードされることを確認してください。
- レポート生成機能は現在バッチ実行を前提としています。スケジューラ（APScheduler/cron等）の設定は Phase 7-2 以降での実装予定です。
