# JSON Schema Specification v3.0

## Overview

video-insight-spec システムは YouTube 動画から知識を抽出し、ビジネス分析を行う統合型プラットフォームです。本ドキュメントは、各フェーズで生成される JSON ファイルとデータベーススキーマの完全な仕様を定義します。

**現在の実装状態：** Phase 4（views セクション実装完了）

---

## ファイル構成

各講座（lecture_id: 01～05）ごとに、以下の 3 つのファイルが生成されます：

| ファイル | 形式 | 役割 | 生成フェーズ |
|---------|------|------|-----------|
| \Mk2_Core_XX.json\ | JSON | 知識体系（center_pins）+ Gemini ラベル | Phase 3 |
| \Mk2_Sidecar_XX.db\ | SQLite | 動画内タイムスタンプ + OCR テキスト + 将来：メタデータ | Phase 2 |
| \insight_spec_XX.json\ | JSON | 最終統合ビュー（video_meta + knowledge_core + views） | Phase 3.3 → Phase 4 |

**ファイルパス例：**
\\\
D:\\AI_Data\\video-insight-spec\\archive\\
├─ Mk2_Core_01.json
├─ Mk2_Sidecar_01.db
├─ insight_spec_01.json
├─ Mk2_Core_02.json
...
└─ insight_spec_05.json
\\\

---

## Schema Details

### 1. insight_spec_XX.json （最終統合ファイル）

#### 1.1 video_meta セクション

YouTube ビデオのメタデータ。Phase 3.3 で YouTube API から取得。

\\\json
{
  "video_meta": {
    "video_id": "ORWMxLU-rI4",
    "channel_id": "UC4fJmw546DjVql_besPQ1TQ",
    "title": "#01【独学で習得】初心者でも分かるwebマーケティング講座",
    "url": "https://www.youtube.com/watch?v=ORWMxLU-rI4",
    "published_at": "2020-06-10T11:01:59Z"
  }
}
\\\

**重要注記：**
- \ideo_id\ は **YouTube video ID**（11 文字）であり、内部の lecture_id（"01"）ではありません
- \channel_id\ は YouTube チャンネル ID
- 本仕様では \ideo_id\ と \channel_id\ を区別します（よくある勘違い参照）

#### 1.2 knowledge_core セクション

知識体系。Gemini により以下のラベルが自動付与されます。

\\\json
{
  "knowledge_core": {
    "center_pins": [
      {
        "element_id": "cp_001",
        "type": "concept",
        "content": "Webマーケティングの基本は...",
        "base_purity_score": 90,
        "labels": {
          "business_theme": [
            "マーケティング",
            "Webマーケティング"
          ],
          "funnel_stage": "認知",
          "difficulty": "beginner"
        }
      },
      ... （計 52 pins）
    ],
    "knowledge_points": []
  }
}
\\\

**ラベル仕様：**

| ラベル | 型 | 値の例 | 説明 |
|-------|------|-------|------|
| \usiness_theme\ | 配列 | ["マーケティング", "集客"] | 複数のビジネステーマを列挙 |
| \unnel_stage\ | 単一値 | "認知" | 顧客ファネルのどの段階か（認知/興味/比較/教育/クロージング/継続・LTV） |
| \difficulty\ | 単一値 | "beginner" | 学習難易度（beginner/intermediate/advanced） |

#### 1.3 views セクション（Phase 4 で実装）

ビジネス分析用の 3 つの異なるビューを提供します。**知識の詳細は knowledge_core.center_pins に一元化され、views はダッシュボード用の要約ビュー + 代表ピン（top N）を含みます。**

##### 1.3.1 views.competitive

YouTube メトリクスと engagement に基づくランキング。

\\\json
{
  "competitive": {
    "###_metadata": {
      "snapshot_timestamp": "2026-03-29T23:59:59Z",
      "snapshot_history": [
        {
          "timestamp": "2026-03-29T23:59:59Z",
          "view_count": 115830,
          "like_count": 1804,
          "comment_count": 48
        }
      ]
    },
    "metrics": {
      "view_count": 115830,
      "like_count": 1804,
      "comment_count": 48,
      "engagement_rate": 0.016,
      "likes_per_1000_views": 15.57,
      "comments_per_1000_views": 0.41
    },
    "top_pins_by_engagement": [
      {
        "element_id": "cp_002",
        "type": "strategy",
        "content": "Webマーケティングの全体像を把握することで...",
        "business_theme": ["Webマーケティング", "ビジネスモデル"],
        "funnel_stage": "認知",
        "difficulty": "beginner",
        "engagement_score": 0.85
      },
      ... （上位 3 件）
    ]
  }
}
\\\

**engagement_score の定義：**

| 要素 | 重み | 説明 |
|------|------|------|
| base_purity_score（A） | 0.6 | 知識の純度。既存スコアを 0～1 に正規化 |
| type（B） | 0.2 | ピンのタイプ（framework=1.0, strategy=0.8, tactic=0.6, concept=0.4） |
| funnel_stage（D） | 0.2 | ファネル段階（クロージング=1.0, 比較=0.8, 教育=0.7, 興味=0.5, 認知=0.3, 継続・LTV=0.9） |

\\\
engagement_score = 0.6 * purity_norm + 0.2 * type_weight + 0.2 * stage_weight
（結果は 0.0～1.0 にクリップ）
\\\

##### 1.3.2 views.education

難易度別の学習ビュー。初心者向けか上級者向けか、どのピンが学習価値が高いかを一瞬で把握。

\\\json
{
  "education": {
    "difficulty_distribution": {
      "beginner": 9,
      "intermediate": 0,
      "advanced": 0
    },
    "top_pins_by_difficulty": {
      "beginner": [
        {
          "element_id": "cp_001",
          "content": "Webマーケティングの基本は...",
          "business_theme": ["マーケティング", "Webマーケティング"],
          "type": "concept"
        },
        ... （上位 3 件）
      ],
      "intermediate": [],
      "advanced": []
    }
  }
}
\\\

##### 1.3.3 views.self_improvement

ビジネステーマとファネル流れを可視化。どのファネル段階でどんなテーマが学べるか。

\\\json
{
  "self_improvement": {
    "business_theme_distribution": {
      "マーケティング": 8,
      "Webマーケティング": 4,
      "デジタルマーケティング": 2,
      "SNSマーケティング": 2,
      "集客": 3,
      ...
    },
    "funnel_stage_distribution": {
      "認知": 5,
      "教育": 2,
      "比較": 0,
      "クロージング": 1,
      "継続・LTV": 1
    },
    "funnel_flow": [
      {
        "stage": "認知",
        "pin_count": 5,
        "top_themes": ["マーケティング", "集客"],
        "average_difficulty": "beginner"
      },
      {
        "stage": "教育",
        "pin_count": 2,
        "top_themes": ["マーケティング", "セールス"],
        "average_difficulty": "beginner"
      },
      ... （全 6 段階）
    ]
  }
}
\\\

#### 1.4 _metadata セクション

処理メタデータ。どのフェーズで生成されたか、どのソースから取得されたかを記録。

\\\json
{
  "_metadata": {
    "converted_at": "2026-03-29T23:59:59Z",
    "source_system": "video-insight-spec",
    "conversion_version": "v2.0_phase4",
    "conversion_phase": "Phase 4",
    "data_sources": {
      "core_json": "Mk2_Core_XX.json",
      "sidecar_db": "Mk2_Sidecar_XX.db",
      "youtube_api": true,
      "youtube_analytics_api": false
    }
  }
}
\\\

---

### 2. Mk2_Core_XX.json

知識体系の生の抽出結果（Phase 2 で生成、Phase 3 で Gemini ラベル付与）。

\\\json
{
  "lecture_id": "01",
  "video_path": "D:\\AI_Data\\video-insight-spec\\downloaded_videos\\01_#01【独学で習得】...mp4",
  "generated_at": "2026-03-25T00:00:00Z",
  "knowledge_core": {
    "center_pins": [
      {
        "element_id": "cp_001",
        "type": "concept",
        "content": "...",
        "base_purity_score": 90,
        "labels": { ... }  // Phase 3 で追加
      }
    ]
  }
}
\\\

---

### 3. Mk2_Sidecar_XX.db

SQLite データベース。動画内のタイムスタンプ、OCR テキスト、将来的には YouTube メタデータを保存。

#### 3.1 evidence_index テーブル

\\\sql
CREATE TABLE evidence_index (
  element_id TEXT,           -- cp_001 など
  start_ms INTEGER,          -- 動画内の開始ミリ秒
  end_ms INTEGER,            -- 動画内の終了ミリ秒
  visual_text TEXT,          -- OCR で抽出されたテキスト
  visual_score REAL,         -- OCR 信頼度スコア（0～100）
  source_video_path TEXT     -- 元動画ファイルパス
);
\\\

#### 3.2 video_metadata テーブル（Phase 3.3 で追加予定）

\\\sql
CREATE TABLE video_metadata (
  lecture_id TEXT PRIMARY KEY,
  video_id TEXT,             -- YouTube video ID
  channel_id TEXT,           -- YouTube channel ID
  title TEXT,                -- 動画タイトル
  url TEXT,                  -- YouTube URL
  published_at TEXT,         -- ISO 8601 形式
  updated_at TIMESTAMP       -- 最後の更新日時
);
\\\

---

## Pipeline Flow

\\\
【Phase 1】
動画ダウンロード
  ↓
【Phase 2】
├─ YouTube API：メタデータ取得（channel_id, url, published_at）
├─ Whisper：音声を文字起こし
├─ OCR：動画内テキスト抽出
└─ 出力：Mk2_Core_XX.json, Mk2_Sidecar_XX.db
  ↓
【Phase 3】
├─ Gemini API：center_pins に labels（business_theme, funnel_stage, difficulty）を付与
├─ 全 52 pins ラベル付き完了（52/52）
└─ 出力：Mk2_Core_XX.json（labels 追加）
  ↓
【Phase 3.3】
├─ YouTube API：video_id から channel_id, title, url, published_at を取得
├─ video_mapping CSV：lecture_id → video_id のマッピング
└─ 出力：insight_spec_XX.json（video_meta 完成）
  ↓
【Phase 4】
├─ YouTube API：最新の view_count, like_count, comment_count を取得
├─ engagement_score 計算：base_purity + type + funnel_stage
├─ views セクション生成：competitive + education + self_improvement
└─ 出力：insight_spec_XX.json（views 完成）
  ↓
本番投入（サブスク開始）
\\\

---

## Current Status

| フェーズ | 状態 | 進捗 | 備考 |
|---------|------|------|------|
| Phase 1 | ✅ 完了 | 5 講座ダウンロード | - |
| Phase 2 | ✅ 完了 | Mk2_Core, Mk2_Sidecar 生成 | - |
| Phase 3 | ✅ 完了 | 52 pins ラベル付き（Gemini） | 品質検査：5/5 合格 |
| Phase 3.3 | ✅ 完了 | video_meta 完成 | 品質検査：5/5 合格 |
| Phase 4 | ✅ 完了 | views セクション実装 | engagement_score 導入 |
| Phase 4.1 | ⏳ 予定 | 週次レポート実装 | サブスク配信用 |
| Phase 5 | ⏳ 予定 | 本番環境セットアップ | - |

---

## よくある勘違い

### ❌ 勘違い 1: video_id と lecture_id の混同

**正:** 
- \lecture_id\ = システム内部 ID（"01", "02"）
- \ideo_id\ = YouTube video ID（"ORWMxLU-rI4"）

insight_spec の \ideo_meta.video_id\ には **YouTube video ID** が入ります。

### ❌ 勘違い 2: video_id と channel_id の混同

**正:**
- \ideo_id\ = 特定の動画を識別（11 文字）
- \channel_id\ = 動画を投稿したチャンネルを識別（24 文字）

例：
\\\
video_id:   ORWMxLU-rI4    （video=講座 01）
channel_id: UC4fJmw546DjVql_besPQ1TQ  （channel=マーケティング講座チャンネル）
\\\

### ❌ 勘違い 3: views に全 pins の詳細を含めるべき

**正:** 
views は **ダッシュボード用要約ビュー** です。
- 集計統計（distribution）
- 代表ピン（top 3）のみ

詳細が必要な場合は knowledge_core.center_pins を参照してください。

---

## 設計原則

1. **Single Responsibility**
   - Mk2_Core: 知識体系
   - Mk2_Sidecar: エビデンス + メタデータ
   - insight_spec: 統合ビュー

2. **Progressive Disclosure**
   - views: 要約 + top N
   - knowledge_core: 詳細

3. **Extensibility**
   - views の新規セクション追加は容易
   - メタデータ更新は _metadata で追跡可能

---

**最終更新：** 2026-03-29
**作成者：** Phase 4 Implementation
**バージョン：** v3.0
