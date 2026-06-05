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
