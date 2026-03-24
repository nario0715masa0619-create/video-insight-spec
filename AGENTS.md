# AGENTS.md

## 目的
このドキュメントは、Genspark などの AI エージェントが `video-insight-spec` リポジトリを活用・拡張する際の指南書です。

`video-insight-spec` は、主に以下の責務を持つリポジトリです：
1. **JSON スキーマ・DB 設計** の仕様化と管理
2. **実装ガイドライン** (`PHASE*.md`) の提供
3. **ドキュメント生成・更新** による設計の最新化

> 💡 **実装コード自体は別リポジトリ（video-scraper など）で管理されていますが、このリポジトリの仕様に基づいて開発が進められます。**

---

## このリポジトリについて

- **リポジトリ名**：`video-insight-spec`
- **目的**：  
  動画スクレイピングで取得したテキストから「実行可能な知恵」を抽出し、  
  1 本 1 JSON で保存するための **仕様書（スキーマ定義）** をまとめる。
- **実装コード・機密情報**：置かない。  
  ここにあるのは **設計レベルの情報だけ**。

---

## 重要ファイル

### スキーマ・仕様
- **`JSON_SPEC.md`**  
  - JSON の構造と各フィールドの意味を定義しているメイン仕様書
  - 3 レイヤー構成：
    - `video_meta`：動画の汎用メタ情報  
    - `knowledge_core`：センターピン + Gemini 拡張知識  
    - `views`：用途別ビュー（competitive / self_improvement など）

### 実装ガイド
- **`PHASE1_IMPLEMENTATION.md`** - Phase 1（基本 JSON 化）
- **`PHASE2_2_YOUTUBE_API_INTEGRATION.md`** - Phase 2.2（YouTube メトリクス取得）
- **`PHASE2_2_1_ENGAGEMENT_METRICS.md`** - Phase 2.2.1（エンゲージメント指標計算）
- **`PHASE2_2_2_OCR_TEXT_CLEANING.md`** - Phase 2.2.2（OCR テキストクリーニング）
- **`PHASE2_2_3_VIDEO_ID_ENRICHER.md`** - Phase 2.2.3（YouTube Video ID 補充）
- **`PHASE3_PREPARATION_OCCURRENCE_IMPORTANCE.md`** - Phase 3 準備（出現回数スコア計算）
- **`PHASE3_GEMINI_KNOWLEDGE_EXPANSION.md`** - Phase 3（Gemini による知識拡張）

---

## 処理フロー全体図

1. **video-scraper** → Mk2_Core_XX.json + Mk2_Sidecar_XX.db
   - Whisper で音声を文字起こし
   - FFmpeg でフレーム抽出 + EasyOCR で画面テキスト抽出
   - Gemini 3 Pro でセンターピン生成
   - Sidecar DB 作成

2. **Phase 1** → insight_spec_XX.json（基本形）
   - JSON スキーマに変換

3. **Phase 2.2** → YouTube メトリクス追加
   - YouTube Data API v3 で動画メタデータ取得
   - views, likes, comments を追加

4. **Phase 2.2.1** → エンゲージメント指標計算
   - engagement_rate = (likes + comments × 2) / views
   - likes_per_1000_views、comments_per_1000_views を計算

5. **Phase 2.2.2** → OCR テキストクリーニング
   - UI ノイズ除去（26.38% 削減）
   - 日本語 OCR 誤認識補正
   - テキスト正規化

6. **Phase 2.2.3** → Video ID 補充
   - YouTube API で video_id を検索
   - video_meta に追加

7. **Phase 3 準備** → 出現回数・重要度スコア
   - occurrence_count をカウント
   - importance_score を計算

8. **Phase 3** → Gemini で gemini_expansion 生成
   - business_theme（1～3 個、日本語）
   - funnel_stage（1 個、日本語）
   - difficulty（beginner/intermediate/advanced）

**最終出力**：insight_spec_XX.json（完全版）

---

## 完了フェーズ一覧

| Phase | 名称 | 状態 | 詳細 |
|-------|------|------|------|
| 1 | 基本 JSON 化 | ✅ 完了 | スキーマ定義・DB 設計 |
| 2.0～2.1 | テストスイート | ✅ 完了 | 62/62 テスト PASS |
| 2.2 | YouTube API 統合 | ✅ 完了 | 動画メタデータ自動取得 |
| 2.2.1 | エンゲージメント指標 | ✅ 完了 | engagement_rate 等計算 |
| 2.2.2 | OCR テキストクリーニング | ✅ 完了 | UI ノイズ・誤認識除去（26.38% 削減） |
| 2.2.3 | YouTube Video ID Enricher | ✅ 完了 | video_id 自動検索・補充 |
| 3 準備 | 出現回数スコア | ✅ 完了 | occurrence_count / importance_score |
| 3 実装 | Gemini ラベル付与 | ✅ 完了 | business_theme / funnel_stage / difficulty |

---

## Gemini API の使用仕様

### モデル情報
- **モデル名**: `gemini-3-pro-preview`
- **出力形式**: JSON（`response_mime_type: "application/json"`）
- **使用フェーズ**: 
  - **video-scraper**: Mk2_Core_XX.json 生成（FACT/LOGIC/SOP/CASE タグ付きセンターピン）
  - **Phase 3**: gemini_expansion 生成（related_concepts / practical_applications / cautions）
  - **Phase 3 実装**: labels 生成（business_theme / funnel_stage / difficulty）

### 環境変数
```bash
GEMINI_API_KEY=<実際の API キー>
GEMINI_MODEL_ID=gemini-3-pro-preview
