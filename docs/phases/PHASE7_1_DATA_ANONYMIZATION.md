# PHASE 7-1：実績データ匿名化・統合
**バージョン**: 1.0（確定版） | **作成日**: 2026-03-27 | **ステータス**: 4月実装予定

## 概要
顧客の実績データを GDPR 準拠で匿名化し、Phase 6 で構築したサンプルレポート統合。

**4月ゴール**: 実績データ匿名化完了 → 手動レポート生成フロー確立 → セキュリティレビュー合格

---

## 成果物（4月末までに完成予定）

### 1. 匿名化ポリシードキュメント (anonymization_policy.md)
- 個人情報の定義（PII）
- 匿名化対象データ一覧
- 匿名化手法（ハッシュ化、トークン化、集約）
- GDPR / CCPA / 個人情報保護法との対応表
- **期限**: 4月7日

### 2. データスキーマ・マッピング (data_schema.json)

lecture テーブル:
- lecture_id: hash化
- lecture_name: トークン化
- category: そのまま保持
- views_raw: 集約
- engagement_rate: そのまま保持

viewer テーブル:
- viewer_id: hash化
- age_group: バケット化（10歳単位）
- role: 一般化
- signup_date: 削除

interaction テーブル:
- interaction_id: hash化
- viewer_id: hash化
- lecture_id: hash化
- completion_rate: そのまま保持
- timestamp: 日単位に丸める

**期限**: 4月7日

### 3. Python 匿名化スクリプト (scripts/anonymize_data.py)

主な処理:
- ID のハッシュ化（SHA-256、最初の12文字）
- 年代をバケット化（10歳単位）
- 役職を一般化（Executive, Sales, Marketing, Engineer）
- 不要なカラムを削除（email, phone, signup_date, company_name）
- CSV 出力

**期限**: 4月12日

### 4. データ品質チェック (scripts/validate_data.py)

検証項目:
- レコード保持率（目標: >= 95%）
- 欠損値率（目標: < 1%）
- 個人情報残存チェック（メールアドレス等）
- 統計量の比較（元データとの差分 < 5%）

**期限**: 4月15日

### 5. サンプルレポート統合
- reports/samples/text/sample_report_marketing_with_real_data.md
- reports/samples/text/sample_report_webdev_with_real_data.md
- reports/samples/text/sample_report_dataanalysis_with_real_data.md
- 対応 HTML/PDF 版も生成

**期限**: 4月20日

---

## 実装手順（4月スケジュール）

### ステップ 1：データ準備（4月1日～7日）
1. 顧客から実績データを CSV で取得
2. ローカル環境でテスト
3. データ品質の初期チェック

### ステップ 2：スキーマ定義・匿名化（4月8日～12日）
1. data_schema.json を確定
2. anonymize_data.py を実装
3. 匿名化実行、出力ファイル確認

### ステップ 3：品質チェック・監査（4月13日～15日）
1. validate_data.py 実行
2. レコード保持率 >= 95% 確認
3. セキュリティチーム監査

### ステップ 4：手動レポート生成（4月16日～20日）
1. 匿名化データを Markdown テンプレートに埋め込み
2. HTML / PDF 生成
3. レイアウト・数値確認

### ステップ 5：本番環境へ移行（4月21日～30日）
1. 最終セキュリティレビュー
2. Git へコミット
3. ドキュメント整備

---

## GDPR / 個人情報保護法対応

| 要件 | 対応方法 | 期限 |
|---|---|---|
| データ最小化 | 不要カラム削除 | 4月7日 |
| 目的限定 | 契約書に明記 | 4月15日 |
| アクセス制御 | 管理者のみアクセス | 4月30日 |
| データ移譲通知 | レポート内に表示 | 4月20日 |

---

## リスク・対応

| リスク | 影響 | 対応 | オーナー |
|---|---|---|---|
| データ提供拒否 | 実績移行遅延 | 仮想データ継続 | PO |
| 有用性低下 | インサイト減少 | 集約単位調整 | データチーム |
| 生データ混入 | セキュリティ侵害 | .gitignore 設定 | エンジニア |
| 品質スコア < 95% | マイルストーン未達 | スキーマ再設計 | QA |

---

## 成功指標（4月末）

必須:
- レコード保持率 >= 95%
- 個人情報検出ゼロ
- データ品質スコア >= 95%
- 手動レポート生成完成（HTML/PDF）

5月への引継ぎ:
- 自動生成スクリプト開発開始
- セキュリティ実装開始

---

## 担当者・スケジュール

| 役割 | 主要タスク | 期限 |
|---|---|---|
| PO | データ取得、最終承認 | 4月7日 / 4月30日 |
| Data Eng | スキーマ定義、データ抽出 | 4月7日 / 4月12日 |
| Lead Dev | 匿名化スクリプト、手動生成 | 4月12日 / 4月20日 |
| Security | ポリシー作成、監査 | 4月7日 / 4月15日 |
| QA | 品質チェック、テスト | 4月15日 / 4月20日 |

---

## 参考資料

- GDPR Article 29: https://ec.europa.eu/newsroom/article29/
- Pandas Documentation: https://pandas.pydata.org/docs/
- Python hashlib: https://docs.python.org/3/library/hashlib.html

---

**次のステップ**: 5月に Deliverable 2（レポート自動生成エンジン）へ移行
