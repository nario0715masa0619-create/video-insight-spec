# video-insight-spec

**YouTube動画から『実行可能な知恵』を抽出し、JSON と SQLite で蓄積する仕組みの仕様書・設計リポジトリ。**

## このリポジトリについて

`video-insight-spec` は、以下を統括する「スキーマ・仕様設計の中核」です：

- **JSON スキーマ定義** (`JSON_SPEC.md`)：1本の動画ごとの知識構造
- **サイドカー DB 設計** (`JSON_SPEC.md` の追記セクション）：時間軸インデックス
- **AI エージェント向けマニュアル** (`AGENTS.md`)：実装・拡張時の指針
- **実装ガイダンス** (PHASE*.md)：各フェーズでの具体的な処理仕様

> 💡 **実装コードや API キーなどの機密情報は、別リポジトリ（`video-scraper` など）で管理**しています。

## ドキュメント案内

| ドキュメント | 対象者 | 概要 |
|-----------|--------|------|
| [JSON_SPEC.md](./JSON_SPEC.md) | 設計者・実装者 | JSON スキーマと DB 構造の完全仕様 |
| [AGENTS.md](./AGENTS.md) | AI エージェント | 動画スクレイピング～JSON 変換のフロー |
| [PHASE1_IMPLEMENTATION.md](./PHASE1_IMPLEMENTATION.md) | 実装者 | Phase 1（基本 JSON 化）の詳細 |
| [PHASE2_2_YOUTUBE_API_INTEGRATION.md](./PHASE2_2_YOUTUBE_API_INTEGRATION.md) | 実装者 | Phase 2.2（YouTube メトリクス取得）の仕様 |
| [PHASE2_2_1_ENGAGEMENT_METRICS.md](./PHASE2_2_1_ENGAGEMENT_METRICS.md) | 実装者 | Phase 2.2.1（エンゲージメント指標計算）の仕様 |
| [PHASE2_2_2_OCR_TEXT_CLEANING.md](./PHASE2_2_2_OCR_TEXT_CLEANING.md) | 実装者 | Phase 2.2.2（OCR テキストクリーニング）の仕様 |

## セットアップ

### 環境変数の設定

#### 1. `.env.example` から `.env` を作成
```bash
cp .env.example .env
```

#### 2. `.env` を編集して実際のAPIキーを設定
```bash
# テキストエディタで .env を開き、以下を編集：
YOUTUBE_API_KEY=sk-proj-xxxxxxxxx  # ← 実際のキーに置き換え
ARCHIVE_DIR=D:\your\actual\path     # ← パスを変更
```

#### 3. 確認コマンド
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ 設定OK' if os.getenv('YOUTUBE_API_KEY') else '❌ APIキーが見つかりません')"
```

## ⚠️ セキュリティに関する重要な注意事項

### APIキー漏洩について
本リポジトリの過去のコミット履歴に Google API キー（`AIza...`）が含まれていました。
**該当のAPIキーは既に無効化（Revoke）済みであり、現在利用することはできません。**
コード内に含まれるキーはあくまでサンプルであり、動作確認用です。

### 環境変数の設定方法
ご自身の環境で本システムを動かす場合は、ご自身で取得した有効なAPIキーを用いた `.env` ファイルを作成してください。
なお、セキュリティ保護のため `.env` ファイルは `.gitignore` に登録されており、Gitのコミット対象外となっています。

### セキュリティルール（重要）
⛔ **以下の操作は絶対に行わないでください：**
- `.env` ファイルを Git にコミット・プッシュすること
- APIキーをコード内にハードコーディングすること
- 認証情報を GitHub Issues や PR コメントに記載すること

✅ **推奨される運用方法：**
- `.env` は必ず `.gitignore` で除外（既に設定済み）
- APIキーはローカルの `.env` ファイルのみに保存
- チームメンバーとは `.env.example` を共有（ダミー値のみ）
- GitHub Actions 等でのキー運用は Secret として管理

### APIキーの再発行方法
万が一、実際のキーが漏洩した場合：
1. Google Cloud Console でキーを無効化（Revoke）
2. 新しいキーを発行
3. ローカルの `.env` を更新
4. 旧キーの使用ログを確認し、不正利用がないか確認

## ライセンス
MIT
