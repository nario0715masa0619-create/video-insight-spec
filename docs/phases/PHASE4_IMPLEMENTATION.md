# Phase 4: Views 生成・YouTube Analytics 統合

**完了日**: 2026-03-26  
**ステータス**: ✅ 完了

## 実装概要

Phase 4 では、各動画の知識体系を「views」という複合指標として可視化し、YouTube Analytics API と連携してリアルタイムメトリクスを取得しました。

## 実装ファイル

### 1. engagement_scorer.py
複合スコアリングロジック

\\\python
engagement_score = 0.6 * purity_norm + 0.2 * type_weight + 0.2 * stage_weight
\\\

**重み定義**:
- purity_norm: base_purity_score を 0-1 に正規化
- type_weight: framework(1.0) > strategy(0.8) > tactic(0.6) > concept(0.4)
- stage_weight: クロージング(1.0) > 継続・LTV(0.9) > 比較(0.8) > 教育(0.7) > 興味(0.5) > 認知(0.3)

### 2. views_generator_service.py
3 つのビューを生成するメインサービス

**生成される views**:
- **competitive**: YouTube メトリクス + engagement スコア top 3
- **education**: 難易度分布 + 難易度別 top 3 pins
- **self_improvement**: テーマ分布 + ファネル流分析

### 3. youtube_metadata_service.py（拡張）
YouTube Analytics API の統合

新規メソッド:
\\\python
def get_video_analytics(self, video_id: str) -> Dict[str, Any]:
    # view_count, like_count, comment_count を取得
\\\

### 4. generate_views.py
CLI メインスクリプト

**使用方法**:
\\\ash
python generate_views.py \\
  --lecture-ids "01,02,03,04,05" \\
  --archive-dir "D:\AI_Data\video-insight-spec\archive" \\
  --api-key "YOUR_YOUTUBE_API_KEY"
\\\

### 5. quality_check_phase4.py
品質検査スクリプト

**チェック項目**:
- views.competitive の metrics が null でない
- top_pins_by_engagement が 3 個存在
- difficulty_distribution の合計が center_pins 総数と一致
- funnel_flow の pin_count 合計が center_pins 総数と一致

**実績**: 40/40 合格（5 講座 × 8 チェック）

## メトリクス実績

| 講座 | views | likes | comments | engagement |
|------|-------|-------|----------|------------|
| 01 | 115,834 | 1,804 | 48 | 2.0% |
| 02 | 47,736 | 776 | 24 | 1.6% |
| 03 | 33,800 | 619 | 21 | 1.9% |
| 04 | 26,024 | 432 | 23 | 1.7% |
| 05 | 21,064 | 310 | 26 | 1.6% |

## JSON スキーマ変更

### insight_spec_XX.json に追加

\\\json
{
  "views": {
    "competitive": {
      "metrics": {
        "view_count": 115834,
        "like_count": 1804,
        "comment_count": 48,
        "engagement_rate": 0.02,
        "likes_per_1000_views": 15.57,
        "comments_per_1000_views": 0.41
      },
      "top_pins_by_engagement": [
        {
          "element_id": "cp_009",
          "type": "framework",
          "content": "...",
          "business_theme": ["マーケティング"],
          "funnel_stage": "教育",
          "engagement_score": 0.9
        }
      ],
      "snapshot_timestamp": "2026-03-26T07:52:19Z"
    },
    "education": {
      "difficulty_distribution": {
        "beginner": 9,
        "intermediate": 0,
        "advanced": 0
      },
      "top_pins_by_difficulty": {
        "beginner": [...]
      }
    },
    "self_improvement": {
      "business_theme_distribution": {...},
      "funnel_stage_distribution": {...},
      "funnel_flow": [...]
    }
  }
}
\\\

## トラブルシューティング

### YouTube API キーが設定されていない
\\\ash
# .env に YOUTUBE_API_KEY を設定するか
python generate_views.py --api-key "YOUR_KEY"
\\\

### video_id が lecture_id になっている場合
\\\powershell
# insight_spec JSON の video_meta.video_id を URL から抽出して修正
\\\

## 次のステップ（Phase 4.1）

### 週次レポート生成
- 初期 snapshot（Phase 4）との比較
- 成長率計算
- HTML/PDF レポート生成
- メール配信

**実装予定**: 2026-04-02

---

**Merged to main**: 2026-03-26
