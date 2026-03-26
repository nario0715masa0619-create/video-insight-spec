# video-insight-spec

YouTube 動画から知識体系を自動抽出し、ビジネス価値を分析する AI パイプライン

## プロジェクト概要

| フェーズ | 状態 | 説明 |
|---------|------|------|
| **Phase 1** | ✅ 完了 | 動画ダウンロード、メタデータ抽出 |
| **Phase 2** | ✅ 完了 | YouTube API、OCR、Whisper 統合 |
| **Phase 3** | ✅ 完了 | Gemini AI ラベリング、52 個の知識要素抽出 |
| **Phase 3.3** | ✅ 完了 | YouTube API で video_meta 埋め込み |
| **Phase 4** | ✅ 完了 | Views 生成、YouTube Analytics 統合 |
| **Phase 4.1** | ⏳ 予定 | 週次レポート生成 |

## Phase 4 の成果

### 実装内容
- **engagement_scorer.py**: purity_score + type_weight + stage_weight で engagement_score を計算
- **views_generator_service.py**: competitive / education / self_improvement の 3 つのビューを生成
- **youtube_metadata_service.py**: YouTube Analytics API を統合し view/like/comment 統計を取得
- **generate_views.py**: 5 講座の views を自動生成し insight_spec JSON に保存
- **quality_check_phase4.py**: 全講座の品質検査で 40/40 合格を確認

### メトリクス（実績）
\\\
Lecture 01: views 115,834 | likes 1,804 | comments 48 | engagement 2.0%
Lecture 02: views 47,736  | likes 776   | comments 24 | engagement 1.6%
Lecture 03: views 33,800  | likes 619   | comments 21 | engagement 1.9%
Lecture 04: views 26,024  | likes 432   | comments 23 | engagement 1.7%
Lecture 05: views 21,064  | likes 310   | comments 26 | engagement 1.6%
\\\

### Views スキーマ

#### competitive view
- metrics: view_count, like_count, comment_count, engagement_rate, likes_per_1000_views, comments_per_1000_views
- top_pins_by_engagement: 上位 3 個の pin（engagement_score 順）
- snapshot_timestamp: データ取得時刻

#### education view
- difficulty_distribution: beginner / intermediate / advanced の分布
- top_pins_by_difficulty: 難易度ごとの top 3 pins

#### self_improvement view
- business_theme_distribution: ビジネステーマの分布
- funnel_stage_distribution: ファネルステージの分布
- funnel_flow: 各ステージの pin_count / top_themes / average_difficulty

## 実行方法

### Views 生成
\\\ash
python generate_views.py \
  --lecture-ids "01,02,03,04,05" \
  --archive-dir "D:\AI_Data\video-insight-spec\archive" \
  --api-key "YOUR_YOUTUBE_API_KEY"
\\\

### 品質検査
\\\ash
python quality_check_phase4.py
\\\

## ドキュメント

- [JSON スキーマ](docs/specs/JSON_SPEC.md)
- [Views デザイン](docs/architecture/VIEWS_DESIGN.md)
- [Phase 4 実装レポート](docs/phases/PHASE4_IMPLEMENTATION.md)
- [デプロイメントガイド](docs/operations/DEPLOYMENT_GUIDE.md)
- [トラブルシューティング](docs/operations/TROUBLESHOOTING.md)

## 今後の計画

### Phase 4.1: 週次レポート生成
- baseline snapshot との比較
- 成長率（delta）を計算
- HTML/PDF/JSON で配信

### Phase 4.2: 競合分析ダッシュボード
- 複数講座間の metrics 比較
- ベストプラクティス抽出

---

**Last Updated**: 2026-03-26
