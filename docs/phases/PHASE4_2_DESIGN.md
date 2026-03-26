# Phase 4.2 Design: Competitor Analytics Views

## 1. 既存データモデルの要約

### 1.1 insight_spec 構造（抜粋）

```json
{
  "video_meta": { ... },
  "knowledge_core": {
    "center_pins": [
      {
        "element_id": "cp_001",
        "type": "concept | strategy | tactic | framework",
        "content": "...",
        "base_purity_score": 90,
        "labels": {
          "business_theme": ["マーケティング", "Webマーケティング"],
          "funnel_stage": "認知",
          "difficulty": "beginner"
        }
      }
    ]
  },
  "views": {
    "competitive": { ... },
    "education": { ... },
    "self_improvement": { ... }
  },
  "snapshot_history": [
    {
      "timestamp": "2026-03-26T17:42:33+09:00",
      "view_count": 115834,
      "like_count": 1804,
      "comment_count": 48,
      "engagement_rate": 0.016
    }
  ]
}
```

### 1.2 engagement_score

- 定義：
  - `engagement_score = 0.6 * purity_norm + 0.2 * type_weight + 0.2 * stage_weight`
- type_weight：
  - framework(1.0) > strategy(0.8) > tactic(0.6) > concept(0.4)
- stage_weight：
  - クロージング(1.0) > 継続・LTV(0.9) > 比較(0.8) > 教育(0.7) > 興味(0.5) > 認知(0.3)

### 1.3 views セクション

- competitive：
  - metrics（view/like/comment, engagement_rate など）
  - top_pins_by_engagement（engagement_score 上位 3 件）
- education：
  - difficulty_distribution（beginner/intermediate/advanced）
  - top_pins_by_difficulty（各 difficulty の上位 3 件）
- self_improvement：
  - business_theme_distribution
  - funnel_stage_distribution
  - funnel_flow（stage ごとの pin_count / top_themes / average_difficulty）

### 1.4 snapshot_history と週次レポート

- snapshot_history：
  - 各実行時点での view/like/comment/engagement_rate を JST で記録
- weekly_report：
  - baseline（初回）
  - 2 回目以降：
    - view_count_delta / growth_rate
    - engagement_rate_delta など

---

## 2. Phase 4.2 で追加する比較ビュー

### 2.1 portfolio_view（講座ポートフォリオマップ）

目的：自社・競合それぞれの「講座構造」を俯瞰する。

- 単位：講座ごと
- 指標：
  - role（self / competitor）
  - dominant_funnel_stage（最多 stage）
  - dominant_difficulty（最多 difficulty）
  - total_center_pins
  - latest_view_count / engagement_rate

出力イメージ：

```json
"portfolio_view": [
  {
    "role": "self",
    "lecture_id": "01",
    "title": "...",
    "dominant_funnel_stage": "認知",
    "dominant_difficulty": "beginner",
    "view_count": 115834,
    "engagement_rate": 0.016
  },
  {
    "role": "competitor",
    "lecture_id": "C01",
    "title": "...",
    "dominant_funnel_stage": "クロージング",
    "dominant_difficulty": "beginner",
    "view_count": 98000,
    "engagement_rate": 0.021
  }
]
```

---

### 2.2 growth_view（伸びている講座ランキング）

**仕様**: growth_view は snapshot_history が 2 件以上ある講座のみを対象とする（1 件のみの講座はランキング対象外）。これにより「直近 2 スナップショット間の変化」を正確に計算できます。

目的：ここ数週間でどの講座が伸びているかを把握する。

- 指標（週次）：
  - view_count_delta / growth_rate
  - engagement_rate_delta

出力イメージ：

```json
"growth_view": {
  "top_by_view_growth": [
    {
      "role": "self",
      "lecture_id": "03",
      "title": "...",
      "view_count_delta": 4120,
      "view_count_growth_rate": 0.124
    },
    {
      "role": "competitor",
      "lecture_id": "C02",
      "title": "...",
      "view_count_delta": 3900,
      "view_count_growth_rate": 0.098
    }
  ]
}
```

---

### 2.3 theme_view（テーマ別“勝ち講座”ランキング）

目的：特定テーマでどの講座を推すべきか（自社/競合）を決めやすくする。

- 集計軸：
  - business_theme ごとに講座をグルーピング
  - 各講座の latest_view_count / engagement_rate
  - 代表 center_pin（top_pins_by_engagement の 1 つ）を添付

出力イメージ：

```json
"theme_view": {
  "集客": [
    {
      "role": "self",
      "lecture_id": "01",
      "title": "...",
      "view_count": 115834,
      "engagement_rate": 0.016,
      "representative_pin": {
        "element_id": "cp_009",
        "content": "集客導線全体の設計図…"
      }
    },
    {
      "role": "competitor",
      "lecture_id": "C03",
      "title": "...",
      "view_count": 82000,
      "engagement_rate": 0.019,
      "representative_pin": {
        "element_id": "cp_021",
        "content": "広告からLINE登録までの…"
      }
    }
  ]
}
```

---

## 3. 実装方針メモ

- 既存の `insight_spec + views + snapshot_history` から計算可能な範囲に収める。
- 自社・競合とも同じパイプラインを通し、比較時に `role` で区別する。
- まずは JSON 出力から実装し、HTML レポートは Phase 4.3 以降で拡張。
