# JSON スキーマ仕様書 v3（video-insight-spec）

## 概要

このプロジェクトは YouTube 動画から知識を抽出し、構造化データとして管理するシステムです。
1 本の動画に対して 3 つのファイルが生成されます：
1. **Mk2_Core_XX.json** - 知識コア（center_pins, knowledge_points）
2. **Mk2_Sidecar_XX.db** - エビデンスインデックス + メタデータ DB（SQLite）
3. **insight_spec_XX.json** - 最終成果物（video_meta + ラベル付き知識）

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

役割: center_pins のエビデンス（OCR テキスト、タイムスタンプ）+ YouTube メタデータを SQLite で管理

### テーブル 1: evidence_index

カラム構成:
  element_id: center_pin の ID（TEXT）
  start_ms: 動画内の開始時間（INTEGER、ミリ秒）
  end_ms: 動画内の終了時間（INTEGER、ミリ秒）
  visual_text: OCR で抽出したテキスト（TEXT）
  visual_score: OCR テキスト信頼度（REAL、0-100）
  source_video_path: 動画ファイルのパス（TEXT）

### テーブル 2: video_metadata（Phase 3.3 で追加）

役割: YouTube メタデータの一元管理。Phase 4 以降で views 生成時に参照

カラム構成:
  lecture_id: 講座ID（TEXT、主キー）
  video_id: YouTube video_id（TEXT）
  channel_id: YouTube チャンネルID（TEXT）
  title: 動画タイトル（TEXT）
  url: YouTube URL（TEXT）
  published_at: 公開日時（ISO8601）
  updated_at: メタデータ更新日時（TIMESTAMP）

## 3. insight_spec_XX.json スキーマ

役割: 最終成果物。video_meta（YouTube メタデータ）+ knowledge_core（ラベル付き）+ views

トップレベルキー:
  video_meta: YouTube メタデータセクション
  knowledge_core: Mk2_Core と同じ（ラベル付与）
  views: 用途別ビュー
  _metadata: メタデータ

video_meta 仕様（Phase 3.3 で完成）:
  video_id: 講座ID（"01" など）
  channel_id: YouTube チャンネルID（Phase 3.3 で設定）
  title: 動画タイトル（Phase 3.3 で設定）
  url: YouTube URL（Phase 3.3 で設定）
  published_at: 公開日時（ISO8601、Phase 3.3 で設定）

knowledge_core: Mk2_Core と同じ（center_pins にラベル付与）

views: 用途別ビュー（Phase 4 で実装予定）

## パイプラインフロー

入力: downloaded_videos/（動画ファイル）

↓ Phase 2（YouTube API, OCR, Whisper）

中間成果物:
  Mk2_Core_XX.json - lecture_id, video_path, knowledge_core.center_pins（ラベルなし）
  Mk2_Sidecar_XX.db - evidence_index（OCR テキスト、タイムスタンプ）

↓ Phase 3（Gemini ラベル付与）

最終成果物（中間）:
  insight_spec_XX.json - video_meta: 未完成（null）、center_pins: ラベル付与済

↓ Phase 3.3（YouTube API で video_meta 補完）

処理フロー:
  1. generate_video_mapping.py - downloaded_videos から video_mapping_new.csv 生成（一時ファイル）
  2. enrich_insight_spec_with_youtube_metadata.py - CSV から video_id を読み込み、insight_spec に反映
  3. update_mk2_sidecar_with_youtube_metadata.py - CSV から video_id を読み込み、Mk2_Sidecar.video_metadata に記録
  4. クリーンアップ - video_mapping_new.csv を削除（または archive に保存）

完成版:
  insight_spec_XX.json - video_meta: 完全（YouTube API から取得）、center_pins: ラベル付与済
  Mk2_Sidecar_XX.db - video_metadata テーブル追加（Phase 4 以降で参照）

↓ Phase 4（views 実装）

最終出力:
  insight_spec_XX.json - views セクション追加（competitive, self_improvement 等）

## 現在のステータス

Phase 1: 完了 - JSON 構造化
Phase 2: 完了 - YouTube API, OCR, Whisper
Phase 3: 完了 - Gemini ラベル付与（52 ピン）
Phase 3.1: 完了 - コード設計改善（責務分離）
Phase 3.2: 完了 - google.generativeai -> google-genai 移行
Phase 3.3: 進行中 - YouTube API で video_meta 補完
  ✅ YouTubeMetadataService 実装完了
  ✅ generate_video_mapping.py 実装完了
  ✅ enrich_insight_spec_with_youtube_metadata.py 実装完了
  ⏳ update_mk2_sidecar_with_youtube_metadata.py（次実装）
  ⏳ Mk2_Sidecar_XX.db に video_metadata テーブル追加
Phase 4: 予定 - views 実装、本番環境対応

## 設計決定事項（Phase 3.3）

### 1. video_mapping.csv の管理
  - 一時ファイルとして phase2_2_output/video_mapping_new.csv に保存
  - 処理完了後に削除または archive に移動
  - 本体管理: Mk2_Sidecar_XX.db.video_metadata テーブル

### 2. メタデータの一元管理
  - Mk2_Sidecar_XX.db に video_metadata テーブルを追加
  - Phase 4 以降で views 生成時に Sidecar DB から参照
  - 拡張性向上（新しいメタデータ追加時に DB に記録するのみ）

### 3. ファイル間の役割分担
  - Mk2_Core_XX.json: 知識抽出のみ（video_meta は追加しない）
  - Mk2_Sidecar_XX.db: エビデンス + メタデータ管理
  - insight_spec_XX.json: 最終成果物（すべての情報を統合）

## 注意事項

1. video_meta の完成フロー
   - Phase 3 完了時: video_meta は {video_id: "01" のみ、その他は null}
   - Phase 3.3 完了時: video_meta は完全（channel_id, title, url, published_at も埋まる）
   - 中間状態は仕様上正常

2. Mk2_Sidecar の拡張計画
   - 現在: evidence_index（OCR テキスト）
   - Phase 3.3: video_metadata（YouTube メタデータ）追加
   - Phase 4 以降: engagement_metrics（再生数、いいね数等）追加予定

3. スキーマの拡張性
   - views セクションで用途別ビューを追加可能
   - knowledge_points セクション（現在は未使用）で複雑な知識構造を管理予定
   - video_metadata テーブルに新しいカラム追加可能
