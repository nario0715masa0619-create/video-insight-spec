# Phase 4.3: HTML/Text Formatter 詳細実装設計書

## 概要
JSON レポート（portfolio_view, growth_view, theme_view）を HTML と テキスト形式に変換。

---

## 1. html_formatter.py 詳細設計

### クラス: HTMLFormatter

#### メソッド 1: generate_html()
入力: data (JSON全データ), title (レポートタイトル)
出力: HTML 文字列

処理フロー:
1. HTML ヘッダー（<!DOCTYPE html>）生成
2. CSS スタイル埋め込み（内部スタイルシート）
3. Body セクション生成
   - ヘッダーセクション
   - portfolio_view テーブル
   - growth_view ハイライト
   - theme_view セクション
4. フッターセクション
5. HTML 閉じタグ

#### メソッド 2: _generate_css()
出力: CSS 文字列（内部スタイル）

含まれるスタイル:
- body, .container
- .header, .section, .footer
- .portfolio-table, table, thead, tbody, tr, td
- .growth-highlight, .theme-section
- .metric-positive, .metric-negative
- @media (max-width: 768px) - レスポンシブ

#### メソッド 3: _generate_portfolio_table()
入力: portfolio_view リスト（5講座）
出力: HTML テーブル文字列

テーブル列:
- Lecture ID
- Title (30~40文字で省略, title属性にフル表示)
- Views (カンマ区切り)
- Engagement Rate (パーセント表示)
- Funnel Stage
- Difficulty
- Pins

ロジック:
- title は CSS ellipsis 適用
- view_count はカンマ区切り（例：118,000）
- engagement_rate はパーセント表示（例：1.61%）
- 数値は text-right クラスで右寄せ
- ホバーエフェクト: 行背景色 #e8f0fe

#### メソッド 4: _generate_growth_section()
入力: growth_view データ
出力: HTML セクション文字列

セクション構成:
- タイトル: 📈 Growth Highlights
- Period 表示
- top_by_view_growth を反復処理
- 各講座: Lecture ID + Title + Delta views + Growth rate + Engagement delta

ロジック:
- view_count_delta はカンマ区切り
- view_count_growth_rate は metric-positive クラス適用（色：#34a853）

#### メソッド 5: _generate_theme_section()
入力: theme_view データ（8テーマ）
出力: HTML セクション文字列

セクション構成（テーマごと）:
- テーマ名を見出し（h3）
- 各テーマの courses を view_count 降順ソート
- 上位3講座を表示
  - Lecture ID + Title
  - View count + Engagement rate
  - representative_pin (100~140文字で省略, <blockquote>で表示)
- 超過分: 「他 X 講座あり」テキスト

representative_pin フォーマット:
- <blockquote> タグで囲む
- フォントサイズ: 13px
- 背景色: #f9f9f9
- パディング: 10px
- ボーダー左: 3px solid #1a73e8

#### メソッド 6: _format_view_count()
入力: 数値（例：118000）
出力: カンマ区切り文字列（例："118,000"）

#### メソッド 7: _format_engagement_rate()
入力: 小数（例：0.0161）
出力: パーセント文字列（例："1.61%"）

#### メソッド 8: _truncate_text()
入力: テキスト, 最大文字数（デフォルト：130）
出力: 省略されたテキスト（末尾に「…」）

---

## 2. text_formatter.py 詳細設計

### クラス: TextFormatter

#### メソッド 1: generate_text()
入力: data (全データ), title (レポートタイトル)
出力: テキスト文字列

処理フロー:
1. ヘッダー（タイトル、生成日時）
2. portfolio_view セクション
3. growth_view セクション
4. theme_view セクション
5. フッター

#### メソッド 2: _generate_portfolio_section()
出力: ポートフォリオセクション（見出し + リスト）

フォーマット:
📈 PORTFOLIO OVERVIEW
─────────────────────────────────────────

Lecture 01: #01【独学で習得】初心者でも分かるwebマーケティング講座
  Views: 118,000 | Engagement: 1.61% | Stage: 認知 | Difficulty: beginner | Pins: 9

#### メソッド 3: _generate_growth_section()
出力: 成長セクション

フォーマット:
📊 GROWTH HIGHLIGHTS
─────────────────────────────────────────

Period: 2026-03-26 to 2026-04-02

• Lecture 01: #01【独学で習得】初心者でも分かるwebマーケティング講座
  +2,166 views (+1.87%)
  Engagement: +0.01%

#### メソッド 4: _generate_theme_section()
出力: テーマセクション（各テーマごと）

フォーマット:
🎨 THEME ANALYSIS
─────────────────────────────────────────

■ マーケティング
  • Lecture 01: 118,000 views (1.61% engagement)
    └ Representative insight: Webサイトの制作を...
  • Lecture 03: 26,024 views (1.72% engagement)
    └ Representative insight: ...
  (他 3 講座あり)

■ Webマーケティング
  ...

#### ヘルパーメソッド
_get_current_timestamp() -> ISO 8601 フォーマット
_format_view_count(count: int) -> str
_format_engagement_rate(rate: float) -> str
_truncate_text(text: str, max_length: int = 140) -> str
_draw_separator(char: str = "─", width: int = 80) -> str

---

## 3. report_generator.py 詳細設計

### クラス: ReportGenerator

#### メソッド 1: generate()
入力: json_file_path (入力JSON), output_dir (出力ディレクトリ="reports")
出力: Dict { "html": パス, "text": パス }

処理フロー:
1. JSON ファイル読み込み
2. 出力ディレクトリ作成（html/, text/）
3. HTMLFormatter.generate_html() 呼び出し
4. TextFormatter.generate_text() 呼び出し
5. ファイル出力（タイムスタンプ付き）
6. 結果返却

#### メソッド 2: _load_json()
入力: json_file_path
出力: Dict (JSON全データ)

例外処理: ファイル不在時は ValueError

#### メソッド 3: _ensure_directories()
入力: output_dir
出力: Dict { "html_dir": Path, "text_dir": Path }

処理: 存在しないディレクトリは作成

#### メソッド 4: _get_output_filename()
入力: prefix (デフォルト="competitor_analytics")
出力: タイムスタンプ付きファイル名

例: competitor_analytics_20260326.html

#### メソッド 5: _save_file()
入力: content (ファイル内容), file_path (保存先パス)
出力: Path (保存したファイルパス)

処理: UTF-8 で保存, 親ディレクトリを作成

---

## 4. competitor_analytics_generator.py 修正設計

修正内容:
- HTMLFormatter, TextFormatter, ReportGenerator をインポート
- JSON 生成後に ReportGenerator.generate() を呼び出し
- HTML/Text ファイルパスをログ出力

修正箇所:
if __name__ == "__main__":
    # JSON 生成
    json_data = generate_json(...)
    json_file = save_json(json_data)
    
    # HTML/Text レポート生成
    print("📄 Generating HTML/Text reports...")
    report_paths = ReportGenerator.generate(json_file)
    
    print(f"✅ HTML Report: {report_paths['html']}")
    print(f"✅ Text Report: {report_paths['text']}")

---

## 5. 出力ファイル構成

reports/
├── competitor_analytics/
│   └── competitor_analytics_20260326.json
├── html/
│   └── competitor_analytics_20260326.html
└── text/
    └── competitor_analytics_20260326.txt

---

## 6. テストケース

### テスト 1: HTML 生成
確認項目:
- "<!DOCTYPE html>" が含まれている
- "<table" が含まれている
- "Lecture 01" が含まれている
- "118,000" カンマ区切りが正しい
- "1.61%" パーセント表示が正しい
- "Growth Highlights" セクションが存在
- Theme セクションが 8 個存在

### テスト 2: Text 生成
確認項目:
- "COMPETITOR ANALYTICS REPORT" が含まれている
- "PORTFOLIO OVERVIEW" が含まれている
- "GROWTH HIGHLIGHTS" が含まれている
- "THEME ANALYSIS" が含まれている
- 日時フォーマットが ISO 8601

### テスト 3: ファイル出力
確認項目:
- HTML ファイルが reports/html に存在
- Text ファイルが reports/text に存在
- ファイルサイズ > 0

---

## 7. 実装チェックリスト

html_formatter.py:
- [ ] HTMLFormatter クラス
- [ ] generate_html() メソッド
- [ ] _generate_css() メソッド
- [ ] _generate_portfolio_table() メソッド
- [ ] _generate_growth_section() メソッド
- [ ] _generate_theme_section() メソッド
- [ ] _format_view_count() メソッド
- [ ] _format_engagement_rate() メソッド
- [ ] _truncate_text() メソッド

text_formatter.py:
- [ ] TextFormatter クラス
- [ ] generate_text() メソッド
- [ ] _generate_portfolio_section() メソッド
- [ ] _generate_growth_section() メソッド
- [ ] _generate_theme_section() メソッド
- [ ] _get_current_timestamp() メソッド
- [ ] _truncate_text() メソッド

report_generator.py:
- [ ] ReportGenerator クラス
- [ ] generate() メソッド
- [ ] _load_json() メソッド
- [ ] _ensure_directories() メソッド
- [ ] _get_output_filename() メソッド
- [ ] _save_file() メソッド

competitor_analytics_generator.py:
- [ ] ReportGenerator インポート
- [ ] generate() 呼び出し
- [ ] ログ出力

テスト:
- [ ] HTML 生成テスト
- [ ] Text 生成テスト
- [ ] ファイル出力テスト

---

## 8. 実装時間予定

html_formatter.py: 40 分
text_formatter.py: 30 分
report_generator.py: 30 分
テスト+デバッグ: 20 分

合計: 約 2 時間

---

## 9. 注意事項

- 全ファイル UTF-8 エンコーディング
- ISO 8601 フォーマット: 2026-03-26T22:36:53+09:00
- theme_view は8つのテーマキーを処理（順序は保持）
- representative_pin が存在しない場合はスキップ
- CSS は内部スタイルシート（<style>タグ内）で埋め込み
- HTML は class 属性で responsive 対応（@media クエリ）
