# Quality Scoring Enhancement - 設計書 v1.0

## 1. 目的
center_pin（一文）の重み（質）を数値化し、顧客向けの改善案・解決策を優先順位付けして提示する

## 2. スコアリング要素

### 2.1 重要キーワード含有率（Weight: 30%）
- 定義: center_pin が業界・課題固有のキーワードを含む度合い
- 測定方法: キーワード辞書との照合
- スコア範囲: 0-100

### 2.2 ビジネス価値度（Weight: 30%）
- 定義: center_pin が顧客のビジネス成果に直結する度合い
- 測定方法: ラベルの business_theme から判定
- スコア範囲: 0-100

### 2.3 実行可能性（Weight: 20%）
- 定義: center_pin の内容が実装・実行しやすい度合い
- 測定方法: テキスト長、具体性、ステップ数
- スコア範囲: 0-100

### 2.4 課題解決度（Weight: 20%）
- 定義: center_pin が顧客の「お困りごと」を解決する度合い
- 測定方法: funnel_stage と business_theme の組み合わせ
- スコア範囲: 0-100

## 3. 計算式

Total Score = 
  (KeywordScore × 0.3) +
  (BusinessValueScore × 0.3) +
  (ExecutabilityScore × 0.2) +
  (ProblemSolvingScore × 0.2)

## 4. 出力例

高スコア center_pin:
- [Score: 92] cp_001: YouTube マーケティング戦略 → 実行案あり
- [Score: 88] cp_003: LPO による CV 改善 → 具体的手順あり

低スコア center_pin:
- [Score: 45] cp_005: 理論的背景の説明 → 実行性低い

## 5. 実装スケジュール
- Phase 1: キーワード辞書作成
- Phase 2: スコアリングアルゴリズム実装
- Phase 3: テスト・検証
