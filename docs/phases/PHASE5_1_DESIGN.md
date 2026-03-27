# Phase 5.1: Executive Summary (1枚レポート) 詳細設計書

## Overview
経営者が3分で意思決定できる「A4 1枚相当のレポート」を JSON データから自動生成する。
Phase 4.3 の詳細レポート（HTML/Text）をベースに、情報を圧縮・要約した形式。

## Status
**In Progress** (2026-03-27)

## Objectives
- ✅ A4 1枚（または Print時 1〜2ページ）のレポート構成を定義
- ✅ 簡易ルール駆動で「理由1行」を自動生成
- ✅ 手動記入型のアクション提案テンプレを用意
- ✅ HTML / Text の両形式で出力

## 採用構成（5ブロック案A）

### Block 1: ヘッダー
- タイトル：「📊 Competitor Analytics Report」
- 対象：動的生成（e.g., 「自社Webマーケ講座（全5講座セット）」）
- 期間：相対表記＋明示日付（e.g., 「直近7日間（2026-03-26〜2026-04-02）」）
- 生成日時：JST 形式「2026-03-26 22:36:53 (JST)」

### Block 2: 全体サマリ（3指標）
- **総ビュー数**：\{total_views:,}\ (カンマ区切り)
- **平均エンゲージメント率**：\{avg_engagement*100:.2f}%\
- **成長テーマ数**：weekly growth >= +1.0% のテーマ数

HTML：3カラムの数字強調ボックス（背景色 #f9f9f9, 左ボーダー #34a853）
Text：「• 指標名：値」形式の箇条書き

### Block 3: Top 3 講座
- ソート基準：\iew_count\ (降順)
- 表示フィールド：Lecture ID, Title (40文字), View Count, Engagement Rate, 理由1行

例：
\\\
1️⃣ Lecture 01: #01【独学で習得】初心者でも分かるweb...
   118,000 views / 1.61% engagement
   💡 基礎ニーズが継続的に強い。安定した人気講座
\\\

### Block 4: 重要テーマ ×3
- ソート基準：各テーマの最高ビュー講座の \iew_count\ (降順)
- 表示フィールド：Theme Name, 理由1行, 代表講座

例：
\\\
1🎯 Webマーケティング基礎
   💡 全体を牽引する最優先テーマ
   代表講座：Lecture 01
\\\

### Block 5: 今月のアクション提案 ×3（手動記入テンプレ）
- 3つの空スロット
- 各スロットに日本語で具体的なアクション文を記入

## 理由1行の自動生成ロジック

### 講座の理由生成
engagement_rate >= 2.0% → "視聴者の関心が高く、深く見られている質の高い講座"
view_count_growth_rate >= 2.0% → "直近で急成長中。テーマの関心度が急速に上昇"
view_count >= 100,000 → "基礎ニーズが継続的に強い。安定した人気講座"
その他 → "着実な成長を見せている講座"

### テーマの理由生成
rank == 1 → "全体を牽引する最優先テーマ"
top_course.engagement_rate >= 2.0% → "視聴者のニーズが高いテーマ"
top_course.view_count >= 80,000 → "ボリュームゾーン。継続強化推奨"
その他 → "成長ポテンシャルのあるテーマ"

## 実装ファイル

### converter/executive_summary_formatter.py
クラス：ExecutiveSummaryFormatter

主要メソッド：
- generate_executive_summary(data) → {'html': ..., 'text': ...}
- _generate_html() → HTML版
- _generate_text() → Text版
- _generate_top3_html() / _generate_top3_text() → Top 3 講座
- _get_top3_themes() → Top 3 テーマ取得
- _generate_themes_html() / _generate_themes_text() → テーマセクション
- _generate_lecture_reason() → 講座の理由
- _generate_theme_reason() → テーマの理由
- _format_jst_timestamp() → JST日時フォーマット
- _format_period() → 期間フォーマット

テンプレート定数：REASON_TEMPLATES

## 出力フォーマット

### HTML版
- ファイル名：reports/executive_summary/executive_summary_YYYYMMDD.html
- Responsive CSS、内部スタイルシート、Print-friendly（A4 1ページ）
- カラーパレット：#1a73e8, #34a853, #ea4335

### Text版
- ファイル名：reports/executive_summary/executive_summary_YYYYMMDD.txt
- 80文字セパレータ、Markdown 互換

## テスト項目
- HTML生成：DOCTYPE, h2, summary row, Top 3, Themes, Actions 確認
- Text生成：各セクションヘッダ、数字、理由、アクション枠 確認
- 理由ロジック確認（各条件分岐）
- JST 日時フォーマット統一
- Top 3 ソート正確性
- アクション提案テンプレ表示確認

## Timeline
- Design: 2026-03-27
- Implementation: 2026-03-27 (in progress)
- Testing: 2026-03-27
- Expected Completion: 2026-03-27

---
*Last Updated: 2026-03-27*
