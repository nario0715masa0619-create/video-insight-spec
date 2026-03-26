# プロジェクト概要・実装進捗

YouTube 動画から『実行可能な知恵』を抽出し、JSON と SQLite で蓄積する仕組み。

## Phase ごとの実装詳細

### Phase 1 ✅ 完了
- 動画ダウンロード（yt-dlp）
- メタデータ抽出（ffprobe）

### Phase 2 ✅ 完了
- YouTube API 統合（video_meta 取得）
- OCR テキスト抽出（Tesseract）
- 音声テキスト化（Whisper）

### Phase 3 ✅ 完了
- Gemini AI ラベリング（52 個の知識要素抽出）
- ビジネステーマ・ファネルステージ・難易度分類
- YouTube API で video_meta 埋め込み

### Phase 4 ✅ 完了（2026-03-26）

#### Views 生成システム
- **engagement_scorer.py**: engagement_score 計算
  - 式: 0.6×purity_norm + 0.2×type_weight + 0.2×stage_weight
  - type_weight: framework 1.0, strategy 0.8, tactic 0.6, concept 0.4
  - stage_weight: クロージング 1.0, 継続・LTV 0.9, 比較 0.8, 教育 0.7, 興味 0.5, 認知 0.3

- **views_generator_service.py**: 3 つのビュー生成
  - competitive_view: YouTube メトリクス + top_3_pins_by_engagement
  - education_view: 難易度別分布 + 難易度ごと top_3_pins
  - self_improvement_view: ビジネステーマ・ファネルステージ集約 + funnel_flow

- **youtube_metadata_service.py**: YouTube Analytics API 統合
  - view_count, like_count, comment_count 取得
  - engagement_rate 計算: (like_count + comment_count) / view_count

#### 実行コマンド
\\\ash
python generate_views.py --lecture-ids "01,02,03,04,05" --archive-dir "D:\\AI_Data\\video-insight-spec\\archive" --api-key "YOUR_API_KEY"
\\\

#### メトリクス実績（2026-03-26 18:39:08 JST）
| 講座 | views | likes | comments | engagement_rate |
|------|-------|-------|----------|-----------------|
| 01 | 115,834 | 1,804 | 48 | 1.60% |
| 02 | 47,739 | 776 | 24 | 1.68% |
| 03 | 33,800 | 619 | 21 | 1.89% |
| 04 | 26,026 | 432 | 23 | 1.75% |
| 05 | 21,064 | 310 | 26 | 1.60% |

#### 品質検査
- quality_check_phase4.py: 40/40 合格 ✅

### Phase 4.1 ✅ 完了（2026-03-26）

#### Weekly Report Generation システム
- **weekly_report_generator.py**: baseline/delta レポート生成
  - Baseline: 初回スナップショット取得・記録
  - Delta: 前週比増減・成長率計算

- **report_utils.py**: delta 計算ユーティリティ
  - delta = current - baseline
  - growth_percentage = (delta / baseline) × 100

- **snapshot_manager.py**: スナップショット履歴管理
  - snapshot_history: [{ timestamp, view_count, like_count, comment_count, engagement_rate }]
  - タイムスタンプ形式: ISO8601+09:00（JST）

- **report_formatter.py**: レポート出力フォーマッタ
  - 公式機能: JSON 出力（reports/weekly/weekly_report_<YYYYMMDD>.json）
  - 実験的機能: HTML/Text（baseline 非対応、Phase 4.2 で改善予定）

#### 実行コマンド
\\\ash
python weekly_report_generator.py --lecture-ids "01,02,03,04,05" --archive-dir "D:\\AI_Data\\video-insight-spec\\archive" --output-dir "reports/weekly"
\\\

#### テスト結果
- Baseline 取得: 5 講座すべてで初回スナップショット記録 ✅
- Delta 計算（擬似テスト）:
  - view_count: +2,166（+1.87%）
  - like_count: +46（+2.55%）
  - comment_count: +4（+8.33%）
  - 0 除算エラー: なし ✅

#### 品質検査
- quality_check_phase4_1.py: 25/25 合格 ✅

#### JSON レポート構造例
\\\json
{
  "lecture_id": "01",
  "title": "#01【独学で習得】初心者でも分かるwebマーケティング講座",
  "status": "BASELINE_SET",
  "baseline_timestamp": "2026-03-26T18:39:08.348463+09:00",
  "baseline_metrics": {
    "view_count": 115834,
    "like_count": 1804,
    "comment_count": 48,
    "engagement_rate": 0.016
  },
  "message": "初回ベースラインスナップショットを記録しました。次週のレポートで増減を表示します。"
}
\\\

### Phase 4.2 📋 準備中

#### Competitor Analytics Views（予定）
- **portfolio_view**: 自社 vs 競合コース比較
  - role: "self" vs "competitor"
  - 難易度・ファネルステージ分布
  - 総ピン数・最新ビューアップ・エンゲージ率

- **growth_view**: 週次ビューアップランキング
  - 期間: YYYY-MM-DD to YYYY-MM-DD
  - top_by_view_growth: rank, lecture_id, delta, growth_rate

- **theme_view**: ビジネステーマ別トップコース抽出
  - themes: [{ business_theme, winning_lectures }]
  - 自社・競合の winning lecture ランキング

#### 設計書
- docs/phases/PHASE4_2_DESIGN.md: 詳細設計書
- docs/operations/ONBOARDING_COMPETITOR_ANALYTICS.md: クライアント オンボーディング

## ディレクトリ構成

\\\
video-insight-spec/
├── README.md                            # プロジェクト概要（最小限）
├── generate_views.py                    # Phase 4 エントリーポイント
├── weekly_report_generator.py           # Phase 4.1 エントリーポイント
├── converter/
│   ├── engagement_scorer.py
│   ├── views_generator_service.py
│   ├── youtube_metadata_service.py
│   ├── report_utils.py
│   ├── report_formatter.py
│   └── snapshot_manager.py
├── scripts/
│   ├── quality_check_phase4.py
│   ├── quality_check_phase4_1.py
│   ├── youtube_to_labeled_spec_pipeline.ps1
│   └── dev/                             # Legacy scripts
├── docs/
│   ├── PROJECT_OVERVIEW.md              # このファイル（詳細実装記録）
│   ├── specs/JSON_SPEC.md
│   ├── architecture/
│   │   ├── MODULES.md
│   │   └── VIEWS_DESIGN.md
│   ├── phases/
│   │   ├── PHASE4_IMPLEMENTATION.md
│   │   ├── PHASE4_1_NOTES.md
│   │   └── PHASE4_2_DESIGN.md
│   ├── operations/
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   └── ONBOARDING_COMPETITOR_ANALYTICS.md
│   └── vision/
│       └── COMPETITOR_ANALYTICS_V1.md
└── reports/weekly/                      # Weekly reports output
\\\

## 実績

| 項目 | 内容 |
|------|------|
| Phase 4 実装時間 | 予定 3h → 実績 ~30min（600% 効率） |
| Phase 4.1 実装時間 | 予定 3h → 実績 ~30min（600% 効率） |
| Views 生成成功率 | 5/5 講座（100%） |
| Quality Check | Phase 4: 40/40 ✅, Phase 4.1: 25/25 ✅ |
| 本番環境展開 | ✅ 準備完了 |
| ドキュメント完備 | ✅ 9 ファイル（MODULES.md, PHASE4_*_*.md 等） |

## 注意事項

### README.md ポリシー
- README.md は**最小限**に保つ（プロジェクト概要 + リンク集のみ）
- 詳細な実装記録は **docs/PROJECT_OVERVIEW.md** に記載
- Phase ごとの詳細は **docs/phases/PHASE*.md** に記載

### snapshot_history の仕様
- 形式: \{ timestamp, view_count, like_count, comment_count, engagement_rate }\
- タイムスタンプ: ISO8601+09:00（JST、UTC+9）
- 初回: baseline として記録
- 2 回目以降: delta 計算で前週比を算出

---
Last Updated: 2026-03-26
