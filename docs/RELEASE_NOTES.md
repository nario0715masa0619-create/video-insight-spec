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
