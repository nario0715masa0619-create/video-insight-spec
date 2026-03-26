# デプロイメントガイド

## 本番環境への Phase 4 デプロイ

**完了日**: 2026-03-26  
**デプロイ対象**: main ブランチ（commit f3f8e17）

### デプロイ内容

| ファイル | 状態 | 説明 |
|---------|------|------|
| converter/engagement_scorer.py | 新規 | engagement スコア計算 |
| converter/views_generator_service.py | 新規 | views 生成サービス |
| converter/youtube_metadata_service.py | 修正 | YouTube Analytics API 追加 |
| generate_views.py | 新規 | CLI メインスクリプト |
| quality_check_phase4.py | 新規 | 品質検査 |

### 事前チェック

- ✅ YouTube API キー設定確認
- ✅ insight_spec JSON の video_id 修正完了
- ✅ 全 5 講座の quality check 合格（40/40）

### デプロイ手順

#### 1. 本番サーバーへのクローン
\\\ash
git clone https://github.com/nario0715masa0619-create/video-insight-spec.git
cd video-insight-spec
git checkout main
\\\

#### 2. 環境変数設定
\\\ash
# .env ファイルを作成
echo "YOUTUBE_API_KEY=YOUR_KEY" > .env
\\\

#### 3. 初回実行（全講座）
\\\ash
python generate_views.py \
  --lecture-ids "01,02,03,04,05" \
  --archive-dir "/path/to/archive"
\\\

#### 4. 品質検査
\\\ash
python quality_check_phase4.py
\\\

### 本番メトリクス

**初回実行結果（2026-03-26）**:
- Lecture 01-05: 全て成功（5/5）
- Quality check: 40/40 合格

### ロールバック手順

何か問題が発生した場合:
\\\ash
# 前のコミットに戻す
git checkout a0b0845

# または feature ブランチを削除してやり直す
git branch -D feature/phase-4-views-implementation
\\\

### サポート連絡先

技術的な問題が発生した場合は、以下を確認してください：
- YouTube API キーの有効期限
- API クォータ（1 日 10,000 ユニット）
- insight_spec JSON のパス設定

---

**Last Updated**: 2026-03-26
