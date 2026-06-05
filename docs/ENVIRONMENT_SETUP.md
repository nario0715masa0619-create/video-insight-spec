# 環境変数セットアップガイド (ENVIRONMENT SETUP)

## 1. はじめに
本ドキュメントは、`video-insight-spec` プロジェクトを実行するための環境変数の設定方法を記載しています。

> [!WARNING]
> **【重要】データ正本に関する方針**
> 当プロジェクトでは `insight_spec_{id}.json` が唯一の正本（Source of Truth）です。
> 過去に利用されていた `executive_report.json` は廃止対象となっており、今後の新規実装・運用・ドキュメントにおいて参照することは禁止されています。

## 2. 必須環境変数の設定方法
バッチ処理および Streamlit アプリの実行には、以下の API キーが必要です。

- **`YOUTUBE_API_KEY`**: YouTube データ取得用 (必須)
- **`GEMINI_API_KEY`**: 動画内容のインサイトラベル付与・テキスト抽出用 (必須)
- **`OPENAI_API_KEY`**: (オプション) 将来の拡張・一部機能用

## 3. `.env` ファイルの配置
プロジェクトではセキュリティの観点から、リポジトリ内ではなくユーザーディレクトリに `.env` ファイルを配置する運用としています。

- **配置パス**: `C:\Users\nario\.video-insight-spec\.env`
- **記入例**:
```env
YOUTUBE_API_KEY=AIzaSy...
GEMINI_API_KEY=AQ.A...
OPENAI_API_KEY=sk-...
```

> [!NOTE]
> `bootstrap_user_env.ps1` を実行することで、このディレクトリと空の `.env` ファイルを自動的に作成できます。作成後、テキストエディタでご自身の API キーを記入してください。

## 4. 確認方法
環境変数が正しく設定されているかを確認するためには、プロジェクトルートから以下のスクリプトを実行します。

```bash
python scripts/check_environment.py
```

**【成功時の出力例】**
```
✅ YOUTUBE_API_KEY: 設定済み
✅ GEMINI_API_KEY: 設定済み
```

## 5. トラブルシューティング

**Q. API キーが認識されない場合**
- `.env` ファイルのフォーマットが正しいか（空白が入っていないか、クォーテーションで括られていないか）確認してください。
- PowerShell 上で既に空の環境変数がロードされてしまっている場合は、PowerShell を再起動するか `$env:GEMINI_API_KEY=""` などでクリアしてから再試行してください。

**Q. `.env` ファイルが見つからない場合**
- `C:\Users\nario\.video-insight-spec\.env` が存在するか確認してください。
- 存在しない場合は、`bootstrap_user_env.ps1` を再実行するか、手動でフォルダとファイルを作成してください。
