## v1.5.0 - Diagnosis & Improvement Separation (2026-06-08)

### What's New
- Separated "Quality Diagnosis" tab from "Improvement Suggestion" tab
- Diagnosis tab now focuses on current state analysis only
- Improvement tab now focuses on next actions and priorities
- Eliminated redundancy between tabs; content is no longer repeated

### Changed
- `explain_channel_diagnosis()`: New function for state diagnosis
- `explain_channel_improvements()`: New function for action planning
- Prompts now have explicit "DO NOT" instructions per role

### Impact
- Users can now read tab 1 and tab 3 without duplicate information
- Clear distinction between "where we are" and "where we go"
- More actionable improvement suggestions

### Testing
- pytest: 8/8 PASS
- Dashboard verification: All tabs working correctly

## v1.4.0 - Language‑First Complete: Diagnostic Evidence Integration (2026-06-07)

### What's New
- **Diagnostic Evidence Framework**: 新たに `diagnostic_evidence.py` を実装し、`insight_spec_{id}.json` から言語ベースの中間材料を抽出（`theme_core`, `learning_roles`, `funnel_profile`, `difficulty_profile`, `audience_clarity`, `bridge_gaps`, `message_consistency`, `hidden_strengths`, `hidden_gaps`, `evidence_metrics`）。
- **Dashboard Tab Integration**: 全6タブ（個別動画4タブ + チャネル全体2タブ）で中間材料ベースのプロンプト呼び出しへ統一。数値説明を完全排除し、「結論 → 意味 → 課題 → 次アクション」の構造を徹底。
- **Console Debug Tool**: `scripts/debug_diagnostic_evidence.py` を追加、`--no-llm` オプションで中間材料のみ検証可能。

### Changed
- `streamlit_app/narrative_engine.py`: `explain_channel_overview` 署名変更、`explain_single_video` 追加、中間材料を受け取るプロンプト実装。
- `streamlit_app/app.py`: 全タブを新しい抽出関数へ切り替え（`extract_pattern_evidence`, `extract_weakness_evidence`, `extract_competitive_evidence`）。
- `streamlit_app/diagnostic_evidence.py`: 追加関数3件（pattern/weakness/competitive）、言語化完全化。

### Technical Impact
- Numeric explanations eliminated completely across all tabs.
- Diagnostic output is now pure textual state‑analysis (no percentages, scores, or raw counts in conclusions).
- Intermediate material is inspectable via debug script, enabling maintenance and future extensions.
- Prompt generation is fully decoupled from raw scores; LLM receives only structural/linguistic evidence.

### Test Coverage
- pytest: 101/101 cases PASS (no failures).
- All dashboard tabs verified; output validated for language consistency and state diagnosis.

### Next Phase (Backlog)
- E2E integration tests (UI → AI → output full flow).
- UI/UX refinement (card components, visual hierarchy for executives).
- Config expansion (threshold fine‑tuning, custom role definitions).

### Breaking Changes
- None. Backward compatible with v1.3.2.

### Known Limitations
- Debug script `--show-prompt` may expose full LLM context (development mode only).
- Config system in `diagnostic_config.yaml` is still basic; further modularization recommended for 50+ themes.

---

## v1.3.2 - AI要約プロンプトの自然な日本語化 (2026-06-07)

### Changed
- **AI要約プロンプトの全面改修**: 横文字・英語由来用語を削除し、会議で直接使える自然な日本語へ統一
  - 修正対象：個別動画分析 4 タブ + チャンネル全体分析
  - 削減項目：`ファネルカバレッジ` → `カバーしている学習段階`、`エンゲージメント効率スコア` → `視聴者の反応スコア` 等
  - 削減成果：英字パラメーター名の AI 出力からの完全排除
- **AI 出力の構成を統一**: 「結論 → 意味 → 課題 → 次アクション」の流れを明確化
- **経営層・営業向けの文体へ**: 取締役会資料や営業提案にそのままコピー＆ペースト可能な品質に

### Impact
- **可読性の大幅向上**: 会議の場で AI 出力を読み上げても違和感なし、専門用語も不要
- **意思決定の加速**: 横文字の説明が不要になり、経営判断が迅速化
- **営業資料の簡素化**: 別途翻訳・調整の手間が削減
- **実務利用の促進**: チーム全体が AI 出力を活用しやすくなる

### Technical Notes
- プロンプト修正により、AI の出力品質が「より鋭く、より自然に」進化
- 診断の鋭さ・内容の深さは完全に保持

### Version History
- v1.3.1: 言語化ファースト完全実装 + Config 化
- v1.3.2: AI要約プロンプトの自然な日本語化（本リリース）

## v1.3.1 - メンテナンス性向上: Config 化とテスト・ドキュメント整備 (2026-06-07)

### Added
- `streamlit_app/diagnostic_config.yaml`: 診断要約の設定ファイル
  - 診断閾値の一元管理（beginner_suitability, theme_diversity など）
  - ラベル翻訳テーブル（theme, funnel, difficulty を日本語化）
  - 将来のラベル追加に Python 修正不要な設計
- 拡充テスト（3 → 8 テストケースに拡大）
  - Config 読込テスト
  - 閾値別の言語化テスト
  - ラベル翻訳テスト
  - フォールバック動作テスト
  - 後戻り防止テスト（数字排除確認）
- `docs/DIAGNOSTIC_ARCHITECTURE.md`: 診断要約アーキテクチャ設計書
  - 「言語化ファースト」の基本原則
  - Config ベースの拡張手法
  - 新ラベル追加の手順
- `docs/TEST_STRATEGY.md`: テスト戦略書
  - ユニットテストの目的（後戻り防止）
  - 重点テスト項目
  - 将来 CI/CD への展開予定

### Changed
- `streamlit_app/diagnostic_summary.py`: Config 参照化
  - `load_diagnostic_config()` で YAML を動的に読込
  - スコア閾値を Config から取得
  - ラベル翻訳を Config から取得
  - 未定義ラベル時のフォールバック処理を追加

### Impact
- **メンテナンス性向上**: 新しいビジネスラベルや閾値変更が YAML ファイル修正のみで対応可能
- **バグリスク低減**: Python コード修正が不要 → テスト範囲が固定
- **将来の拡張性確保**: Config ベース設計で、ラベル体系の拡張に耐える
- **チーム引継ぎ簡素化**: ドキュメントで設計思想と拡張手法を明記

### Technical Notes
- Config 読込時にエラーハンドリング済み（YAML パース失敗時は例外で通知）
- 未定義ラベルはフォールバック（原文を維持）して、サイレント失敗を防止
- テストは pytest 設定に組み込まれ、CI/CD 対応可能

### Next Phase
- [ ] 統合テスト（E2E）の実装
- [ ] GitHub Actions による自動テスト・デプロイ
- [ ] カバレッジ測定・最適化

## v1.3.0 - 言語化ファースト完全実装: 全主要タブの診断ベース統一化 (2026-06-07)

### Added
- 3 つの高度分析タブ用の診断要約関数を `diagnostic_summary.py` に追加
  - `extract_competitive_advantage_summary()`: 競争優位性スコアを市場ポジショニング診断に変換
  - `extract_golden_pattern_summary()`: 高反応パターンを構造的勝因に言語化
  - `extract_hidden_weakness_diagnosis()`: 品質とエンゲージメントのギャップを課題診断に翻訳
- `tests/test_diagnostic_summary.py`: 上記 3 関数の堅牢性テスト（3/3 PASS）

### Changed
- **競争優位性分析** (`app.py` 533行目): スコア JSON から「構造的特徴」へプロンプト改修
- **黄金の組み合わせ** (`app.py` 423行目): 数値パターンから「構造的勝因」へプロンプト改修
- **隠れた弱点分析** (`app.py` 453行目): スコアギャップから「課題状態診断」へプロンプト改修

### Impact
- **ダッシュボード全体が「言語化ファースト」に統一**: 数値説明は完全排除、状態診断がすべてのタブに貫徹
- **AI 出力の統一性**: 「結論 → 意味 → 根拠 → 次アクション」の流れが全タブで一貫
- **VIS の本来価値の完全実現**: 営業・経営層が会議でそのまま使えるビジネスコンサルティング型出力
- **プロダクト体験の統一**: UI 全体の方針が「言語化ファースト」で揃った

### Completion
- ✅ 個別動画分析 4 タブ（基本・黄金・弱点・競争）が診断ベース
- ✅ チャンネル全体分析 2 タブ（品質・改善）が診断ベース
- ✅ すべての AI 要約が「数値説明」から「状態診断」へ転換
- ✅ テストカバレッジ拡充（6 タブの診断関数が検証対象）

### Next Phase
- [ ] `diagnostic_summary.py` の Config 化（拡張性向上）
- [ ] 統合テスト（E2E）追加
- [ ] CI/CD パイプライン構築

## v1.2.0 - 言語化ファースト: AI 要約の構造診断ベース転換 (2026-06-06)

### Added
- `streamlit_app/diagnostic_summary.py`: 構造化JSON から状態診断用サマリーを抽出するヘルパー関数
  - `extract_diagnostic_summary()`: 個別動画の テーマ・難易度・ファネル分布 を構造化
  - `extract_channel_diagnostic_summary()`: チャンネル全体の傾向を集計し、強み・弱み・次アクションを診断

### Changed
- **個別動画分析** (`app.py`): AI 要約プロンプトを「数値説明」から「構造診断ベース」へ転換
  - 従来: スコアや再生数を説明する形式
  - 新規: `insight_spec` の テーマ・難易度・ファネル構造 を活用し、「何に強く、どこで弱いか」を診断

- **チャンネル全体分析** (`narrative_engine.py`): AI 要約プロンプトを「スコア説明」から「ビジネス診断」へ転換
  - 従来: 平均Quality Score や総再生数を説明
  - 新規: チャンネルの「顧客獲得における役割」「戦略的な弱点」「次に補うべきコンテンツ」を診断

### Impact
- **UI/UX の価値向上**: ダッシュボードが「数値の実況中継」から「ビジネスインサイト」へ格上げ
- **言語化ファースト実現**: 数字は根拠として最後に添える設計に統一
- **会議・報告での利用**: 要約文をそのまま営業会議や経営報告に使える品質へ

### Technical Notes
- `diagnostic_summary.py` は現在、`difficulty` / `business_theme` / `funnel_stage` を扱う静的設計
  - 将来のラベル体系拡張時には Config 化を検討（Phase 3）
- 他タブ（黄金の組み合わせ、隠れた弱点等）のプロンプト改修は次フェーズへ

### Next Phase
- [ ] 他タブ（高度分析）の「数値説明」→「診断ベース」への転換
- [ ] `test_diagnostic_summary.py` による堅牢性向上
- [ ] `diagnostic_summary.py` の Config 化と拡張性向上

## [1.1.0] - 2026-06-05

### Added
- `env_loader.py` による統一的な環境変数ロード処理の実装
- `master_batch_refiner.py` に `--skip-whisper` 軽量実行モードを追加
- 開発者向けドキュメントの新規作成：
  - `docs/ENVIRONMENT_SETUP.md`
  - `docs/BATCH_EXECUTION.md`
  - `docs/ARCHITECTURE.md`

### Changed
- `data_loader.py`: `executive_report.json` への物理ファイル依存を完全除去し、`insight_spec` からの動的集計へ完全移行
- 各バッチスクリプト (`enrich_...`, `expand_...`, `master_batch...`): 必須引数を環境変数からデフォルトロードするように改修し、エラーメッセージを改善

### Fixed
- `insight_spec` および古い `executive_report` に由来する不完全な JSON（空辞書、型不一致、欠損キーなど）に対する fallback ロジックを強化

### Removed
- `config.py` から不要となった `EXEC_REPORT_PATH` の定義を削除

### Important Notes
- **`executive_report.json` は廃止対象です。** 今後の新規実装で参照することは禁止されています。
- 本プロジェクトにおける正本（Source of Truth）は **`insight_spec_{id}.json`** となります。
