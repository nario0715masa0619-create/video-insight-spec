# JSON Schema Specification

このディレクトリには、video-insight-spec システムの JSON スキーマと実装ドキュメントが含まれています。

## ファイル一覧

| ファイル | 説明 |
|---------|------|
| **JSON_SPEC.md** | 完全な JSON スキーマ仕様（v3.0）。insight_spec_XX.json、Mk2_Core_XX.json、Mk2_Sidecar_XX.db の構造を定義。 |
| **WORKFLOW_IMPLEMENTATION_MAP.md** | ワークフロー実装マップ。各フェーズでのデータフロー、処理ロジック、API 呼び出し。 |

## 主な構造

- **video_meta**: YouTube メタデータ（video_id, channel_id, title, url, published_at）
- **knowledge_core**: 知識体系（center_pins）と Gemini ラベル（business_theme, funnel_stage, difficulty）
- **views**: ビジネス分析ビュー（competitive, education, self_improvement）
- **_metadata**: 処理メタデータ

詳細は [JSON_SPEC.md](JSON_SPEC.md) を参照してください。
