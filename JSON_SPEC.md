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
