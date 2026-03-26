# video-insight-spec

**YouTube動画から『実行可能な知恵』を抽出し、JSON と SQLite で蓄積する仕組みの仕様書・設計リポジトリ。**

## クイックスタート

### セットアップ
\\\ash
cp .env.example .env
# .env を編集して YOUTUBE_API_KEY を設定
\\\

### Views 生成（Phase 4）
\\\ash
python generate_views.py --lecture-ids "01,02,03,04,05" --archive-dir "D:\\AI_Data\\video-insight-spec\\archive" --api-key "YOUR_API_KEY"
\\\

### Weekly Report 生成（Phase 4.1）
\\\ash
python weekly_report_generator.py --lecture-ids "01,02,03,04,05" --archive-dir "D:\\AI_Data\\video-insight-spec\\archive" --output-dir "reports/weekly"
\\\

## ドキュメント

| ドキュメント | 説明 |
|-----------|------|
| [docs/PROJECT_OVERVIEW.md](./docs/PROJECT_OVERVIEW.md) | 📖 詳細な実装進捗・Phase ごとの説明 |
| [JSON_SPEC.md](./docs/specs/JSON_SPEC.md) | JSON スキーマ定義 |
| [docs/architecture/MODULES.md](./docs/architecture/MODULES.md) | モジュール参照（全モジュールの役割） |
| [docs/operations/DEPLOYMENT_GUIDE.md](./docs/operations/DEPLOYMENT_GUIDE.md) | デプロイメントガイド |

## ⚠️ セキュリティに関する注意

本リポジトリの過去のコミット履歴に Google API キー（\AIza...\）が含まれていました。
**該当のAPIキーは既に無効化（Revoke）済みです。**

ご自身で取得した有効なAPIキーを用いて \.env\ ファイルを作成してください。
\.env\ ファイルは \.gitignore\ に登録されており、Git のコミット対象外です。

## ライセンス
MIT

---
Last Updated: 2026-03-26
