# Phase 3.2・3.3 ロードマップ

## 優先順位・実施順序

### 推奨順序：Phase 3.2 → Phase 3.3

#### Phase 3.2: google.generativeai → google.genai 移行（高優先度）
- **所要時間**: 2-3 時間
- **難易度**: 低
- **リスク**: 低
- **理由**:
  - 現在 FutureWarning が毎回表示される（体験悪化）
  - 単純な置き換えで機能変化なし
  - 完了後は API が新しい状態 → Phase 3.3 で堅牢な実装が可能
  - 時間効率が良い（午前中で完了の可能性）

#### Phase 3.3: YouTube API 統合（中優先度）
- **所要時間**: 4-6 時間
- **難易度**: 中
- **リスク**: 中
- **理由**:
  - Phase 3.2 完了後に実施することで、新機能追加が堅牢に
  - Antigravity スクリプトを活用して engagement_metrics 取得
  - 既存 52 ピンの品質は変わらない

---

## 詳細スケジュール（予定）

### 日時: 2026-03-26 以降

#### Day 1（Phase 3.2）
1. google.generativeai パッケージを google.genai に差し替え
2. GeminiLLMClient の API 呼び出しを新形式に修正
3. テスト実行（Lecture 01）
4. main ブランチへマージ

#### Day 2（Phase 3.3）
1. Antigravity スクリプト（scripts/dev/phase2_2_antigravity_full.py）を現パイプラインに統合
2. Mk2_Core に engagement_metrics フィールド追加
3. InsightSpecRepository にメトリクス保存機能追加
4. テスト実行（全 5 講座）
5. main ブランチへマージ

---

## 技術仕様

### Phase 3.2: google.genai への移行
**変更対象**: converter/gemini_llm_client.py
- `import google.generativeai as genai` → `import google.genai as genai`
- API 呼び出しシグネチャの更新
- response 処理の更新（新 SDK の形式に対応）

### Phase 3.3: YouTube API 統合
**対象ファイル**:
- converter/youtube_engagement_service.py（新規）
- converter/insight_spec_repository.py（修正）
- expand_insight_spec_with_gemini.py（修正）

**追加機能**:
- likes, views, comments の取得
- engagement_rate 計算（likes + comments / views）
- Mk2_Core への保存

---

## 注記

- Phase 3.2 は **機能的変化なし** → 品質テストは不要（リファクタリング）
- Phase 3.3 は **新機能追加** → 既存 52 ピン品質への影響確認必要
- 両フェーズ完了後、Phase 4（テスト拡張・本番環境対応）へ進める
