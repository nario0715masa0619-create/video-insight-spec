# video-insight-spec

YouTube 動画から知識体系を自動抽出し、ビジネス価値を分析する AI パイプライン

## プロジェクト概要

| フェーズ | 状態 | 説明 |
|---------|------|------|
| Phase 1 | ✅ 完了 | 動画ダウンロード、メタデータ抽出 |
| Phase 2 | ✅ 完了 | YouTube API、OCR、Whisper 統合 |
| Phase 3 | ✅ 完了 | Gemini AI ラベリング、52 個の知識要素抽出 |
| Phase 3.3 | ✅ 完了 | YouTube API で video_meta 埋め込み |
| Phase 4 | ✅ 完了 | Views 生成、YouTube Analytics 統合 |
| Phase 4.1 | ✅ JSON weekly report generation | 2026-03-26 |
| Phase 4.1 | ⏳ 予定 | 週次レポート生成 |

## Phase 4 の成果

### 実装内容
- engagement_scorer.py: engagement_score を計算
- views_generator_service.py: competitive/education/self_improvement の 3 つのビュー生成
- youtube_metadata_service.py: YouTube Analytics API 統合
- generate_views.py: 5 講座の views を自動生成
- quality_check_phase4.py: 品質検査（40/40 合格）

### メトリクス実績

Lecture 01: views 115,834 | likes 1,804 | comments 48 | engagement 2.0%
Lecture 02: views 47,736  | likes 776   | comments 24 | engagement 1.6%
Lecture 03: views 33,800  | likes 619   | comments 21 | engagement 1.9%
Lecture 04: views 26,024  | likes 432   | comments 23 | engagement 1.7%
Lecture 05: views 21,064  | likes 310   | comments 26 | engagement 1.6%

## ドキュメント

- docs/specs/JSON_SPEC.md: JSON スキーマ
- docs/architecture/VIEWS_DESIGN.md: Views 設計書
- docs/phases/PHASE4_IMPLEMENTATION.md: Phase 4 実装レポート
- docs/operations/DEPLOYMENT_GUIDE.md: デプロイメントガイド

## 実行方法

Views 生成:
python generate_views.py --lecture-ids "01,02,03,04,05" --archive-dir "D:\AI_Data\video-insight-spec\archive" --api-key "YOUR_API_KEY"

品質検査:
python quality_check_phase4.py

---
Last Updated: 2026-03-26

