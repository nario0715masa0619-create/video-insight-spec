# PHASE 7-2：レポート自動生成エンジン
**バージョン**: 1.1（YouTube API 自動フィルタリング対応） | **作成日**: 2026-03-28 | **ステータス**: 計画中

## 概要
Phase 7-1 で構築した実績データ匿名化フローを基に、YouTube API を用いた自動講座フィルタリング、Markdown→HTML→PDF のレポート自動生成、および定期実行スケジューリングを実装。毎月 1 日に自動実行、人的操作は月 1 回のボタン押下のみ。

---

## 成果物（5月～6月完成予定）

### 1. YouTube API 自動フィルタリングスクリプト
**ファイル**: scripts/youtube_auto_filter.py
- YouTube Data API v3 で全講座を取得
- フィルタリング条件：
  - 再生数 ≥ 10,000
  - 成長率（月増加率） ≥ 10%
  - エンゲージメント率 ≥ 1.5%
- 結果を CSV (data/filtered_lectures.csv) に出力
- エラーハンドリング・API 制限対応
- **期限**: 5月12日

### 2. レポート自動生成スクリプト
**ファイル**: scripts/generate_report.py
- 入力: CSV (filtered_lectures.csv) + 匿名化済み実績データ
- Jinja2 テンプレートで Markdown 生成
- pandoc / markdown-it で HTML 変換
- wkhtmltopdf / Playwright で PDF 生成
- 出力: reports/html/, reports/text/, reports/pdf/
- **期限**: 5月26日

### 3. スケジューリング・実行エンジン
**ファイル**: scripts/scheduler_config.py
- APScheduler で毎月 1 日 09:00 に自動実行
- フロー: API 取得 → フィルタリング → レポート生成 → 配信
- ログ記録・アラート通知（Slack/Email）
- **期限**: 6月9日

### 4. テンプレートライブラリ
**ディレクトリ**: templates/
- templates/marketing_template.jinja2
- templates/webdev_template.jinja2
- templates/dataanalysis_template.jinja2
- カスタマイズガイド同梱
- **期限**: 5月19日

### 5. テスト・ドキュメント
- Unit テスト (tests/test_youtube_filter.py, test_generate_report.py)
- Integration テスト (tests/test_full_pipeline.py)
- ユーザーガイド (docs/PHASE7_2_USER_GUIDE.md)
- 管理者ガイド (docs/PHASE7_2_ADMIN_GUIDE.md)
- **期限**: 6月23日

---

## 技術スタック

| レイヤー | 技術 | 役割 |
|---|---|---|
| YouTube 連携 | YouTube Data API v3 + google-api-python-client | 講座自動取得・メタデータ抽出 |
| フィルタリング | Python (pandas) | 条件評価・ソート |
| データ準備 | Python (Pandas, NumPy) | 匿名化データ統合・正規化 |
| テンプレート | Jinja2 | Markdown テンプレート埋め込み |
| Markdown→HTML | pandoc / markdown-it | 出力フォーマット変換 |
| HTML→PDF | wkhtmltopdf / Playwright | PDF レンダリング |
| スケジューリング | APScheduler / cron | 定期実行（毎月 1 日） |
| 環境・CI/CD | Docker / GitHub Actions | 本番環境・自動テスト |
| ログ・監視 | Python logging + ELK | エラー追跡・パフォーマンス監視 |

---

## アーキテクチャ・処理フロー

\\\
[毎月 1 日 09:00] 
  ↓
[YouTube API] → 全講座メタデータ取得
  ↓
[youtube_auto_filter.py] → 再生数≥10k, 成長率≥10%, エンゲージ≥1.5% でフィルタリング
  ↓
[data/filtered_lectures.csv] → フィルタリング結果を出力
  ↓
[匿名化データ結合] → data/anonymized_customer_data.csv + filtered_lectures.csv
  ↓
[generate_report.py] → Jinja2 テンプレートで Markdown 生成
  ↓
[pandoc / markdown-it] → HTML 変換
  ↓
[wkhtmltopdf / Playwright] → PDF 変換
  ↓
[reports/ に保存]
  ↓
[APScheduler] → Slack/Email 通知
  ↓
[ログ記録・モニタリング]
\\\

---

## 実装スケジュール（5月～6月）

### ステップ 1：YouTube API 統合（5月1日～12日）
| 日程 | タスク | 担当 | KPI |
|---|---|---|---|
| 5/1-5/3 | YouTube Data API v3 キー取得・認証確認 | Lead Dev | API 接続確認 |
| 5/4-5/7 | youtube_auto_filter.py 実装・基本テスト | Lead Dev | フィルタリング動作 100% |
| 5/8-5/12 | エラーハンドリング・API レート制限対応 | Lead Dev | エラー処理 100%, レート制限対応 ✅ |

### ステップ 2：レポート生成パイプライン実装（5月13日～26日）
| 日程 | タスク | 担当 | KPI |
|---|---|---|---|
| 5/13-5/15 | Jinja2 テンプレート 3 種完成 | PO + Designer | テンプレート 100% |
| 5/16-5/19 | generate_report.py 実装（Markdown 生成） | Lead Dev | スクリプト動作 100% |
| 5/20-5/23 | pandoc/markdown-it 統合、HTML 変換テスト | QA + Lead Dev | HTML 出力確認 ✅ |
| 5/24-5/26 | wkhtmltopdf / Playwright 統合、PDF 変換テスト | QA + Lead Dev | PDF 出力確認 ✅ |

### ステップ 3：スケジューリング・本番化（5月27日～6月15日）
| 日程 | タスク | 担当 | KPI |
|---|---|---|---|
| 5/27-5/30 | APScheduler / cron 設定、定期実行テスト | Lead Dev + DevOps | スケジューリング動作 ✅ |
| 6/1-6/5 | 本番環境デプロイ（Docker / GitHub Actions） | DevOps + Lead Dev | 本番環境 ✅ |
| 6/6-6/9 | Slack/Email 通知・ロギング統合 | Lead Dev + Ops | 通知機能 ✅ |

### ステップ 4：テスト・ドキュメント（6月10日～23日）
| 日程 | タスク | 担当 | KPI |
|---|---|---|---|
| 6/10-6/15 | Unit / Integration テスト実施、バグ修正 | QA + Lead Dev | テスト合格率 100% |
| 6/16-6/20 | ユーザーガイド・管理者ガイド作成 | PO + Tech Writer | ドキュメント完成度 100% |
| 6/21-6/23 | 最終レビュー・本運用開始準備 | Lead Dev + PO | 本運用開始可否判定 |

### ステップ 5：本運用開始・監視（6月24日～30日）
| 日程 | タスク | 担当 | KPI |
|---|---|---|---|
| 6/24-6/30 | 本運用開始、1 週間モニタリング | Ops + Support | エラー率 < 1%, 応答時間 < 5 分 |

---

## リスク・対応

| # | リスク | 影響度 | 対応策 | オーナー |
|---|---|---|---|---|
| 1 | YouTube API レート制限超過 | 高 | キャッシング・バッチ処理・複数 API キー | Lead Dev |
| 2 | Markdown→PDF 崩れ | 高 | wkhtmltopdf + Playwright テンプレート検証 | QA |
| 3 | 大規模データ処理遅延 | 中 | 非同期処理・キュー実装 | Lead Dev |
| 4 | スケジューラ停止 | 中 | 監視アラート・自動再起動 | DevOps |
| 5 | セキュリティ脆弱性 | 高 | コード審査・依存パッケージ更新 | Security |

---

## 成功指標（KPI）

### 5月末
- ✅ YouTube API フィルタリング動作率 100%
- ✅ Markdown 生成成功率 ≥ 99%
- ✅ HTML/PDF 出力品質スコア ≥ 95%
- ✅ テンプレート 3 種完成度 100%

### 6月末
- ✅ レポート生成時間 < 5 分/件
- ✅ スケジューリング成功率 ≥ 99.5%
- ✅ エラー率 < 0.5%
- ✅ テスト合格率 100%
- ✅ ドキュメント完成度 100%
- ✅ 本運用準備完了

---

## 担当者・役割

| 役割 | 主要タスク | スキル要件 |
|---|---|---|
| **PO** | 要件定義、テンプレート承認、進捗管理 | ビジネス理解、プロセス設計 |
| **Lead Dev** | API・スクリプト・パイプライン実装、テスト | Python, YouTube API, Jinja2, pandoc |
| **QA** | テスト計画・実施、品質保証 | テスト設計、自動テスト |
| **Designer** | テンプレートレイアウト、PDF スタイル | HTML/CSS, PDF デザイン |
| **DevOps** | Docker, GitHub Actions, 本番デプロイ | Docker, CI/CD, Linux |
| **Security** | セキュリティレビュー、GDPR 対応確認 | セキュリティ監査、暗号化 |
| **Tech Writer** | ユーザー・管理者ガイド | ドキュメント作成スキル |

---

## 参考資料

- YouTube Data API v3: https://developers.google.com/youtube/v3
- google-api-python-client: https://github.com/googleapis/google-api-python-client
- Jinja2 Documentation: https://jinja.palletsprojects.com/
- Pandoc: https://pandoc.org/
- markdown-it: https://github.com/executablebooks/markdown-it-py
- wkhtmltopdf: https://wkhtmltopdf.org/
- Playwright: https://playwright.dev/python/
- APScheduler: https://apscheduler.readthedocs.io/
- Docker Documentation: https://docs.docker.com/
- GitHub Actions: https://docs.github.com/en/actions

---

**次のステップ**: 5月 1 日から実装着手。毎週金曜日に進捗ミーティング。
