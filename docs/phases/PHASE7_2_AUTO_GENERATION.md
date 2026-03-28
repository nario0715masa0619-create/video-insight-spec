# PHASE 7-2：レポート自動生成エンジン
**バージョン**: 1.0（計画版） | **作成日**: 2026-03-28 | **ステータス**: 計画中

## 概要
Phase 7-1 で匿名化した実績データを入力として、Markdown / HTML / PDF レポートを自動生成・配信するエンジンを構築。毎月・毎週・毎日の定期実行をサポート。

**5月～6月実装予定**（4月は Phase 7-1 匿名化・手動フロー確立に集中）

---

## 成果物（5月～6月）

### 1. PHASE7_2_AUTO_GENERATION.md（このファイル）
- レポート自動生成エンジン全体設計
- 技術スタック、アーキテクチャ
- 実装スケジュール、KPI

### 2. Python 自動化スクリプト (scripts/generate_report.py)
機能:
- CSV / JSON データ入力 → Markdown テンプレート埋め込み
- Markdown → HTML 変換（markdown-it または pandoc）
- HTML → PDF 出力（wkhtmltopdf または Playwright）
- エラーハンドリング・ロギング
- メール送信（オプション）

### 3. スケジューリング設定 (scripts/scheduler_config.py)
- APScheduler を使用した定期実行（日次・週次・月次）
- cron 式対応
- エラー時の再試行・通知機能

### 4. テンプレートライブラリ (templates/)
- report_template_marketing.md
- report_template_webdev.md
- report_template_dataanalysis.md
- report_template_custom.md

### 5. 統合テスト・ドキュメント
- tests/test_generate_report.py
- docs/AUTO_GENERATION_USER_GUIDE.md
- docs/AUTO_GENERATION_ADMIN_GUIDE.md

---

## 技術スタック

| レイヤー | 技術 | 用途 |
|---|---|---|
| データ入力 | CSV / JSON | 匿名化データ |
| テンプレート | Jinja2 | Markdown 埋め込み |
| Markdown→HTML | markdown-it/pandoc | HTML 生成 |
| HTML→PDF | wkhtmltopdf/Playwright | PDF 生成 |
| スケジューリング | APScheduler | 定期実行 |
| ロギング | Python logging | 監査ログ |
| エラー通知 | メール/Slack | アラート |
| 実行環境 | Docker/GitHub Actions/AWS Lambda | 本番運用 |

---

## アーキテクチャ概要

入力層: CSV / JSON / YAML
 ↓
処理層（Python）
├─ データ読み込み & 検証（pandas）
├─ テンプレート変数埋め込み（Jinja2）
├─ Markdown 生成
├─ HTML 変換（pandoc / markdown-it）
└─ PDF 生成（wkhtmltopdf / Playwright）
 ↓
出力層
├─ reports/text/report_YYYYMMDD.md
├─ reports/html/report_YYYYMMDD.html
├─ reports/pdf/report_YYYYMMDD.pdf
└─ メール / Slack 送信
 ↓
スケジューリング層（APScheduler）
├─ 日次（毎朝 6:00 JST）
├─ 週次（毎月曜 8:00 JST）
└─ 月次（毎月 1 日 9:00 JST）

---

## 実装ステップ（5月～6月）

### ステップ 1：スクリプト実装（5月1日～15日）
1. generate_report.py 基本フレーム（入力検証、エラーハンドリング）
2. Markdown → HTML 変換モジュール（レスポンシブ CSS）
3. HTML → PDF 変換モジュール（日本語フォント対応）

### ステップ 2：テンプレート整備（5月8日～20日）
1. 3 種類のテンプレート完成
2. Jinja2 変数ドキュメント作成
3. サンプルレンダリング & 確認

### ステップ 3：スケジューリング実装（5月15日～25日）
1. APScheduler 設定（日次・週次・月次）
2. ロギング実装（audit log）
3. エラー時の再試行・通知

### ステップ 4：統合テスト（5月26日～31日）
1. 単体テスト（pytest）
2. 統合テスト（CSV → PDF 全フロー）
3. パフォーマンステスト（生成時間 < 5分確認）

### ステップ 5：本番デプロイ準備（6月1日～15日）
1. Docker イメージ作成
2. GitHub Actions ワークフロー設定
3. AWS Lambda / Scheduler 設定
4. 監視・アラート設定
5. ドキュメント完成

### ステップ 6：本番運用開始（6月16日～30日）
1. 本番環境デプロイ
2. 日次 → 週次 → 月次レポート段階的運用開始
3. 監視・ログ確認（1～2週間）

---

## スケジュール（5月～6月詳細）

| 週 | タスク | 担当 | KPI |
|---|---|---|---|
| 5/1-5/5 | スクリプト基本フレーム | Lead Dev | コード 50% 完成 |
| 5/6-5/12 | Markdown→HTML/PDF 変換実装 | Lead Dev | 変換モジュール 100% |
| 5/13-5/19 | テンプレート整備、Jinja2 変数定義 | PO + Dev | 3種テンプレート完成 |
| 5/20-5/26 | APScheduler 設定、ロギング実装 | Dev + Ops | スケジューリング 100% |
| 5/27-6/2 | 単体テスト、統合テスト | QA | テスト合格率 100% |
| 6/3-6/9 | Docker 化、CI/CD 設定 | DevOps | デプロイ自動化 100% |
| 6/10-6/16 | 本番環境テスト、ドキュメント完成 | Team | ドキュメント 100% |
| 6/17-6/30 | 本番デプロイ、監視・最適化 | Ops + Dev | 稼働率 99.9% |

---

## リスク・対応

| リスク | 影響 | 対応 | オーナー |
|---|---|---|---|
| PDF 生成遅延 | 5分以上かかる | 非同期処理化、キューイング | Lead Dev |
| 日本語フォント未対応 | 文字化け | フォント埋め込み、テスト | Dev |
| テンプレート拡張困難 | カスタマイズ困難 | Jinja2 ドキュメント充実 | PO |
| スケジューリング漏れ | 実行停止 | 監視・アラート、キュー | Ops |
| DB 接続エラー | 生成失敗 | 再試行ロジック | Dev |

---

## 成功指標（KPI）

### 5月末
- ✅ スクリプト実装率 >= 80%
- ✅ テンプレート 3種完成
- ✅ 単体テスト合格率 100%

### 6月末
- ✅ レポート生成時間 < 5分 / 件
- ✅ 生成成功率 >= 99.5%
- ✅ 本番デプロイ完了・稼働率 99.9%
- ✅ ドキュメント完成・利用者評価 >= 4.5/5.0

---

## 担当者・所属

| 役割 | 人数 | 主要タスク |
|---|---|---|
| Lead Dev | 1 | スクリプト実装、PDF 生成、最適化 |
| PO | 1 | テンプレート設計、スケジュール定義 |
| QA / テスト | 1 | 単体テスト、統合テスト |
| DevOps | 1 | Docker 化、CI/CD |
| Ops | 1 | スケジューリング運用、監視 |

---

## 参考資料

- Jinja2: https://jinja.palletsprojects.com/
- Pandoc: https://pandoc.org/
- wkhtmltopdf: https://wkhtmltopdf.org/
- APScheduler: https://apscheduler.readthedocs.io/
- Python Logging: https://docs.python.org/3/library/logging.html

---

**次のステップ**: 5月1日に実装開始（スクリプト基本フレーム）
