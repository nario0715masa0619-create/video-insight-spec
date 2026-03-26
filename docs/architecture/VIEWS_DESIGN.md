# Views Design Document

## Overview

**views** セクションは insight_spec の中核を成す分析ビューです。**ダッシュボード用の要約ビュー + 代表的なピン（top N）** という "progressive disclosure" の設計思想に基づいています。

---

## Design Philosophy

### 問題設定

Mk2_Core.knowledge_core.center_pins には、1 講座あたり 9～11 個の詳細なピンがあります。クライアント向けのダッシュボード・レポートでは、この 52 個のピンをそのまま見せるのではなく：

1. **その講座がどんな性格か** を一瞬で理解できる
2. **最初にどのピンを見るべきか** が明確
3. **複数講座の比較** が容易

が必要です。

### 解決策：3 つのビューと engagement_score

views セクションで 3 つの異なる切り口を提供し、各ビューでは：
- **集計統計**（distribution）で全体像
- **top N ピン**（N=3）で代表例

を示します。

\\\
views: {
  competitive: メトリクス + トップピン by engagement
  education: 難易度分布 + トップピン by 難易度
  self_improvement: テーマ・ファネル分布 + ファネルフロー
}
\\\

---

## Component 1: engagement_score

### 定義

講座内の各ピンに対して、その「ビジネス価値」を 0.0～1.0 でスコアリングします。

\\\
engagement_score = 0.6 * purity_norm + 0.2 * type_weight + 0.2 * stage_weight
\\\

### 構成要素

#### A) base_purity_score（重み：0.6）

**意味：** ピンがどれだけ「芯を食っているか」の指標

Gemini の自動評価（0～100）を 0.0～1.0 に正規化。

**理由：** 
- 知識の"質"を最も重視する
- 既存データとして利用可能
- Phase 2 で自動算出済み

#### B) type の重み（重み：0.2）

**意味：** ピンの形式によるビジネス価値

\\\python
TYPE_WEIGHT = {
    "framework": 1.0,  # 講座の中核フレームワーク
    "strategy": 0.8,   # 戦略的なアプローチ
    "tactic": 0.6,     # 具体的な戦術
    "concept": 0.4,    # 基本概念
}
\\\

**理由：**
- framework が複数あれば講座の"体"が成立
- concept だけでは実務的価値が低い
- strategy/tactic のバランスが学習効果に寄与

#### D) funnel_stage の重み（重み：0.2）

**意味：** 顧客ファネルのどの段階に貢献するか

\\\python
STAGE_WEIGHT = {
    "クロージング": 1.0,   # 最終成約に直結
    "継続・LTV": 0.9,     # 既存顧客の価値向上
    "比較": 0.8,          # 購買判断を左右
    "教育": 0.7,          # スキルアップ
    "興味": 0.5,          # 初期関心
    "認知": 0.3,          # 認知獲得（最低価値）
}
\\\

**理由：**
- 売上寄与の直接性が高いほど価値
- BtoB/BtoC で重みの調整余地あり
- Phase 4.1 で運用フィードバックから最適化可能

### 計算例

\\\
ピン cp_005:
  - base_purity_score = 91
  - type = "tactic"
  - funnel_stage = "クロージング"

purity_norm = 91 / 100 = 0.91
type_weight = 0.6
stage_weight = 1.0

engagement_score = 0.6 * 0.91 + 0.2 * 0.6 + 0.2 * 1.0
                = 0.546 + 0.12 + 0.2
                = 0.866
\\\

### 特性

- **0.0～1.0 でクリップ：** 異常値対策
- **重み付けは線形：** 運用中のチューニング容易
- **type/stage は離散値：** メンテナンス性が高い

---

## Component 2: views.competitive

### 目的

**YouTube 競争力分析ビュー**。視聴数、いいね、コメント、エンゲージメント率を軸に、この講座の「市場パフォーマンス」を可視化。

### スキーマ

\\\json
{
  "competitive": {
    "###_metadata": {
      "snapshot_timestamp": "2026-03-29T23:59:59Z",
      "snapshot_history": [
        { "timestamp": "...", "view_count": 115830, ... }
      ]
    },
    "metrics": {
      "view_count": 115830,
      "like_count": 1804,
      "comment_count": 48,
      "engagement_rate": 0.016,
      "likes_per_1000_views": 15.57,
      "comments_per_1000_views": 0.41
    },
    "top_pins_by_engagement": [ ... ]  // 上位 3 件
  }
}
\\\

### snapshot_history の用途

**Phase 4 初回：**
\\\
snapshot_history = [
  { timestamp: "2026-03-29", view_count: 115830, like_count: 1804 }
]
\\\

**Phase 4.1 Week 1（1 週間後）：**
\\\
snapshot_history = [
  { timestamp: "2026-03-29", view_count: 115830, like_count: 1804 },
  { timestamp: "2026-04-05", view_count: 118170, like_count: 1890 }
]
\\\

→ delta レポート生成：
\\\
成長率 = (118170 - 115830) / 115830 = 2.02%
likes_growth = (1890 - 1804) / 1804 = 4.77%
\\\

### top_pins_by_engagement の価値

- **初見でビジネスインパクトの大きいピンを 3 つ即座に提示**
- **複数講座比較で「どの講座がどのタイプのピンを多く含むか」を視覚化可能**
- **ダッシュボード実装時に JSON だけで充足可能**

---

## Component 3: views.education

### 目的

**学習ビュー**。難易度別の学習構成と、各レベルで最も学習価値の高いピンを提示。

### スキーマ

\\\json
{
  "education": {
    "difficulty_distribution": {
      "beginner": 9,
      "intermediate": 0,
      "advanced": 0
    },
    "top_pins_by_difficulty": {
      "beginner": [ ... ],      // 上位 3 件
      "intermediate": [],
      "advanced": []
    }
  }
}
\\\

### クライアント向けレポート例

**"この講座は初心者向けです。以下の 3 つを押さえるとコア理解が完成します："**

1. Webマーケティングの基本フレームワーク
2. 検索 vs SNS の集客戦略
3. LPO による購買率向上

---

## Component 4: views.self_improvement

### 目的

**ビジネス視点のビュー**。どのテーマがどのファネル段階で学べるか、成長順序と学習パス を提示。

### スキーマ

\\\json
{
  "self_improvement": {
    "business_theme_distribution": { ... },
    "funnel_stage_distribution": { ... },
    "funnel_flow": [
      {
        "stage": "認知",
        "pin_count": 5,
        "top_themes": ["マーケティング", "集客"],
        "average_difficulty": "beginner"
      },
      ... （計 6 段階）
    ]
  }
}
\\\

### クライアント向けレポート例

**"顧客ファネル全体のカバレッジ："**

\\\
認知（5 pins）   → マーケティング、集客      → 難易度：beginner
教育（2 pins）   → マーケティング、セールス  → 難易度：beginner
比較（0 pins）   → ※未カバー
クロージング（1）→ コンバージョン最適化     → 難易度：beginner
継続・LTV（1）   → SNSマーケティング        → 難易度：beginner
\\\

→ "ファネル下流（クロージング以降）をもっと拡充すると、より完全な講座になる"

---

## Implementation Details

### 1. top N ピン抽出アルゴリズム

\\\python
# Competitive
pins_by_engagement = sorted(center_pins, key=lambda p: calculate_engagement_score(p), reverse=True)
top_3_competitive = pins_by_engagement[:3]

# Education
pins_by_difficulty = {d: [] for d in ['beginner', 'intermediate', 'advanced']}
for pin in center_pins:
    difficulty = pin['labels'].get('difficulty')
    pins_by_difficulty[difficulty].append(pin)

for difficulty in pins_by_difficulty:
    sorted_pins = sorted(pins_by_difficulty[difficulty], key=engagement_score, reverse=True)
    top_3_by_difficulty[difficulty] = sorted_pins[:3]
\\\

### 2. funnel_flow 構築アルゴリズム

\\\python
funnel_order = ["認知", "興味", "比較", "教育", "クロージング", "継続・LTV"]
funnel_flow = []

for stage in funnel_order:
    pins_in_stage = [p for p in center_pins if p['labels']['funnel_stage'] == stage]
    
    # top_themes を抽出
    theme_count = Counter([t for p in pins_in_stage for t in p['labels']['business_theme']])
    top_themes = [t for t, _ in theme_count.most_common(3)]
    
    # average_difficulty を計算
    avg_difficulty = get_most_common_difficulty(pins_in_stage)
    
    funnel_flow.append({
        "stage": stage,
        "pin_count": len(pins_in_stage),
        "top_themes": top_themes,
        "average_difficulty": avg_difficulty
    })
\\\

---

## Weekly Report Integration（Phase 4.1）

### フロー

\\\
Phase 4 生成の views （初期 baseline）
  ↓
1 週間後、weekly_update_views.py 実行
  ↓
同じ構造で YouTube API から最新データを取得
  ↓
snapshot_history に追加
  ↓
delta を計算してレポート生成
  ↓
クライアント向け HTML/PDF レポート配信
\\\

### レポートテンプレート例

\\\markdown
## 週次レポート：Lecture 01

**期間：** 2026-03-29 → 2026-04-05

### Competitive Metrics

| 指標 | 前週 | 今週 | 変化 |
|------|------|------|------|
| Views | 115,830 | 118,170 | +2,340（+2.02%） |
| Likes | 1,804 | 1,890 | +86（+4.77%） |
| Engagement | 1.6% | 1.65% | +0.05pt |

### Education Level

- **Beginner:** 9 pins（変化なし）
- **Intermediate:** 0 pins（変化なし）

### Highlighted Content

このコンテンツの推奨される学習順序：
1. cp_002: Webマーケティング全体像
2. cp_005: LPO と購買最適化
3. cp_009: 3C分析フレームワーク
\\\

---

## Future Extensions

### Phase 4.2: Competitive Analysis

複数講座の views を並べて比較：

\\\json
{
  "comparison": {
    "lecture_01": { "view_count": 115830, "engagement_score_avg": 0.82 },
    "lecture_02": { "view_count": 47734, "engagement_score_avg": 0.78 },
    "lecture_03": { "view_count": 33796, "engagement_score_avg": 0.85 }
  }
}
\\\

### Phase 5: Content Recommendation Engine

engagement_score と view_count のクロス分析で「今後どのテーマを追加すべきか」を提案。

---

**最終更新：** 2026-03-29
**バージョン：** v1.0
