# Quality Scoring Enhancement - 設計書 v2.0

## 1. 目的と責務分離

### 1.1 スコアリングの役割
- スコアは「ビュー生成の中間指標」として機能
- 総合点ではなく、3系統のスコアに分離
- 説明可能性と再現性を優先

### 1.2 責務分離（3系統）
knowledge_core: 分類結果の保存
scoring: スコア計算と管理
views: ランキング・可視化用

## 2. スコアリング要素（3系統）

### 2.1 text_quality_score
定義: 文字起こしの欠損・ノイズ・重複の汚染度

測定項目:
- 欠損率、記号ノイズ率、重複率、短小率

計算式:
text_quality_score = 100 - (欠損率×0.25 + ノイズ率×0.25 + 重複率×0.25 + 短小率×0.25)

範囲: 0-100

### 2.2 semantic_purity_score
定義: 抽出トピックの集中度と話題遷移の少なさ

測定項目:
- 主要テーマ占有率 (%)
- 話題遷移の少なさ (%)
- トピック集中度 (%)

計算式:
semantic_purity_score = (主要テーマ占有率×0.4 + 話題遷移スコア×0.3 + 集中度×0.3)

範囲: 0-100

### 2.3 business_fit_score
定義: content_type と business_stage を踏まえた補正値

測定項目:
- content_type の分類信頼度
- business_stage の分類信頼度
- テーマとビジネス価値の相関度

計算式:
business_fit_score = (content_type信頼度×0.35 + stage信頼度×0.35 + テーマ相関×0.3)

範囲: 0-100

## 3. 総合スコア計算

### 3.1 final_score
用途: ランキング・比較・Executive Summary 用

計算式:
final_score = (text_quality_score × 0.35) + (semantic_purity_score × 0.40) + (business_fit_score × 0.25)

範囲: 0-100

## 4. JSON 構造設計

knowledge_core:
- themes: []
- content_type: "tutorial"
- business_stage: "acquisition"
- classification_confidence: {theme, content_type, business_stage}

scoring:
- text_quality_score: 0.91
- semantic_purity_score: 0.76
- business_fit_score: 0.64
- final_score: 0.77
- score_version: "v2.0"
- calculation_timestamp: "2026-04-09T10:30:00Z"

## 5. 実装規則（Perplexity推奨）

### 5.1 重み管理
- 設定ファイル化: config/scoring_weights.json に記載
- 変更時は version を increment

### 5.2 スコア保存戦略
- 部分点を全て保存: text_quality / semantic_purity / business_fit
- 総合点のみ保存は禁止
- ログで後追い検証可能な設計

### 5.3 Version 管理
- score_version は必須フィールド
- v1.0 → v2.0 以上へ更新時、旧スコアとの比較可能にする

### 5.4 丸め処理の明示
- 小数点第2位で丸め（例: 0.77）
- ログに「丸めルール: round(score, 2)」と記載

### 5.5 検証方法
- サンプル動画 20～30 本での人手評価
- スコア vs 人手評価の相関係数を測定
- ズレが大きい場合は重みを再調整

## 6. 実装スケジュール

### Phase 1: 設定ファイル作成
- config/scoring_weights.json 作成
- scoring_rules.json（計算ロジック詳細）

### Phase 2: スコアリングエンジン実装
- scripts/quality_scoring_engine.py
- 3要素の計算ロジック実装

### Phase 3: JSON 更新スクリプト
- scripts/apply_scoring_to_insights.py
- 既存 insight_spec_*.json に scoring セクション追加

### Phase 4: テスト・検証
- サンプル 20～30 本で人手評価
- スコア vs 評価の相関分析

### Phase 5: ドキュメント・レポート統合
- Executive Summary へのスコア表示
- Full Report でランキング表示

## 7. 説明可能性の確保

### 7.1 スコア根拠の明示
各スコアの計算過程をログに記録

### 7.2 再現性の確保
- 同じ入力 → 同じスコア（毎回）
- score_version で世代管理

## 8. 注意点

- ML的厳密さより説明可能性を優先
- 自動生成時の成功率・品質 KPI と連動
- 毎回同じ入力なら同じスコア が大原則
