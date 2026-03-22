# JSON設計 v1（video-insight-spec）

## 基本コンセプト
- 1 JSON = 1本の動画。
- 3レイヤー構成：
  - `video_meta`：動画の汎用メタ情報。
  - `knowledge_core`：Brain_Marketing_Master.json 準拠の「知恵」。
  - `views`：用途別ビュー（competitive / self_improvement / education など）。

---

## スキーマ（抜粋）

```jsonc
{
  "video_meta": {
    "video_id": "string",
    "channel_id": "string",
    "title": "string",
    "url": "string",
    "published_at": "ISO8601"
  },

  "knowledge_core": {
    "center_pins": [
      {
        "element_id": "string",
        "type": "FACT | LOGIC | SOP",
        "content": "string",
        "base_purity_score": 0-100
      }
    ],
    "knowledge_points": [
      {
        /* Brain_Marketing_Master.json 準拠の動的スキーマ
           （term, logic_structure, algorithm, phenomenon,
            example_change, strategy, methodology, risk_management など） */
      }
    ]
  },

  "views": {
    "competitive": {
      "view_count": 0,
      "like_count": 0,
      "comment_count": 0,
      "performance_score": 0,
      "trend_score": 0,
      "content_role": "education | branding | sales | hiring"
    },
    "self_improvement": {
      /* 将来自社AnalyticsやCVデータを統合する用（現時点は空でOK） */
    },
    "education": {
      /* 教材化・Brain商品化用のラベル・難易度など（将来拡張） */
    }
  }
}

## 追加仕様：サイドカーDB（SQLite）構造

このプロジェクトでは、動画1本ごとのJSONと対になる  
「検索高速化用サイドカー・データベース（SQLite）」を併用します。  
動画内の視覚情報（スライドの文字など）を時間軸でインデックス化するための物理構造は以下の通りです。

### DB物理構造

1. テーブル名  
   - `evidence_index`

2. カラム構成  
   - `element_id` (TEXT)  
     - ノウハウの各要素に対するユニークID。  
       JSON側の `knowledge_core.center_pins` や各 Knowledge 要素と紐づける前提。  
   - `start_ms` / `end_ms` (INTEGER)  
     - 動画内での出現時間（ミリ秒）。  
     - `start_ms` はその要素が画面に現れ始める時刻、`end_ms` は消える時刻。  
   - `visual_text` (TEXT)  
     - Whisperによる音声文字起こしとは別に、画面上から抽出した視覚テキスト（OCR結果など）。  
   - `visual_score` (REAL)  
     - 抽出された視覚テキストの信頼度スコア。  
   - `source_video_path` (TEXT)  
     - 参照元の動画ファイルの物理パス（ローカルパス or ストレージ上のパス）。

3. 運用ルール  
   - JSONとの紐付け  
     - JSON内の各ノウハウ（Value）の根拠となる動画のタイムスタンプを、  
       このテーブルの `start_ms` と一致させて管理する。  
     - `element_id` をキーとして、JSONの知識要素 ↔ サイドカーDBの証拠行を対応付ける。  
   - 検索性の向上  
     - 「〇〇について話している／表示されている場面を動画から探せ」という指示に対して、  
       AIはこの `evidence_index.visual_text` を全文検索し、該当箇所の `start_ms` / `end_ms` を特定する。  
     - 特定したタイムスタンプを使って、動画プレーヤーや別ツールから該当シーンへジャンプできるようにする。

### サイドカーDBの配置ルール

- サイドカーDBは、動画1本ごとのJSONファイルと同じディレクトリに配置する。
- 命名規則：
  - JSON本体：`Mk2_Core_XX.json`
  - サイドカーDB：`Mk2_Sidecar_XX.db`
- `XX` 部分は動画ごとの通し番号または一意なIDで、  
  同じ `XX` を持つ JSON と SQLite ファイルがペアになる前提とする。
- これにより、ツールやAIエージェントは
  1. `Mk2_Core_XX.json` を読み込んで論理情報（知恵・メタ情報）を取得し、
  2. 同じフォルダ内の `Mk2_Sidecar_XX.db` を開いて、視覚情報インデックス（`evidence_index` テーブル）を参照する、
  という2段構造で動画分析を行える。

> メモ：このセクションで定義しているのは**物理DB構造**であり、  
> JSONスキーマとは別レイヤーの「検索インデックス用仕様」です。  
> 実装時は、video-insight-spec のJSONと、このSQLiteサイドカーDBの両方を一貫して更新してください。

