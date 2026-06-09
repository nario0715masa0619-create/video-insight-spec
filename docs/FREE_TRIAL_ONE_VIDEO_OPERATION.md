# 無料1本解析 運用ガイド

## 概要
VIS の無料1本解析は、顧客の動画1本をシンプルに診断し、商談用の成果物を返すサービスです。
最小限の手動作業で確実に回せることを重視しています。

## 運用フロー

### 1. 動画受領
営業が顧客から動画ファイル（MP4 推奨）を受領します。

### 2. 動画配置
受領した動画を以下に配置：
`free_trial_cases/incoming/{video_file_name}`

例: `free_trial_cases/incoming/sample_20260609_company_name.mp4`

### 3. 案件登録
`free_trial_cases/cases.yaml` に案件情報を追加：

```yaml
cases:
  - case_id: trial_companyx_20260609
    client_name: Company X
    video_file: sample_20260609_company_name.mp4
    status: pending
    date_created: 2026-06-09
    focus: 初心者向けコンテンツの品質診断
    notes: 営業A氏より依頼
    assigned_to: 営業部 A氏
    expected_delivery: 2026-06-10
```

### 4. 解析実行
以下いずれかの方法で実行：

方法1: Python スクリプト直接実行

```bash
python scripts/run_free_trial_one_video.py --case-id trial_companyx_20260609
```

方法2: バッチファイル（Windows）

```bash
run_free_trial.bat trial_companyx_20260609
```

### 5. 成果物確認
解析後、以下にファイルが出力されます：

```
free_trial_cases/deliverables/trial_companyx_20260609/
├── report.md           # 顧客返却用レポート（マークダウン）
├── report.html         # 同（HTML変換版、任意）
└── metadata.json       # 内部用メタデータ
```

### 6. 顧客返却
`report.md` をメールで送信、または Web で共有します。 HTML 版が必要な場合は Pandoc などで変換：

```bash
pandoc report.md -o report.html
```

## ファイル配置リファレンス
| 役割 | パス |
| --- | --- |
| 受領動画の配置場所 | `free_trial_cases/incoming/` |
| 動画解析中の一時置き | `free_trial_cases/processing/` |
| 解析済み動画アーカイブ | `free_trial_cases/completed/` |
| 顧客返却物の出力 | `free_trial_cases/deliverables/{case_id}/` |
| 実行ログ | `free_trial_cases/logs/{case_id}.log` |
| 案件メタデータ | `free_trial_cases/cases.yaml` |

## 命名規則
### 案件ID (case_id)
`trial_{会社略号}_{YYYYMMDD}`
例:
- `trial_companyx_20260609`
- `trial_vendora_20260608`

### 動画ファイル
`{任意の説明}_{YYYYMMDD}_{会社名}.mp4`
例:
- `sample_20260609_company_x.mp4`
- `marketing_20260610_vendor_a.mp4`

## エラー対応
### エラーが出た場合
1. ログを確認：`free_trial_cases/logs/{case_id}.log`
2. よくあるエラー：
   - 「動画ファイルが見つかりません」→ incoming に正しく配置したか確認
   - 「case_id が見つかりません」→ cases.yaml に登録したか確認
   - その他 → logs ファイルの詳細を確認

## トラブルシューティング
**Q: 動画ファイルが見つからないと言われた**
A: `free_trial_cases/incoming/` に配置したか確認
相対パスではなく、フォルダ構成が正確か確認

**Q: 返却物が出ない**
A: ログファイルでエラーを確認
動画ファイルが壊れていないか確認（再受領検討）

**Q: 同じ case_id で再実行したい**
A: `cases.yaml` の status を pending に変更して再実行
または新しい case_id を付けて新規登録

## 無料枠の範囲
- ✅ 1本の動画
- ✅ 品質診断 + 改善提案
- ✅ マークダウンレポート
- ✅ 実行ログ
- ❌ 複数動画の同時処理
- ❌ YouTube からの自動ダウンロード
- ❌ 自動化の大規模展開
- ❌ カスタム分析軸追加

## よくある質問
**Q: 本番環境との違いは？**
A: 本番は複数動画・チャネルを管理します。無料解析は1本のみシンプル処理です。

**Q: ダッシュボードで見られる？**
A: 今回は無料解析専用の流れです。本番ダッシュボードとは分離しています。

**Q: 商談中に動画を追加ダウンロードしたい**
A: 今回は手動配置です。自動ダウンロードは実装していません。
