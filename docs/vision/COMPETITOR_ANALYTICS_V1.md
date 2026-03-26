# Competitor Analytics Vision / Service Design v1

## 1. サービス全体像とポジショニング

video-insight-spec は、YouTube ビジネス講座の「中身」と「パフォーマンス」を共通の軸で分解し、  
自社・競合の両方を比較できるようにする分析基盤／サービスです。

### 1.1 既存の自社分析との違い

多くのクライアントは、すでに以下のような自社分析を持っています：

- 再生回数・視聴維持率・登録者増減
- YouTube Studio / GA4 / Looker などのダッシュボード

video-insight-spec が追加で提供する価値は：

- **コンテンツの中身レベルでのラベリング**
  - business_theme（ビジネステーマ）
  - funnel_stage（顧客フェーズ）
  - difficulty（難易度）
  - engagement_score（中身ベースの重要度 proxy）
- 自社と同じ軸で **競合講座も分解** し、同一 taxonomy で比較できること
- 週次での **変化量（delta）を自動レポート** できること

---

## 2. 提供プラン案

### 2.1 自社分析アップグレード（Internal Insight）

既存の自社ダッシュボードを前提に、「中身レベルの分析」を後付けするプラン。

- 対象：
  - クライアント自社のチャンネル／講座のみ
- 提供内容（例）：
  - 各講座の center_pins に対するラベル付与
    - business_theme / funnel_stage / difficulty
  - views セクションによる講座ごとのビュー
    - competitive（YouTube metrics + top_pins_by_engagement）
    - education（難易度分布）
    - self_improvement（ビジネステーマ・ファネル分布）
  - 「ポートフォリオの穴」の可視化
    - 例：認知×beginner は多いが、比較×intermediate がゼロ

### 2.2 競合分解プラン（Competitor Insight）

競合チャンネル／講座を「自社と同じ軸」で分解し、構造を可視化するプラン。

- 対象：
  - 競合チャンネル／プレイリスト（1〜数本）
- 提供内容：
  - 競合講座のポートフォリオ（テーマ × ファネル × 難易度）
  - 競合側の「勝ち講座」とその中身（top_pins_by_engagement）
  - 自社と比較したときに「真似すべき構造」がどこかの仮説

### 2.3 自社 vs 競合ポジショニングプラン（Positioning Insight）

自社と競合をまとめて比較し、「どこで戦うか」を決めるためのプラン。

- 対象：
  - 自社チャンネル＋複数競合チャンネル
- 提供内容（例）：
  - テーマ別・ファネル別の講座分布
    - 自社が優位なゾーン／競合が強いゾーン
  - ここ数週間の伸び率比較（view_count / engagement_rate）
  - テーマ別の「推し講座」一覧（自社・競合それぞれ）
