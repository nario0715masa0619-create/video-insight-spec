# Phase 1 Implementation: video-insight-spec Converter

## 概要

このディレクトリ内の実装ファイルは、video-scraper の出力（Mk2_Core_XX.json + Mk2_Sidecar_XX.db）を
video-insight-spec 仕様に準拠した JSON に変換するための Phase 1 実装です。

## ファイル構成

converter/ 
├─ __init__.py 
├─ db_helper.py # Mk2_Sidecar_XX.db 読取 
├─ json_extractor.py # Mk2_Core_XX.json 抽出 
├─ knowledge_analyzer.py # 知識系メトリクス計算 
├─ keyword_extractor.py # キーワード抽出（簡易版） 
├─ views_competitive_builder.py # views.competitive 構築 
└─ insights_converter.py # 最終 JSON 生成

convert_to_insight_spec_phase1.py # メインスクリプト（CLI）

## 使用方法

```bash
python convert_to_insight_spec_phase1.py \
    --lecture-id 01 \
    --archive-dir "D:\Knowledge_Base\Brain_Marketing\archive"
```

## 実装範囲（Phase 1）

✅ 実装済み
- ベースラインKPI層（推定値） view_count, like_count, comment_count, engagement_rate など 
- 中身インサイト層（差別化指標） knowledge_density_per_minute actionability_score content_intelligence_score visual_knowledge_synthesis_ratio competitive_moat_strength など 
- キーワード分析（簡易版：正規表現） primary_theme_keywords keyword_mention_frequency keyword_segment_count 

⏸️ 非実装（Phase 2+） 
- YouTube Analytics API 統合 
- NLP キーワード抽出（JANOME/transformers） 
- keyword_first_appearance_ms 
- トラフィックソース分析 

## データソース 
Phase 1 では以下のみを使用：

Mk2_Core_XX.json - OFLOOP 分解結果（center_pins）
Mk2_Sidecar_XX.db - SQLite 証拠インデックス（evidence_index テーブル）
YouTube API は使用しない（Phase 2 で統合予定）

## 出力形式
```json
{
  "video_meta": { ... },
  "knowledge_core": { 
    "center_pins": [ ... ],
    "knowledge_points": []
  },
  "views": {
    "competitive": { ... },
    "self_improvement": {},
    "education": {}
  },
  "_metadata": { ... }
}
```
詳細は JSON_SPEC.md を参照してください。

## Phase 2 への展開
- YouTube Analytics API による補完
- NLP による自動キーワード抽出
- テストコードの追加
- ドキュメント拡充
