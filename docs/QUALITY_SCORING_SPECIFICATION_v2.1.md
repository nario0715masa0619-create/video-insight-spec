# Quality Scoring Engine v2.1 - 仕様書

## 1. 目的

YouTube 動画から抽出された center_pin（学習ポイント）に対し、以下の品質指標を計算し、
経営向けレポート（Executive Summary / Portfolio View など）の補助指標として利用する。

- テキスト品質（transcription loss, noise, duplication）
- セマンティック純度（テーマの集中度）
- ビジネス適合度（content_type, business_stage, theme の関連性）

## 2. 設計方針

### 2.1 ハードコードの位置付け

**原則: テーマ正規化ルールは JSON（data-driven）として管理する**

- Python コードに ハードコードしない
- config/scoring_rules.json に集約
- ルール変更 = JSON 変更のみ（コード変更不要）
- Git diff で履歴管理可能

### 2.2 なぜハードコードなのか

1. **説明可能性**: 「なぜこのテーマをこのカテゴリに分類したか」を明示できる
2. **再現性**: 「いつ見ても同じ結果」が保証される
3. **経営向け**: モデル評価ではなく「レポート補助指標」なので、一貫性が最優先

### 2.3 「有限ラベル」を前提とする

- テーマの canonical（正規化後）は有限リスト（6-8 個）
- 完全自動クラスタリング（embedding など）は目指さない
- マスタ自体の生成・更新を段階的に自動化する

## 3. JSON 構造と責務分離

### 3.1 JSON 階層

knowledge_core に scoring セクションを追加：

scoring:
  text_quality_score: 0.91
  semantic_purity_score: 0.74
  business_fit_score: 0.64
  quality_score: 0.81
  ranking_score: 0.77
  score_version: "v2.1"
  rules_version: "1.0"
  calculation_timestamp: "2026-04-09T14:28:10Z"

### 3.2 責務分離

knowledge_core: 中心知識、スコア結果（JSON）
config/scoring_rules.json: テーマルール（Git管理）
quality_scoring_engine.py: 計算処理（Python）
views: レポート表示（JSON）

## 4. スコアリング計算式

### 4.1 text_quality_score

計算式:
text_quality_score = 1 - (0.25*missing_rate + 0.25*noise_rate + 0.25*duplication_rate + 0.25*short_fragment_rate)

missing_rate:
- center_pins が空 → 0.2
- 存在 → 0.0

noise_rate: config の固定値（デフォルト 0.05）
duplication_rate: config の固定値（デフォルト 0.02）
short_fragment_rate:
- 平均テキスト長 < 50文字 → 0.1
- else → 0.0

範囲: 0.0 ～ 1.0（clamped）

### 4.2 semantic_purity_score

計算式:
semantic_purity_score = 0.4*dominant_theme_ratio + 0.3*topic_entropy_score + 0.3*topic_transition_stability

dominant_theme_ratio:
- 最頻出 canonical テーマの占有率
- count(most_common) / len(all_canonical_themes)

topic_entropy_score:
- テーマ分布のエントロピー（正規化）
- 1 - (entropy / max_entropy)

topic_transition_stability:
- config の固定値（デフォルト 0.75）

重要: テーマは必ず正規化してから計算
raw_theme → normalize_theme() → canonical_theme

範囲: 0.0 ～ 1.0（clamped）

### 4.3 business_fit_score

計算式:
business_fit_score = 0.35*content_type_conf + 0.35*business_stage_conf + 0.3*theme_business_value

content_type_conf:
- knowledge_core.classification_confidence.content_type から取得
- デフォルト 0.5

business_stage_conf:
- knowledge_core.classification_confidence.business_stage から取得
- デフォルト 0.5

theme_business_value:
- canonical テーマごとの価値スコア
- config/scoring_rules.json の business_fit_mapping から取得
- デフォルト 0.5

範囲: 0.0 ～ 1.0（clamped）

### 4.4 quality_score と ranking_score

quality_score 計算式:
quality_score = 0.45*text_quality_score + 0.55*semantic_purity_score

用途: テキスト・テーマの品質を単一指標で表現
範囲: 0.0 ～ 1.0

ranking_score 計算式:
ranking_score = 0.75*quality_score + 0.25*business_fit_score

用途: Portfolio View / Growth View でのソート
範囲: 0.0 ～ 1.0

## 5. テーマ正規化（Theme Normalization）

### 5.1 目的

raw_theme（Gemini が出力したラベル）を
canonical_theme（制御された有限リスト）に統一する

例:
- "SNSマーケティング" → "マーケティング"
- "商品開発" → "プロダクト開発"
- "市場分析" → "分析"

### 5.2 ルール管理場所

config/scoring_rules.json 内の theme_normalization セクション

構造:
- mapping: raw_theme → canonical_theme の辞書
- groups: canonical_theme の説明・親ドメイン定義
- changelog: バージョン履歴

### 5.3 正規化アルゴリズム

入力: raw_theme, rules
出力: (canonical_theme, source)

処理順序:
1. canonical_theme が JSON に存在？ → 使用、source="canonical"
2. raw_theme が mapping に存在？ → 使用、source="rules"
3. どちらもなし → raw_theme のまま、source="raw"（警告を記録）

## 6. 出力形式

### 6.1 score_insight_json() の戻り値

戻り値は Python 辞書：

{
  "classification_confidence": {
    "theme": 0.82,
    "content_type": 0.74,
    "business_stage": 0.68
  },
  "scoring": {
    "text_quality_score": 0.91,
    "semantic_purity_score": 0.74,
    "business_fit_score": 0.64,
    "quality_score": 0.81,
    "ranking_score": 0.77,
    "score_version": "v2.1",
    "rules_version": "1.0",
    "theme_normalization_version": "1.0",
    "calculation_timestamp": "2026-04-09T14:28:10Z"
  },
  "score_details": { ... },
  "warnings": []
}

### 6.2 score_details に含まれる項目

text_quality_score の詳細:
- missing_rate, noise_rate, duplication_rate, short_fragment_rate
- total_texts, avg_text_length

semantic_purity_score の詳細:
- dominant_theme_ratio, topic_entropy_score
- unique_canonical_themes, total_theme_mentions
- normalized_theme_counts（辞書）

business_fit_score の詳細:
- content_type_confidence, business_stage_confidence
- theme_business_value_score

### 6.3 warnings リスト

warnings は問題が発生した場合に記録される配列

警告タイプ:

insufficient_text_data:
- 原因: center_pins が空
- 対応: semantic_purity_score = 0.5（デフォルト）

missing_classification_confidence:
- 原因: classification_confidence が無い
- 対応: 各 confidence = 0.5（デフォルト）

unmapped_theme:
- 原因: theme_normalization.mapping に無い raw_theme
- 対応: raw_theme のまま使用

no_center_pins:
- 原因: center_pins 配列が空
- 対応: text_quality_score = 0.5（デフォルト）

no_themes_found:
- 原因: center_pins からテーマが抽出されない
- 対応: semantic_purity_score = 0.5（デフォルト）

## 7. 実装要件

### 7.1 関数一覧

load_scoring_config(weights_path, rules_path):
- 入力: ファイルパス
- 出力: (weights, rules) 辞書
- 責務: JSON ロード

extract_text_units(knowledge_core):
- 入力: knowledge_core 辞書
- 出力: (center_pin_texts, knowledge_point_texts)
- 責務: テキスト抽出

normalize_theme(raw_theme, rules):
- 入力: raw_theme, rules 辞書
- 出力: (canonical_theme, source)
- 責務: 単一テーマ正規化

normalize_themes(raw_themes, rules):
- 入力: raw_themes リスト, rules 辞書
- 出力: [canonical_themes] リスト
- 責務: 複数テーマ正規化

calculate_text_quality_score(center_pin_texts, knowledge_point_texts):
- 出力: (score, details)
- 責務: テキスト品質計算

calculate_semantic_purity_score(knowledge_core, rules):
- 出力: (score, details)
- 責務: セマンティック純度計算

calculate_business_fit_score(knowledge_core, rules):
- 出力: (score, details)
- 責務: ビジネス適合度計算

calculate_quality_score(text_quality_score, semantic_purity_score):
- 出力: score
- 責務: 統合品質スコア計算

calculate_ranking_score(quality_score, business_fit_score):
- 出力: score
- 責務: ランキングスコア計算

build_scoring_result(insight_json, weights, rules):
- 出力: result_dict
- 責務: 全スコア計算・結果構築

score_insight_json(insight_json, weights_path, rules_path):
- メインエントリーポイント
- 出力: result_dict

### 7.2 重要な実装特性

Deterministic:
- 同じ入力 + 同じ rules_version → 必ず同じ出力
- ランダム性なし
- 浮動小数点演算は小数点第2位で丸める

No Side Effects:
- JSON ファイル書き込みなし
- ファイル操作は load_scoring_config のみ
- apply_scoring_to_insights.py で JSON 更新を実施

Configurable:
- すべての定数は config/scoring_rules.json から読み込み
- Python コードに魔法数はない

Explainable:
- score_details に中間値を完全に保持
- normalization_log でテーマ正規化の経路を記録
- warnings で問題を明示

### 7.3 スコアの丸め方

すべてのスコアは小数点第2位で丸める：

round(score, 2)

例: 0.8123456 → 0.81

## 8. 段階的進化パス

### Phase 1（現在）: 手動マスタ

現状:
- scoring_rules.json に手動で theme_normalization を記述
- quality_scoring_engine は JSON lookup のみ
- Gemini は business_theme（raw）のみ出力

特徴:
- 完全に説明可能
- ルール変更が容易
- スケール: 6 insight_spec, ~60 unique themes

### Phase 2（数ヶ月後）: 半自動生成

予定:
- unique themes を自動抽出スクリプト作成
- Gemini に「この themes をクラスタ化」と指示
- JSON を半自動生成（人間確認後 commit）
- 既存マスタを段階的に置き換え

特徴:
- スケール: 30-50 insight_spec
- ルール更新を自動化
- 人間が最終確認

### Phase 3（さらに先）: Embedding ベース補正

予定:
- canonical は有限ラベルのまま維持
- 未知テーマ → embedding で最近接 canonical へ自動アタッチ
- ただしスコア計算は常に離散ラベル前提

特徴:
- 完全自動化ではない
- canonical の有限性を維持
- 説明可能性を損なわない

## 9. 版管理（Version Management）

### 9.1 version フィールド

各スコアには3つの version を記録：

score_version: "v2.1"
- quality_scoring_engine.py 自体のバージョン
- アルゴリズム変更時に上げる
- 例: 重み付けの変更 → v2.2

rules_version: "1.0"
- config/scoring_rules.json 全体のバージョン
- テーママッピング・ビジネス価値設定が変わった時に上げる

theme_normalization_version: "1.0"
- theme_normalization セクション専用のバージョン
- テーマルール更新のみで上げられる

calculation_timestamp: "2026-04-09T14:28:10Z"
- ISO 8601 形式
- どの時刻で計算されたかを記録

### 9.2 ルール更新時の手順

1. config/scoring_rules.json を編集
2. theme_normalization.version を上げる（例: 1.0 → 1.1）
3. theme_normalization.changelog にエントリを追加
4. Git commit
5. 既存 insight_spec JSON を再スコアリング
6. スコア変動を確認

### 9.3 スコア比較時の注意

異なる rules_version で計算したスコアは比較しない
- 必ず「どの version で計算したか」を確認
- 差分の原因は rules 変更にある可能性

## 10. テスト・検証戦略

### 10.1 単体テスト

normalize_theme():
- mapping に存在するテーマ → 正規化できるか
- mapping に無いテーマ → raw のまま返すか
- source フィールドが正しいか

各スコア計算関数:
- 境界値（0.0, 1.0）のテスト
- 空入力時の処理
- warning 生成の確認

### 10.2 統合テスト

全 insight_spec ファイル（6 本）を処理:
- insight_spec_01.json ～ 05.json
- insight_spec_mirirepi.json

確認項目:
- score_details が完全か
- normalized_theme_counts が正しいか
- warnings が適切か
- スコアの整合性（quality_score の計算が正確か）

### 10.3 人手評価（Phase 2 以降）

20～30 サンプル動画で検証:
- semantic_purity_score と人間評価を比較
- 相関係数を計算
- 重み付けの調整が必要か判定

目標相関: > 0.7

## 11. FAQ

### Q1: なぜ embedding ではなくハードコードなのか？

A: このプロジェクトはモデル評価ではなく「経営向けレポートの補助指標」。

重要な特性:
- いつ見ても同じ結果
- なぜそう分類したか説明できる
- 一貫性が最優先

embedding は「後で必要になれば」Phase 3 で足せば良い。

### Q2: ルールが増え続けたら管理できるか？

A: Phase 2 で自動生成に移行。

Gemini に「この 100 テーマを 8 個のカテゴリに分類」と言わせれば、
マスタ管理は自動化できる。
JSON 管理は同じ仕組みで継続可能。

### Q3: Gemini が違う分類をしたら？

A: business_theme_canonical（Gemini 出力）と 
theme_normalization（ルール）の二段構え。

ルールで「Gemini のゆらぎ」を補正できる。
Phase 1 では raw_theme のみなので問題ない。

### Q4: スコアが変わったのはなぜ？

A: 必ず rules_version を確認。

スコア変動の原因:
- rules_version が上がっている → 仕様変更
- rules_version が同じ → 入力データの違い

## 12. 付録: config/scoring_rules.json 構造

### 12.1 最小構成

{
  "version": "v2.1",
  "rules_version": "1.0",
  "text_quality_thresholds": {
    "missing_rate_threshold": 0.3,
    "noise_rate_threshold": 0.2,
    "duplication_rate_threshold": 0.25,
    "short_fragment_min_tokens": 10
  },
  "normalization": {
    "method": "minmax",
    "output_range": [0.0, 1.0],
    "rounding_decimal_places": 2
  },
  "business_fit_mapping": {
    "content_type": {
      "tutorial": 0.9,
      "webinar": 0.85,
      "sales_pitch": 0.7,
      "awareness": 0.6,
      "unknown": 0.5
    },
    "business_stage": {
      "acquisition": 0.8,
      "nurture": 0.75,
      "retention": 0.7,
      "upsell": 0.65,
      "unknown": 0.5
    },
    "theme_business_value": {
      "マーケティング": 0.95,
      "プロダクト開発": 0.8,
      "分析": 0.85,
      "セールス": 0.9
    }
  },
  "theme_normalization": {
    "version": "1.0",
    "mapping": { ... },
    "groups": { ... },
    "changelog": [ ... ]
  }
}

### 12.2 theme_normalization の詳細構造

"theme_normalization": {
  "version": "1.0",
  "created_at": "2026-04-09",
  "created_by": "manual_curation",
  "mapping": {
    "マーケティング": "マーケティング",
    "Webマーケティング": "マーケティング",
    "SNSマーケティング": "マーケティング",
    "ダイレクトレスポンスマーケティング": "マーケティング",
    "広告": "マーケティング",
    "商品開発": "プロダクト開発",
    "プロダクト開発": "プロダクト開発",
    "市場分析": "分析",
    "データ分析": "分析",
    "営業": "セールス",
    "カスタマーサクセス": "カスタマーサクセス"
  },
  "groups": {
    "マーケティング": {
      "description": "集客・販促・広告運用",
      "parent_domain": "go_to_market"
    },
    "プロダクト開発": {
      "description": "商品・サービス開発",
      "parent_domain": "product"
    },
    "分析": {
      "description": "市場・データ分析",
      "parent_domain": "analytics"
    },
    "セールス": {
      "description": "営業・販売",
      "parent_domain": "sales"
    },
    "カスタマーサクセス": {
      "description": "顧客支援・LTV最大化",
      "parent_domain": "post_sales"
    }
  },
  "changelog": [
    {
      "version": "1.0",
      "date": "2026-04-09",
      "changes": "Initial mapping from 60 themes to 5 canonical",
      "source": "manual_curation",
      "themes_mapped": 40
    }
  ]
}

## 13. 実装チェックリスト

### 13.1 即座の実装タスク

- [ ] normalize_theme() 関数確認
  質問: JSON lookup のみか？source タプル返却か？

- [ ] normalize_themes() 関数確認
  質問: リスト全体を正規化できるか？

- [ ] calculate_semantic_purity_score() の更新
  質問: canonical ベースで計算しているか？
  質問: normalization_log を返却しているか？

- [ ] score_details に以下が含まれているか確認
  質問: normalized_theme_counts が出力されているか？
  質問: unique_canonical_themes が出力されているか？

- [ ] scoring セクションに version フィールドが全て含まれているか
  質問: theme_normalization_version を記録しているか？
  質問: calculation_timestamp を ISO 8601 で記録しているか？

### 13.2 検証タスク

- [ ] test_scoring_v2.py を実行して出力確認
  期待値: semantic_purity_score が改善されているか？
  期待値: warnings が正しく生成されているか？

- [ ] 全 6 ファイルで再スコアリング
  期待値: スコアが安定しているか？
  期待値: score_details に矛盾がないか？

- [ ] Git に仕様書をコミット
  コマンド: git add docs/QUALITY_SCORING_SPECIFICATION_v2.1.md
  コマンド: git commit -m "docs: Quality Scoring Engine v2.1 仕様書完成"










## 18. Phase 7-4: Embedding Integration

### 18.1 実装概要
Phase 7-3 後に残存した 6 個の unmapped テーマに対して、Sentence Transformer (all-MiniLM-L6-v2) を使用した embedding ベースのクラスタリングを実装。各テーマの embedding を計算し、既存の 6 canonical との cosine similarity を比較して自動マッピング。

### 18.2 アルゴリズム
1. **Embedding モデルロード**: sentence-transformers/all-MiniLM-L6-v2 (384 次元)
2. **Canonical 代表テーマ取得**: 各 canonical から最初の 5 テーマを抽出
3. **類似度計算**: unmapped テーマと各 canonical の代表テーマ群との cosine similarity を計算
4. **最高スコア選択**: 最も高い similarity を示す canonical を推奨
5. **手動レビュー**: 妥当性を確認し、必要に応じて修正

### 18.3 マッピング結果（6 個）
| raw_theme | 推奨 canonical | 信頼度 | 状態 |
|---|---|---|---|
| コンテンツ制作 | マーケティング | 0.78 | ✅ |
| コンバージョン改善 | マーケティング | 0.81 | ✅ |
| 広告運用 | マーケティング | 0.85 | ✅ 修正 |
| 行動心理学 | 分析 | 0.45 | ✅ |
| 動画マーケティング | マーケティング | 0.87 | ✅ |
| 動画編集 | プロダクト開発 | 0.80 | ✅ 修正 |

### 18.4 スコア改善
- 平均 semantic_purity: 0.59 → 0.61 (+0.02)
- insight_spec_mirirepi: 0.56 → 0.76 (+0.20)
- insight_spec_04: 0.72 → 0.75 (+0.03)

### 18.5 実装上の注意
- Embedding モデルは固定（all-MiniLM-L6-v2）。日本語対応で多言語対応。
- Canonical 数は固定（6 個）。新規 canonical の自動生成は禁止。
- マッピング結果は常に human review を経て確定。
- embedding confidence (0.45–0.87) は参考値。最終的には手動判断を優先。

### 18.6 今後の拡張（Phase 3 後期）
- Embedding モデルの fine-tuning （domain-specific）
- Confidence threshold の動的調整
- cluster ごとの embedding centroid 計算

