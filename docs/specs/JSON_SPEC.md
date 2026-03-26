# JSON スキーマ仕様書 v2（video-insight-spec）

## 概要

このプロジェクトは YouTube 動画から知識を抽出し、構造化データとして管理するシステムです。
1 本の動画に対して 3 つのファイルが生成されます：
1. **Mk2_Core_XX.json** - 知識コア（center_pins, knowledge_points）
2. **Mk2_Sidecar_XX.db** - エビデンスインデックス（OCR テキスト、タイムスタンプ）
3. **insight_spec_XX.json** - 最終成果物（video_meta + ラベル付け）

## ファイル構成（D:\AI_Data\video-insight-spec\archive）

archive/
  Mk2_Core_01.json through Mk2_Core_05.json
  Mk2_Sidecar_01.db through Mk2_Sidecar_05.db
  insight_spec_01.json through insight_spec_05.json

## 1. Mk2_Core_XX.json スキーマ

役割: 動画から抽出した知識の構造化データ

トップレベルキー:
  lecture_id: 講座ID（"01" など）
  video_path: 動画ファイルパス
  generated_at: 生成日時（ISO8601）
  knowledge_core: 知識コアセクション

knowledge_core.center_pins（Phase 3 で Gemini ラベル付与）:
  element_id: center_pin ID（cp_001 など）
  type: FACT, LOGIC, SOP など
  content: 知識内容
  base_purity_score: 知識品質スコア（0-100）
  labels: Phase 3.2 で追加（以下を参照）

ラベル仕様（Phase 3.2 で追加）:
  business_theme: 配列形式、複数のビジネステーマを指定
    例: ["マーケティング", "Webマーケティング"]
  funnel_stage: 購買ファネル段階
    値: "認知", "興味・関心", "教育", "比較検討", "クロージング", "継続・LTV"
  difficulty: 難易度レベル
    値: "beginner", "intermediate", "advanced"

## 2. Mk2_Sidecar_XX.db スキーマ

役割: center_pins のエビデンス（OCR テキスト、動画内のタイムスタンプ）を SQLite で管理

テーブル: evidence_index

カラム構成:
  element_id: center_pin の ID（TEXT）
  start_ms: 動画内の開始時間（INTEGER、ミリ秒）
  end_ms: 動画内の終了時間（INTEGER、ミリ秒）
  visual_text: OCR で抽出したテキスト（TEXT）
  visual_score: OCR テキスト信頼度（REAL、0-100）
  source_video_path: 動画ファイルのパス（TEXT）

## 3. insight_spec_XX.json スキーマ

役割: 最終成果物。video_meta（YouTube メタデータ）+ knowledge_core（ラベル付き）

トップレベルキー:
  video_meta: YouTube メタデータセクション
  knowledge_core: Mk2_Core と同じ（ラベル付与）
  views: 用途別ビュー
  _metadata: メタデータ

video_meta 仕様:
  video_id: "01" など、講座ID（現在: 設定済み）
  channel_id: YouTube チャンネルID（現在: null、Phase 3.3 で設定予定）
  title: 動画タイトル（現在: "Lecture 01" など、改善予定）
  url: YouTube URL（現在: null、Phase 3.3 で設定予定）
  published_at: 公開日時（ISO8601、現在: null、Phase 3.3 で設定予定）

knowledge_core: Mk2_Core と同じ（center_pins にラベル付与）

views: 用途別ビュー（Phase 4 で実装予定）

## パイプラインフロー

入力: downloaded_videos/（動画ファイル）

↓ Phase 2（YouTube API, OCR, Whisper）

中間成果物:
  Mk2_Core_XX.json - lecture_id, video_path, knowledge_core.center_pins（ラベルなし）
  Mk2_Sidecar_XX.db - evidence_index（OCR テキスト、タイムスタンプ）

↓ Phase 3（Gemini ラベル付与）

最終成果物:
  insight_spec_XX.json
    - video_meta: 未完成（channel_id, url, published_at = null）
    - knowledge_core.center_pins: ラベル付与済（business_theme, funnel_stage, difficulty）

↓ Phase 3.3（YouTube API で video_meta 補完）

完成版:
  insight_spec_XX.json
    - video_meta: 完全（YouTube API から取得）
    - knowledge_core.center_pins: ラベル付与済

## 現在のステータス

Phase 1: 完了 - JSON 構造化
Phase 2: 完了 - YouTube API, OCR, Whisper
Phase 3: 完了 - Gemini ラベル付与（52 ピン）
Phase 3.1: 完了 - コード設計改善（責務分離）
Phase 3.2: 完了 - google.generativeai -> google-genai 移行
Phase 3.3: 予定 - YouTube API で video_meta 補完
Phase 4: 予定 - views 実装、本番環境対応

## 注意事項

1. video_meta の未完成状態
   - Phase 3 ラベル付与完了時点では、channel_id, url, published_at が null
   - Phase 3.3（YouTube API 統合）で完全に埋める予定
   - 現在の状態は仕様上正常

2. Mk2_Sidecar の役割
   - center_pins のエビデンス管理
   - 将来的に「どこから知識を得たか」をトレース可能にする
   - 現在は OCR テキストのみ記録

3. スキーマの拡張性
   - views セクションで用途別ビューを追加可能
   - knowledge_points セクション（現在は未使用）で複雑な知識構造を管理予定
