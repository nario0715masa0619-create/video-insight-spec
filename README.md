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

### 生成ファイル（D:\AI_Data\video-insight-spec\archive）

| ファイル | 説明 |
|---------|------|
| Mk2_Core_01-05.json | Whisper + EasyOCR + Gemini による抽出結果 |
| insight_spec_01-05.json | ラベル付与済みの insight_spec |
| Mk2_Sidecar_01-05.db | SQLite DB（evidence_index テーブル） |
| Mk2_OCR_01-05.txt | EasyOCR で抽出したテキスト |

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

