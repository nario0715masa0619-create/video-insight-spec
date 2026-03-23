# AGENTS.md

## 目的
このドキュメントは、Genspark などの AI エージェントが `video-insight-spec` リポジトリを活用・拡張する際の指南書です。

`video-insight-spec` は、主に以下の責務を持つリポジトリです：
1. **JSON スキーマ・DB 設計** の仕様化と管理
2. **実装ガイドライン** (`PHASE*.md`) の提供
3. **ドキュメント生成・更新** による設計の最新化

> 💡 **実装コード自体は別リポジトリで管理されていますが、このリポジトリの仕様に基づいて開発が進められます。**

## AI エージェントに期待する役割
# AGENTS.md （Genspark用メモ）

## このリポジトリについて
- リポジトリ名：`video-insight-spec`
- 目的：  
  - 動画スクレイピングで取得したテキストから「実行可能な知恵」を抽出し、  
    1本1JSONで保存するための **仕様書（スキーマ定義）** をまとめる。
- 実装コードや機密情報は置かない。  
  - ここにあるのは **設計レベルの情報だけ**。

## 重要ファイル
- `JSON_SPEC.md`  
  - JSONの構造と各フィールドの意味を定義しているメイン仕様書。  
  - 3レイヤー構成：
    - `video_meta`：動画の汎用メタ情報  
    - `knowledge_core`：Brain_Marketing_Master.json 準拠の知識レイヤー  
    - `views`：用途別ビュー（competitive / self_improvement / education など）



## Phase 2.2: YouTube API 統合（実装完了）
- **YouTube Data API v3** から view_count, like_count, comment_count を自動取得
- 21講座全体の動画メタデータを自動収集
- insight_spec_XX.json の iews.competitive.youtube_metrics に統合

## Phase 2.2.1: エンゲージメント指標の計算（実装完了）
- **Engagement Metrics** の追加実装：
  - engagement_rate: (likes + comments * 2) / view_count
  - likes_per_1000_views: likes / view_count * 1000
  - comments_per_1000_views: comments / view_count * 1000
- ゼロ除算を安全に回避し、すべての動画に対応
- 全テスト 50/50 PASS



## ロードマップ方針の変更
**Phase 2.3 (Brain 販売数 API 統合) をスコープ外へ**
- 理由：本来のプロダクト目的（YouTube運用に悩む企業向けに「何を真似すべきか」を可視化）から外れている
- Brain 販売データは想定ユーザーにとって直接的な価値にならない
- 今後は、あらゆるジャンルのチャンネルに汎用的に効く「コア機能」に集中

## 次フェーズ：Phase 3 へ集中
**Phase 3: Gemini API による knowledge_points の自動拡張**
- 目的：center_pins から、より詳細な「実装可能な知識」を自動抽出
- 対象：すべての業界・ジャンルに応用可能な汎用機能
- 難易度：★★★★☆ / 所要時間：3～4h

## 期待するGensparkの役割
1. 市場・競合リサーチ  
   - YouTube運用代行／分析ツールがどんなレポート項目・指標を扱っているかを調査し、  
     `views.competitive` に反映すべき追加項目や説明文を提案する。
2. 仕様ブラッシュアップ  
   - `JSON_SPEC.md` を読んだ上で、  
     - 命名の改善案  
     - フィールドの分割・統合案  
     - 将来拡張（自社Analytics連携・教材化など）を見据えた構造案  
     を提案する。
3. ドキュメント生成  
   - 外部向け説明資料（例：クライアント向け概要資料、金融機関向け資料）用に、  
     JSON仕様のわかりやすい解説ドキュメントを生成する。

## 注意事項
- このリポジトリは **仕様書専用**。  
  - 実際のAPIキー・環境変数・本番コードは別リポジトリで管理する。  
- 仕様変更を行う場合は、`JSON_SPEC.md` を更新し、変更点をコメントかコミットメッセージで明記する。
