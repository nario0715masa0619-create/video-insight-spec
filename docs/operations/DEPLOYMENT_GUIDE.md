# デプロイメントガイド

## 本番環境への Phase 4 デプロイ

完了日: 2026-03-26
デプロイ対象: main ブランチ（commit f3f8e17）

## デプロイ内容

| ファイル | 状態 | 説明 |
|---------|------|------|
| converter/engagement_scorer.py | 新規 | engagement スコア計算 |
| converter/views_generator_service.py | 新規 | views 生成サービス |
| converter/youtube_metadata_service.py | 修正 | YouTube Analytics API 追加 |
| generate_views.py | 新規 | CLI メインスクリプト |
| quality_check_phase4.py | 新規 | 品質検査 |

## 事前チェック

- YouTube API キー設定確認
- insight_spec JSON の video_id 修正完了
- 全 5 講座の quality check 合格（40/40）

## デプロイ手順

### 1. 本番サーバーへのクローン

git clone https://github.com/nario0715masa0619-create/video-insight-spec.git
cd video-insight-spec
git checkout main

### 2. 環境変数設定

echo "YOUTUBE_API_KEY=YOUR_KEY" > .env

### 3. 初回実行（全講座）

python generate_views.py --lecture-ids "01,02,03,04,05" --archive-dir "/path/to/archive"

### 4. 品質検査

python quality_check_phase4.py

## 本番メトリクス

初回実行結果（2026-03-26）:
- Lecture 01-05: 全て成功（5/5）
- Quality check: 40/40 合格

## ロールバック手順

何か問題が発生した場合:

git checkout a0b0845

または feature ブランチを削除してやり直す:

git branch -D feature/phase-4-views-implementation

---
Last Updated: 2026-03-26

## Phase 4.1: Weekly Report Generation

### 概要
週次レポート生成機能。複数週のスナップショットから成長率を計算し、JSON形式で出力。

### 必須ファイル
- \weekly_report_generator.py\: レポート生成エンジン
- \converter/report_utils.py\: Delta計算ユーティリティ
- \converter/report_formatter.py\: JSON/HTML/Text フォーマッタ
- \converter/snapshot_manager.py\: スナップショット管理
- \quality_check_phase4_1.py\: 品質検査スクリプト

### 実行例
\\\ash
python weekly_report_generator.py \\
  --lecture-ids "01,02,03,04,05" \\
  --archive-dir "D:\\AI_Data\\video-insight-spec\\archive" \\
  --output-dir "reports/weekly"
\\\

### 出力フォーマット
- **初回（Baseline）**: \BASELINE_SET\ ステータス、スナップショット初期化
- **2回目以降（Delta）**: 前週との差分、成長率を計算

### メトリクス
- view_count, like_count, comment_count, engagement_rate
- タイムスタンプ: ISO8601+09:00 (JST)

### 品質検査結果
- ✅ 25/25 合格
- ✅ Delta計算: 0除算なし
- ✅ baseline/current の値の取り違いなし

