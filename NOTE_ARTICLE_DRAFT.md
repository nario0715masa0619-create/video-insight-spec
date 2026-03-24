# YouTube 動画から「実行可能な知恵」を自動抽出する仕組み

## はじめに

このプロジェクト「video-insight-spec」は、YouTube 動画の内容を JSON と SQLite で体系的に蓄積し、分析可能にする仕組みです。

単なる「動画メタデータの取得」ではなく、**動画から「事実」「論理」「手順」といった知識を抽出し、それを数値化・比較可能にする**ことが特徴です。

## 何ができるのか

### 1. 動画の「中身」を自動認識

- 字幕・テロップ・スクリーンショットの抽出：OCR で画面上の情報を取得
- 知識の構造化：「事実（FACT）」「論理（LOGIC）」「手順（SOP）」に分類
- 品質スコア化：各セグメントの情報密度を 0～100 で数値化

### 2. YouTube メトリクスと統合

- 再生数・高評価・コメント数を自動取得
- エンゲージメント率 = (高評価 + コメント×2) / 再生数
- ジャンル相場比較：1000 回再生あたりの反応数で正規化

### 3. 競合・周辺動画の「相対的な価値」を判定

- 表面的な再生数だけでなく、「中身の濃さ」と「反応」の両面から評価
- 「高再生でも内容が薄い」「低再生でも実用性が高い」といった動画を自動検出
- ROI 予測スコア：この動画が売上に結びつく可能性を推定

## 実装の流れ

### Phase 1: 基本構造（完了）
- JSON スキーマ設計
- SQLite サイドカー DB 構造設計
- 動画スクレイピング → JSON 変換の自動化

### Phase 2.0 ～ 2.1: テスト・品質保証（完了）
- マスターデータの統合
- 自動テスト基盤（pytest 62 テスト全 PASS）

### Phase 2.2: YouTube API 統合（完了）
- YouTube Data API v3 で全動画のメトリクス自動取得
- engagement_rate、likes_per_1000_views、comments_per_1000_views 計算

### Phase 2.2.2: OCR テキストクリーニング（完了）
- UI ノイズ（メニュー、日時、ウィンドウ枠など）を自動除去
- 日本語 OCR 誤認識を正規表現で補正（例：「アブリ」→「アプリ」）
- 平均 26.38% のテキスト削減で高精度化を実現

### Phase 2.2.3: YouTube Video ID Enricher（完了）
- 動画タイトルから YouTube の video_id を自動検索・補充
- insight_spec_XX.json に統合、メタデータの完全性を確保

### Phase 3（設計中）
- Gemini API で knowledge_points を自動拡張予定

## 技術スタック

- 言語：Python 3.13.12
- データベース：SQLite（サイドカー DB）
- API：YouTube Data API v3
- テスト：pytest（62 テスト）
- バージョン管理：Git / GitHub

## 使用例

### JSON 出力（insight_spec_01.json）

video_id: b8u2CQLQBVU
title: 【超重要！】コンテンツ販売必須の基礎知識

center_pins:
- BRAIN_CENTERPIN_001 (FACT, purity: 90.0)
- BRAIN_CENTERPIN_002 (LOGIC, purity: 85.0)

metrics:
- engagement_rate: 2.32%
- likes_per_1000_views: 23.04
- comments_per_1000_views: 0.10
- knowledge_density_per_minute: 11.63
- actionability_score: 95.0

## なぜこれが必要か

YouTube を「コンテンツ販売の営業ツール」として捉えると：

1. どの動画が稼ぎに結びつくかが見えない
2. 何が視聴者に刺さるのかが曖昧
3. 競合との差別化ポイントが不明確

このシステムにより：

✅ 動画ごとの「実質的な価値」を数値化
✅ 視聴者の反応パターンを可視化
✅ 今後の動画企画の意思決定をデータドリブン化

## まとめ

「video-insight-spec」は、単なる YouTube メタデータ取得ツールではなく、動画の「中身」と「反応」を統合分析し、ビジネス成果に直結させるための基盤です。

現在、Phase 2.2 系が完成し、本番環境（main ブランチ）に乗った状態です。

次の Phase 3（Gemini API 統合）では、さらに高度な知識抽出・分析が可能になります。

プロジェクト URL：https://github.com/nario0715masa0619-create/video-insight-spec
