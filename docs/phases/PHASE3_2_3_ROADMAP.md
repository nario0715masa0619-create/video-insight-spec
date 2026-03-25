# Phase 3.2・3.3 ロードマップ

## Phase 3.2: ライブラリ移行・API 統合（予定）

### 1. google.generativeai → google.genai への移行
- **現状**: FutureWarning が出ている（deprecated パッケージ）
- **作業内容**:
  - GeminiLLMClient を google.genai API に対応させる
  - API 呼び出し方式の変更
  - テスト実行による品質検証
- **予定作業時間**: 2-3 時間
- **優先度**: 中（現在は動作しているが、今後の保守性を考慮）

### 2. YouTube API 統合（Antigravity の活用）
- **現状**: YouTube API は未統合。エンゲージメント指標（likes, comments, views）が取得されていない
- **リソース**: scripts/dev/phase2_2_antigravity_full.py に実装済み
- **作業内容**:
  - Antigravity を現パイプラインに統合
  - YouTube メトリクスを Mk2_Core に追加
  - engagement_rate などの指標を計算
  - 既存 52 ピンで品質検証
- **予定作業時間**: 4-6 時間
- **優先度**: 中（「重要度スコア」精度向上に寄与）

## Phase 3.3: テスト拡張・本番化

### 1. 単体テスト拡張
- GeminiLLMClient の単体テスト（Mock LLM）
- CenterPinLabelingService のバリデーションテスト
- InsightSpecRepository の I/O テスト

### 2. 統合テスト
- 全パイプライン（YouTube → MP4 → Mk2_Core → insight_spec → labeled JSON）

### 3. ドキュメント・デプロイ
- README 最終更新
- DEPLOYMENT.md 作成
- 本番運用ガイド

---

**作成日**: 2026-03-25
**作成者**: Development Team
