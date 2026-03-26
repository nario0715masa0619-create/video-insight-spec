# video-insight-spec

**YouTube動画から『実行可能な知恵』を抽出し、JSON と SQLite で蓄積する仕組みの仕様書・設計リポジトリ。**

## このリポジトリについて

\ideo-insight-spec\ は、以下を統括する「スキーマ・仕様設計の中核」です：

- **JSON スキーマ定義** (\JSON_SPEC.md\)：1本の動画ごとの知識構造
- **サイドカー DB 設計** (\JSON_SPEC.md\ の追記セクション）：時間軸インデックス
- **AI エージェント向けマニュアル** (\AGENTS.md\)：実装・拡張時の指針
- **実装ガイダンス** (PHASE*.md)：各フェーズでの具体的な処理仕様

> 💡 **実装コードや API キーなどの機密情報は、別リポジトリ（\ideo-scraper\ など）で管理**しています。

## プロジェクト進捗

| フェーズ | 状態 | 説明 | 更新日 |
|---------|------|------|--------|
| Phase 1 | ✅ 完了 | 動画ダウンロード、メタデータ抽出 | - |
| Phase 2 | ✅ 完了 | YouTube API、OCR、Whisper 統合 | - |
| Phase 3 | ✅ 完了 | Gemini AI ラベリング、52 個の知識要素抽出 | - |
| Phase 3.3 | ✅ 完了 | YouTube API で video_meta 埋め込み | - |
| Phase 4 | ✅ 完了 | Views 生成（engagement_score ベース）、YouTube Analytics 統合 | 2026-03-26 |
| Phase 4.1 | ✅ 完了 | Weekly Report Generation（baseline/delta 計算） | 2026-03-26 |
| Phase 4.2 | 📋 準備中 | Competitor Analytics Views（portfolio/growth/theme_view） | TBD |

## ドキュメント案内

| ドキュメント | 対象者 | 概要 |
|-----------|--------|------|
| [JSON_SPEC.md](./docs/specs/JSON_SPEC.md) | 設計者・実装者 | JSON スキーマと DB 構造の完全仕様 |
| [AGENTS.md](./AGENTS.md) | AI エージェント | 動画スクレイピング～JSON 変換のフロー |
| [docs/architecture/MODULES.md](./docs/architecture/MODULES.md) | 実装者 | Phase 4/4.1 全モジュールの役割 |
| [docs/architecture/VIEWS_DESIGN.md](./docs/architecture/VIEWS_DESIGN.md) | 設計者 | Views 設計書 |
| [docs/phases/PHASE4_IMPLEMENTATION.md](./docs/phases/PHASE4_IMPLEMENTATION.md) | 実装者 | Phase 4 実装レポート |
| [docs/phases/PHASE4_1_NOTES.md](./docs/phases/PHASE4_1_NOTES.md) | 実装者 | Phase 4.1 実装メモ・テスト結果 |
| [docs/phases/PHASE4_2_DESIGN.md](./docs/phases/PHASE4_2_DESIGN.md) | 設計者 | Phase 4.2 設計書 |
| [docs/operations/DEPLOYMENT_GUIDE.md](./docs/operations/DEPLOYMENT_GUIDE.md) | 運用者 | デプロイメントガイド |
| [docs/operations/ONBOARDING_COMPETITOR_ANALYTICS.md](./docs/operations/ONBOARDING_COMPETITOR_ANALYTICS.md) | クライアント | クライアント オンボーディングガイド |
| [docs/vision/COMPETITOR_ANALYTICS_V1.md](./docs/vision/COMPETITOR_ANALYTICS_V1.md) | マネジメント | Competitor Analytics ビジョン |

## セットアップ

### 環境変数の設定

#### 1. \.env.example\ から \.env\ を作成
\\\ash
cp .env.example .env
\\\

#### 2. \.env\ を編集して実際のAPIキーを設定
\\\ash
# テキストエディタで .env を開き、以下を編集：
YOUTUBE_API_KEY=sk-proj-xxxxxxxxx  # ← 実際のキーに置き換え
ARCHIVE_DIR=D:\\your\\actual\\path     # ← パスを変更
\\\

#### 3. 確認コマンド
\\\ash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ 設定OK' if os.getenv('YOUTUBE_API_KEY') else '❌ APIキーが見つかりません')"
\\\

## 実行方法

### Views 生成（Phase 4）
\\\ash
python generate_views.py --lecture-ids "01,02,03,04,05" --archive-dir "D:\\AI_Data\\video-insight-spec\\archive" --api-key "YOUR_API_KEY"
\\\

### Weekly Report 生成（Phase 4.1）
\\\ash
python weekly_report_generator.py --lecture-ids "01,02,03,04,05" --archive-dir "D:\\AI_Data\\video-insight-spec\\archive" --output-dir "reports/weekly"
\\\

## ⚠️ セキュリティに関する重要な注意事項

### APIキー漏洩について
本リポジトリの過去のコミット履歴に Google API キー（\AIza...\）が含まれていました。
**該当のAPIキーは既に無効化（Revoke）済みであり、現在利用することはできません。**
コード内に含まれるキーはあくまでサンプルであり、動作確認用です。

### 環境変数の設定方法
ご自身の環境で本システムを動かす場合は、ご自身で取得した有効なAPIキーを用いた \.env\ ファイルを作成してください。
なお、セキュリティ保護のため \.env\ ファイルは \.gitignore\ に登録されており、Gitのコミット対象外となっています。

### セキュリティルール（重要）
⛔ **以下の操作は絶対に行わないでください：**
- \.env\ ファイルを Git にコミット・プッシュすること
- APIキーをコード内にハードコーディングすること
- 認証情報を GitHub Issues や PR コメントに記載すること

✅ **推奨される運用方法：**
- \.env\ は必ず \.gitignore\ で除外（既に設定済み）
- APIキーはローカルの \.env\ ファイルのみに保存
- チームメンバーとは \.env.example\ を共有（ダミー値のみ）
- GitHub Actions 等でのキー運用は Secret として管理

### APIキーの再発行方法
万が一、実際のキーが漏洩した場合：
1. Google Cloud Console でキーを無効化（Revoke）
2. 新しいキーを発行
3. ローカルの \.env\ を更新
4. 旧キーの使用ログを確認し、不正利用がないか確認

## ライセンス
MIT

---
Last Updated: 2026-03-26
