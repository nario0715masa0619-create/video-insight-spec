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
動画入力（MP4） ↓ [video-scraper リポジトリ] ├─ Step 1: Whisper で音声を文字起こし ├─ Step 2: FFmpeg でフレーム抽出 + EasyOCR で画面テキスト抽出 ├─ Step 3: Gemini 3 Pro でセンターピン生成（Mk2_Core_XX.json 出力） └─ Step 4: Sidecar DB 作成（Mk2_Sidecar_XX.db 出力）

↓
[video-insight-spec リポジトリ / Phase 1] ├─ Mk2_Core_XX.json + Mk2_Sidecar_XX.db を読込 ├─ JSON スキーマに変換 └─ insight_spec_XX.json 出力（基本形）

↓
[Phase 2.2: YouTube API 統合] ├─ YouTube Data API v3 で動画メタデータ取得 ├─ views、likes、comments を取得 └─ insight_spec_XX.json に views.competitive を追加

↓
[Phase 2.2.1: エンゲージメント指標] ├─ engagement_rate = (likes + comments × 2) / views ├─ likes_per_1000_views、comments_per_1000_views を計算 └─ insight_spec_XX.json に統合

↓
[Phase 2.2.2: OCR テキストクリーニング] ├─ Sidecar DB の visual_text から UI ノイズを除去 ├─ 日本語 OCR 誤認識を補正 ├─ テキスト正規化（スペース・改行整理） └─ evidence_index テーブルを更新

↓
[Phase 2.2.3: YouTube Video ID Enricher] ├─ center_pin.title から YouTube API で video_id を検索 ├─ 取得した video_id を video_meta に追加 └─ insight_spec_XX.json の video_id を確定

↓
[Phase 3 準備: 出現回数・重要度スコア計算] ├─ evidence_index の visual_text をグルーピング ├─ 各テキストの出現回数をカウント（occurrence_count） ├─ importance_score = occurrence_count を計算 ├─ evidence_index テーブルに追加 └─ Gemini への入力データとして準備

↓
[Phase 3: Gemini による知識点自動拡張] ├─ importance_score 上位 5 件のセンターピンを選定 ├─ Gemini 3 Pro で以下を生成： │ ├─ related_concepts（関連概念 3 件） │ ├─ practical_applications（実務応用例 3 件） │ └─ cautions（注意点 3 件） ├─ JSON を gemini_expansion フィールドに統合 └─ 最終版 insight_spec_XX.json 出力

最終成果物：insight_spec_XX.json ├─ video_meta（動画メタデータ + video_id） ├─ knowledge_core（センターピン + gemini_expansion） ├─ views.competitive（YouTube メトリクス + エンゲージメント指標） └─ _metadata（処理履歴・タイムスタンプ）


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
| 3 | Gemini 知識拡張 | 🔄 実装中 | gemini_expansion フィールド自動生成 |

---

## Gemini API の使用仕様

### モデル情報
- **モデル名**: `gemini-3-pro-preview`
- **出力形式**: JSON（`response_mime_type: "application/json"`）
- **使用フェーズ**: 
  - **video-scraper**: Mk2_Core_XX.json 生成（FACT/LOGIC/SOP/CASE タグ付きセンターピン）
  - **Phase 3**: gemini_expansion 生成（related_concepts / practical_applications / cautions）

### 環境変数
```bash
GEMINI_API_KEY=<実際の API キー>
GEMINI_MODEL_ID=gemini-3-pro-preview
リトライロジック
最大再試行回数: 3 回
初期待機時間: 1～2 秒
バックオフ戦略: 指数バックオフ（2^n）
API クォータ管理
初期実装：TOP 5 センターピンを対象（小さく試す戦略）
将来：バッチ処理や response_schema で複数レコードを 1 リクエストで処理
期待する Genspark の役割
市場・競合リサーチ

YouTube 運用代行・分析ツールの現況を調査
views.competitive に反映すべき追加項目を提案
仕様ブラッシュアップ

JSON_SPEC.md の改善案（命名・構造・拡張性）を提案
将来機能（Analytics 連携、教材化など）を検討
ドキュメント生成

外部向け説明資料（クライアント・金融機関向け）を生成
JSON スキーマのわかりやすい解説資料を作成
注意事項
機密情報の管理：
このリポジトリに API キー・本番コードは置かない

実装リポジトリ：
実装コードは video-scraper など別リポジトリで管理

仕様変更時：
JSON_SPEC.md と各 PHASE*.md を更新 コミットメッセージで変更意図を明記

環境構築：
.env.example を参考に、ローカルの .env に API キー設定 .env は .gitignore で除外済み