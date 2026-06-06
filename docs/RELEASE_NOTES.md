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
