# アーキテクチャと運用方針 (ARCHITECTURE)

## 1. 正本データ（Source of Truth）の定義

当プロジェクトにおけるデータの正本（Source of Truth）は **`insight_spec_{id}.json`** となります。
以前の中間生成物であった `executive_report.json` は**廃止対象**となりました。今後のダッシュボード表示、バッチ処理、データ分析はすべて `insight_spec_{id}.json` を直接参照、またはそこから動的に集計する形で成立させます。

## 2. データ流の図

```text
動画ファイル (.mp4)
   ↓ 
   ↓ (Whisper, FFmpeg, EasyOCR, Gemini によるテキスト化・構造化処理)
   ↓ 
insight_spec_*.json  ← 【ここが正本 (Source of Truth)】
   ↓ 
   ↓ (data_loader.py による動的集計・動的構築・フォールバック)
   ↓ 
Streamlit ダッシュボード表示
   ↓ 
ユーザー (画面閲覧)
```

## 3. 各コンポーネントの役割

- **`streamlit_app/data_loader.py`**:
  `insight_spec_{id}.json` 群を読み込み、ダッシュボードで必要とされる形式に動的に集計・変換します。物理ファイルとしての `executive_report.json` には依存しません。

- **`streamlit_app/env_loader.py`**:
  API キー等の環境変数をユーザーディレクトリ（`~/.video-insight-spec/.env`）などから安全かつ統一的にロードします。

- **バッチスクリプト群 (`scripts/`)**:
  動画の文字起こしや YouTube メタデータの補完、Gemini によるナレッジラベル付与など、`insight_spec` の生成および拡張処理を行います。

- **Streamlit ダッシュボード (`streamlit_app/app.py`)**:
  `data_loader.py` が構築したビューモデルを受け取り、インサイトやナレッジマップをユーザーフレンドリーな UI でレンダリングします。

## 4. 廃止方針の詳細

プロジェクトの健全性を保つため、以下の厳格なルールを定めています。

1. **`executive_report.json` への新規参照の禁止**
   今後、新たに `executive_report.json` を読み書きするコードを追加することは禁止されています。
2. **既存参照の除去**
   旧来のシステムに残っている `executive_report.json` の参照箇所は、発見次第段階的に除去し、`insight_spec` を起点とした動的処理へリファクタリングします。
3. **欠損値の扱い**
   `insight_spec` に未知の値や処理未完了で不足している項目があった場合、勝手に `0` やフェイクデータで埋め合わせることはせず、UI上では「None」または「未算出」として誠実に表現します。
