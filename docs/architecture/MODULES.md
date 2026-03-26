# Module Reference: Phase 4 / 4.1

このドキュメントは、Phase 4 と Phase 4.1 で追加された全モジュール・スクリプトの役割を説明します。

---

## Converter Modules (converter/)

### converter/engagement_scorer.py
**役割**: Center pin のエンゲージメントスコア計算エンジン

**機能**:
- calculate_engagement_score(pin): pin の engagement_score を計算
- 計算式: 0.6 × purity_norm + 0.2 × type_weight + 0.2 × stage_weight

---

### converter/views_generator_service.py
**役割**: Views セクション生成エンジン

**機能**:
- generate_views(): views セクション全体を生成
- _generate_competitive_view(): YouTube メトリクス + top_pins
- _generate_education_view(): 難易度分布
- _generate_self_improvement_view(): テーマ・ファネル分布

---

### converter/youtube_metadata_service.py
**役割**: YouTube Analytics API クライアント

**機能**:
- get_video_analytics(video_id): 再生数・いいね数・コメント数を取得

---

### converter/report_utils.py
**役割**: Weekly Report 用ユーティリティ関数群

**機能**:
- calculate_delta(): 前週との差分を計算
- calculate_growth_percentage(): 成長率を計算
- format_metric(): メトリクス値をフォーマット

---

### converter/snapshot_manager.py
**役割**: snapshot_history 管理クラス

**機能**:
- load_insight_spec(): JSON を読み込み
- save_insight_spec(): JSON を保存
- add_snapshot(): 新しい snapshot を追加
- get_latest_snapshot(): 最新 snapshot を取得

---

### converter/report_formatter.py
**役割**: レポート出力フォーマッター

**機能**:
- to_html(): JSON → HTML
- to_json(): JSON 形式出力
- to_text(): プレーンテキスト出力

**ステータス**: JSON は公式機能、HTML/テキストは実験的機能

---

## CLI Scripts

### generate_views.py
**役割**: Phase 4 Views 生成エントリーポイント

**実行例**: python generate_views.py --lecture-ids 01,02,03,04,05 --archive-dir D:\AI_Data\video-insight-spec\archive

---

### weekly_report_generator.py
**役割**: Phase 4.1 Weekly Report 生成エントリーポイント

**実行例**: python weekly_report_generator.py --lecture-ids 01,02,03,04,05 --archive-dir D:\AI_Data\video-insight-spec\archive --output-dir reports/weekly

---

## Quality Check Scripts

### quality_check_phase4.py
**役割**: Phase 4 Views 生成品質検査
**検査項目**: 8項目/講座（views, metrics, engagement_rate など）
**合格基準**: 40/40

---

### quality_check_phase4_1.py
**役割**: Phase 4.1 Weekly Report 生成品質検査
**検査項目**: 5項目/講座（snapshot_history, metrics, timestamp）
**合格基準**: 25/25

---

## Summary

| モジュール | 型 | 役割 |
|-----------|----|----|
| engagement_scorer.py | Core | Engagement スコア計算 |
| views_generator_service.py | Core | Views 生成 |
| youtube_metadata_service.py | Core | YouTube API |
| report_utils.py | Core | Delta 計算 |
| report_formatter.py | Core | レポートフォーマット |
| snapshot_manager.py | Core | スナップショット管理 |
| generate_views.py | CLI | Views 生成実行 |
| weekly_report_generator.py | CLI | レポート生成実行 |
| quality_check_phase4.py | QC | Phase 4 品質検査 |
| quality_check_phase4_1.py | QC | Phase 4.1 品質検査 |

最終更新: 2026-03-26

