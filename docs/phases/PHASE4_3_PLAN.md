# Phase 4.3: HTML/Text Formatter & Report Generation

## Status
**Completed** ✅ (2026-03-27)

## Overview
Convert JSON analytics reports (portfolio_view, growth_view, theme_view) into HTML and text formats for executive consumption. Provides both machine-readable and human-friendly outputs with consistent data and styling.

## Objectives
- ✅ Convert JSON reports to professional HTML format with responsive design
- ✅ Generate executive-friendly text summaries
- ✅ Unify content across HTML and text outputs
- ✅ Implement dynamic Target generation based on portfolio data
- ✅ Standardize timestamps to JST (Japan Standard Time)

## Outputs

### HTML Report Format
**File**: eports/html/competitor_analytics_YYYYMMDD.html

**Structure**:
- DOCTYPE & semantic HTML5 structure
- Meta information header:
  - Title: "Competitor Analytics"
  - Generated timestamp (JST): "2026-03-26 22:36:53 (JST)"
  - **Target**: Dynamically generated from portfolio_view count (e.g., "自社Webマーケ講座（全5講座セット）")
  - **Period**: Relative + explicit dates (e.g., "直近7日間（2026-03-26〜2026-04-02）")
  - **Last Updated**: Same as Generated timestamp (JST)
- Responsive CSS (embedded):
  - Light theme: bg #f5f5f5, header #1a73e8, growth #34a853, negative #ea4335
  - Font stack: 'Segoe UI', 'メイリオ', sans-serif
  - Max-width 1200px, mobile-friendly (horizontal scroll <768px)
- **Portfolio Overview** section:
  - Summary line: "要約: X講座 / 合計 YYY,ZZZ views / 平均エンゲージメント率 Z.ZZ%"
  - Table with columns: Lecture ID, Title, Views, Engagement Rate, Funnel Stage, Difficulty, Pins
  - Title truncation (30-40 chars) with full title in title attribute
- **Growth Highlights** section:
  - Period display (relative + explicit dates)
  - Top courses with growth metrics
  - "No growth" message when applicable
- **Theme Analysis** section:
  - Per-theme subsections with:
    - **要約**: One-line theme summary (e.g., "LPO系講座が全体を牽引")
    - Top 3 courses by view count with engagement metrics
    - **Representative insight**: Truncated to single sentence (~100-140 chars)
    - **代表講座**: Top course indicator (e.g., "代表講座: Lecture 01")

### Text Summary Format
**File**: eports/text/competitor_analytics_YYYYMMDD.txt

**Structure**:
- Header section (80-char separator):
  - Title: "📊 Competitor Analytics"
  - Generated timestamp (JST): "Generated: 2026-03-26 22:36:53 (JST)"
  - **Target**: Dynamically generated (e.g., "Target: 自社Webマーケ講座（全5講座セット）")
  - **Period**: Relative + explicit dates (e.g., "Period: 直近7日間（2026-03-26〜2026-04-02）")
  - **Last Updated**: Same as Generated (JST)
- **Portfolio Overview** section:
  - Summary line: "要約: 5講座 / 合計 246,629 views / 平均エンゲージメント率 1.71%"
  - Lecture list with views and engagement
- **Growth Highlights** section:
  - Period display
  - Top growth courses (only if growth >= +1.0%)
  - "No lectures with significant weekly growth (>= +1.0%)." when applicable
- **Theme Analysis** section:
  - Per-theme headings with:
    - **要約**: Theme summary
    - Top 3 courses by view count
    - **Representative insight**: Truncated text with optional detail note
    - **代表講座**: Top course in theme
- Footer: 80-char separator + Last Updated timestamp

## Implementation Details

### New Files Created
1. **converter/html_formatter.py**
   - HTMLFormatter class with static methods
   - generate_html(data, title) → HTML string
   - Helper methods: _generate_css(), _generate_page_header(), _generate_portfolio_table(), _generate_growth_section(), _generate_theme_section(), etc.
   - Utilities: _format_view_count(), _format_engagement_rate(), _truncate_insight(), _format_jst_timestamp()

2. **converter/text_formatter.py**
   - TextFormatter class with static methods
   - generate_text(data, title, include_detail_note) → text string
   - Dynamic channel_info generation from portfolio_view count
   - Helper methods: _generate_header(), _generate_portfolio_section(), _generate_growth_section(), _generate_theme_section(), _generate_footer()
   - Utilities: _format_jst_timestamp(), _format_period(), _format_view_count(), _format_engagement_rate(), _truncate_insight(), _draw_separator()

3. **converter/report_generator.py**
   - ReportGenerator class with generate(json_file_path, output_dir) method
   - Loads JSON, ensures output directories (eports/html/, eports/text/)
   - Calls both formatters, saves timestamped files
   - Returns dict with {'html': filepath, 'text': filepath}

### Modified Files
1. **competitor_analytics_generator.py**
   - Added import: rom converter.report_generator import ReportGenerator
   - After JSON generation, calls ReportGenerator.generate(output_file, output_dir="reports")
   - Logs HTML and text output file paths

2. **README.md**
   - Updated CLI examples to show HTML/text report generation

## Test Results
✅ HTML generation: DOCTYPE, headings, tables, CSS, meta info, Target, Period, Last Updated all present
✅ Text generation: sections, summary lines, timestamps (JST), content match with HTML
✅ Target dynamic generation: portfolio_view lecture count correctly reflected
✅ Period formatting: relative + explicit dates in both HTML and text
✅ Timestamp formatting: unified JST format "YYYY-MM-DD HH:MM:SS (JST)"
✅ Representative insight: truncated to single sentence, properly formatted
✅ Theme summaries: generated and displayed correctly
✅ Representative lecture: identified and displayed

## Sample Output Files
- eports/competitor_analytics/competitor_analytics_20260326.json (input)
- eports/html/competitor_analytics_20260327.html (output)
- eports/text/competitor_analytics_20260327.txt (output)

## Timeline
- **Design**: 2026-03-26 to 2026-03-26
- **Implementation**: 2026-03-26 to 2026-03-27
- **Testing & Refinement**: 2026-03-27
- **Completion**: 2026-03-27 ✅

## Next Phase
**Phase 5: Advanced Analytics** – cohort analysis, engagement predictions, trend forecasting

---
*Last Updated: 2026-03-27*
