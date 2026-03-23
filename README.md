# video-insight-spec

YouTube動画から知識ポイント・インサイトを自動抽出するシステム。

## セットアップ

### 1. `.env.example` から `.env` を作成
```bash
cp .env.example .env
```

### 2. `.env` を編集して実際のAPIキーを設定
```bash
YOUTUBE_API_KEY=sk-proj-xxxxxxxxx  # ← 実際のキーに置き換え
```

## ⚠️ セキュリティに関する重要な注意事項

### APIキー漏洩について
本リポジトリの過去のコミット履歴に Google API キー（`AIza...`）が含まれていました。
**該当のAPIキーは既に無効化（Revoke）済みであり、現在利用することはできません。**

### 環境変数の設定方法

#### 1. `.env.example` から `.env` を作成
```bash
cp .env.example .env
```

#### 2. `.env` を編集して実際のAPIキーを設定
```bash
YOUTUBE_API_KEY=sk-proj-xxxxxxxxx  # ← 実際のキーに置き換え
ARCHIVE_DIR=D:\your\actual\path     # ← パスを変更
```

#### 3. 確認コマンド
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ 設定OK' if os.getenv('YOUTUBE_API_KEY') else '❌ APIキーが見つかりません')"
```

### セキュリティルール（重要）

⛔ **以下の操作は絶対に行わないでください：**
- `.env` ファイルを Git にコミット・プッシュすること
- APIキーをコード内にハードコーディングすること
- 認証情報を GitHub Issues や PR コメントに記載すること

✅ **推奨される運用方法：**
- `.env` は必ず `.gitignore` で除外（既に設定済み）
- APIキーはローカルの `.env` ファイルのみに保存
- チームメンバーとは `.env.example` を共有（ダミー値のみ）

## ライセンス
MIT
