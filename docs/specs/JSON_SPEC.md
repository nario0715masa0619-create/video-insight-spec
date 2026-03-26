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

役割: center_pins のエビデンス（OCR テキスト、動画内のタイムスタンプ）+ YouTube メタデータを SQLite で管理

### テーブル 1: evidence_index

カラム構成:
  element_id: center_pin の ID（TEXT）
  start_ms: 動画内の開始時間（INTEGER、ミリ秒）
  end_ms: 動画内の終了時間（INTEGER、ミリ秒）
  visual_text: OCR で抽出したテキスト（TEXT）
  visual_score: OCR テキスト信頼度（REAL、0-100）
  source_video_path: 動画ファイルのパス（TEXT）

### テーブル 2: video_metadata（Phase 3.3 で追加）

役割: YouTube から取得した動画メタデータを一元管理。Phase 4 以降で views 生成時に参照可能。

カラム構成:
  lecture_id: 講座ID（TEXT、主キー） - 例: "01"
  video_id: YouTube video_id（TEXT） - 例: "ORWMxLU-rI4"
  channel_id: YouTube チャンネルID（TEXT） - 例: "UC4fJmw546DjVql_besPQ1TQ"
  title: 動画タイトル（TEXT） - 例: "#01【独学で習得】初心者でも分かるwebマーケティング講座"
  url: YouTube URL（TEXT） - 例: "https://www.youtube.com/watch?v=ORWMxLU-rI4"
  published_at: 公開日時（TEXT） - 例: "2020-06-10T11:01:59Z"
  updated_at: メタデータ更新日時（TIMESTAMP）

重要な区別:
  lecture_id = "01" は【内部 ID】このプロジェクト内で使う
  video_id = "ORWMxLU-rI4" は【外部 ID】YouTube で使われる

## 3. insight_spec_XX.json スキーマ

役割: 最終成果物。video_meta（YouTube メタデータ）+ knowledge_core（ラベル付き）

トップレベルキー:
  video_meta: YouTube メタデータセクション
  knowledge_core: Mk2_Core と同じ（ラベル付与）
  views: 用途別ビュー
  _metadata: メタデータ

video_meta 仕様:
  video_id: YouTube video_id（例: "ORWMxLU-rI4"）【重要】Phase 3.3 で YouTube API から取得した値に更新される
  注意: lecture_id（"01" など）とは異なります
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

処理ステップ:
  1. generate_video_mapping.py
     - downloaded_videos フォルダのファイル名から YouTube を検索
     - video_id を取得し、video_mapping_new.csv に記録
  
  2. enrich_insight_spec_with_youtube_metadata.py
     - video_mapping_new.csv を読み込み
     - insight_spec_XX.json の video_meta を YouTube メタデータで更新
     - video_id, channel_id, title, url, published_at を反映
  
  3. update_mk2_sidecar_with_youtube_metadata.py【今後実装予定】
     - video_mapping_new.csv を読み込み
     - Mk2_Sidecar_XX.db の video_metadata テーブルに記録
  
  4. クリーンアップ
     - video_mapping_new.csv を削除（一時ファイル）

完成版:
  insight_spec_XX.json
    - video_meta: 完全（YouTube API から取得）
      video_id = "ORWMxLU-rI4"（YouTube video_id）
      channel_id = "UC4fJmw546DjVql_besPQ1TQ"（YouTube チャンネルID）
      title, url, published_at も埋まる
    - knowledge_core.center_pins: ラベル付与済
  
  Mk2_Sidecar_XX.db
    - video_metadata テーブル追加

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
  ✅ Lecture 01-05 で video_meta 完成（品質検査: 5/5 合格）
  ⏳ update_mk2_sidecar_with_youtube_metadata.py（次実装予定）
Phase 4: 予定 - views 実装、本番環境対応



## よくある勘違い

### 勘違い 1: video_id は講座番号？
❌ 間違い: "video_id": "01"
✅ 正しい: "video_id": "ORWMxLU-rI4"
説明: "01" は lecture_id（内部 ID）です。YouTube で使われるのは "ORWMxLU-rI4" のような 11 文字の video_id です。

### 勘違い 2: channel_id と video_id は同じ？
❌ 間違い: "channel_id": "ORWMxLU-rI4"（これは video_id）
✅ 正しい:
  "video_id": "ORWMxLU-rI4"（個別の動画を識別）
  "channel_id": "UC4fJmw546DjVql_besPQ1TQ"（チャンネル全体を識別）
説明: video_id は個別の動画、channel_id はチャンネルを識別します。形式が異なります。



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
