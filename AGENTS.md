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
2. **Phase 1** → insight_spec_XX.json（基本形）
3. **Phase 2.2** → YouTube メトリクス追加
4. **Phase 2.2.1** → エンゲージメント指標計算
5. **Phase 2.2.2** → OCR テキストクリーニング
6. **Phase 2.2.3** → Video ID 補充
7. **Phase 3 準備** → 出現回数・重要度スコア
8. **Phase 3** → Gemini で gemini_expansion 生成

**最終出力**：insight_spec_XX.json（完全版）
完了状況
✅ Phase 1, 2.0～2.1, 2.2, 2.2.1, 2.2.2, 2.2.3, 3 準備
🔄 Phase 3（実装中）

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


