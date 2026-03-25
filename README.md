# video-insight-spec

YouTube動画から実行可能な知恵を抽出し、JSONとSQLiteに蓄積するシステム

## プロジェクト進捗

Phase 1: ✅ 基本JSON化
Phase 2: ✅ テストスイート (77/77 PASS)
Phase 3: ✅ Geminiラベル付与 (52個のcenter_pins)

## Phase 3 完了（2026-03-25）

- YouTube → MP4 → Mk2_Core → insight_spec → labeled JSON パイプライン実装
- 5講座処理完了、52個のcenter_pinsにラベル付与
- 品質検証: 5/5講座 OK
- 処理時間: 約20分
## 📁 ファイル構成

\\\
video-insight-spec/
├── README.md
├── NOTE_ARTICLE_DRAFT.md
├── requirements.txt
├── pytest.ini
├── .env.example              # セットアップテンプレート
├── .env.test                 # テスト設定
├── .gitignore
│
├── 【メインスクリプト】
├── youtube_to_labeled_spec_pipeline.ps1    # Phase 3 統合パイプライン
├── master_batch_refiner.py                 # Step 2: Mk2_Core 生成
├── convert_to_insight_spec_phase1.py       # Step 3: insight_spec 生成
├── expand_insight_spec_with_gemini.py      # Step 4: Gemini ラベル付与
│
├── converter/                  # Python modules
│   ├── __init__.py
│   ├── gemini_knowledge_expander.py
│   ├── gemini_llm_client.py           # Phase 3.1 new
│   ├── center_pin_labeling_service.py # Phase 3.1 planned
│   ├── insight_spec_repository.py     # Phase 3.1 planned
│   └── その他モジュール
│
├── analysis/                   # Analysis & validation scripts
│   ├── validate_pipeline_output.ps1
│   └── analyze_phase3_labels.py
│
├── docs/                       # Documentation
│   ├── phases/                 # Phase implementation docs
│   │   ├── PHASE1_5_HOTFIXES.md
│   │   ├── PHASE2_2_YOUTUBE_API_INTEGRATION.md
│   │   ├── PHASE2_2_1_ENGAGEMENT_METRICS.md
│   │   ├── PHASE2_2_2_OCR_TEXT_CLEANING.md
│   │   ├── PHASE2_2_3_VIDEO_ID_ENRICHER.md
│   │   ├── PHASE3_GEMINI_KNOWLEDGE_EXPANSION.md
│   │   ├── PHASE3_PREPARATION_OCCURRENCE_IMPORTANCE.md
│   │   └── PHASE3_IMPROVEMENT_ROADMAP.md
│   │
│   └── specs/                  # Specification docs
│       ├── JSON_SPEC.md
│       └── WORKFLOW_IMPLEMENTATION_MAP.md
│
├── scripts/                    # Development & utility scripts
│   └── dev/                    # デバッグ・開発スクリプト（16個）
│       ├── phase2_*.py
│       ├── add_importance_schema.py
│       ├── calculate_occurrence_and_importance.py
│       ├── check_content.py
│       └── batch_label_lectures_02_21.ps1
│
├── targets/                    # Target URLs
│   └── marketing_univ_top5.txt
│
├── tests/                      # Test suite
│   ├── conftest.py
│   ├── test_*.py
│   └── TEST_IMPROVEMENT_PLAN.md
│
├── logs/                       # Execution logs
├── results/                    # Validation results
├── batch_refine_work/          # Working directory
├── quality_validation_results/ # Quality check results
└── phase2_2_output/            # Legacy output directory
\\\
## 🎯 講座別結果

| 講座 | Core Pins | 平均文字数 | ラベル | 検証 |
|------|-----------|----------|--------|------|
| Lecture 01 | 10 | 141 chars | ✅ | ✅ |
| Lecture 02 | 10 | 204 chars | ✅ | ✅ |
| Lecture 03 | 11 | 150 chars | ✅ | ✅ |
| Lecture 04 | 10 | 116 chars | ✅ | ✅ |
| Lecture 05 | 11 | 154 chars | ✅ | ✅ |

## 🚀 クイックスタート

### セットアップ

1. .env.example をコピーして .env を作成
2. GEMINI_API_KEY と ARCHIVE_OUTPUT_DIR を設定
3. PowerShell で以下を実行:

.\youtube_to_labeled_spec_pipeline.ps1

### 品質検証

.\analysis\validate_pipeline_output.ps1

## 🔒 セキュリティ

- .env ファイルは .gitignore に登録済み
- API キーは環境変数から読み込み
- 過去に Google API キーが流出した場合は Google Cloud Console で無効化

## 📚 関連ドキュメント

- JSON_SPEC.md - JSON スキーマ・DB 設計
- AGENTS.md - AI エージェント仕様
- WORKFLOW_IMPLEMENTATION_MAP.md - ワークフロー仕様
- PHASE3_COMPLETION_SUMMARY.md - Phase 3 詳細レポート
- PHASE3_IMPROVEMENT_ROADMAP.md - Phase 3+ ロードマップ

## 📄 ライセンス

MIT License

## 最終更新

2026-03-25 - Phase 3 完了（52 center_pins ラベル付与、品質検証 5/5 OK）


