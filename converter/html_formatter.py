# converter/html_formatter.py

from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta


class HTMLFormatter:
    """JSON レポートを HTML に変換（テキスト版と同じ内容構造）"""

    # ハードコード定義
    LOOKBACK_DAYS = 7
    SUMMARY_LABEL = "要約"
    KEY_LECTURE_LABEL = "代表講座"
    NO_GROWTH_MESSAGE = "No lectures with significant weekly growth (>= +1.0%)."
    DETAIL_NOTE = "（詳細はHTML版レポート参照）"
    MAX_INSIGHT_LENGTH = 120
    SENTENCE_END_MARKER = "。"
    JST_TIMEZONE = timezone(timedelta(hours=9))

    @staticmethod
    def generate_html(data: Dict[str, Any], title: str = "Competitor Analytics") -> str:
        """
        JSON データを HTML レポートに変換

        Args:
            data: competitor_analytics JSON全データ
            title: レポートタイトル

        Returns:
            HTML 文字列
        """
        html_parts = []

        # portfolio_view から講座数を自動取得して Target を生成
        portfolio_view = data.get("portfolio_view", [])
        num_lectures = len(portfolio_view)
        channel_info = f"自社Webマーケ講座（全{num_lectures}講座セット）"

        # HTML ヘッダー
        html_parts.append(HTMLFormatter._generate_header(title))

        # CSS スタイル
        html_parts.append(HTMLFormatter._generate_css())

        # Body 開始
        html_parts.append("<body>")
        html_parts.append('<div class="container">')

        # ページヘッダーセクション（メタ情報）
        html_parts.append(HTMLFormatter._generate_page_header(data, channel_info))

        # Portfolio セクション
        if "portfolio_view" in data:
            html_parts.append(HTMLFormatter._generate_portfolio_section(data["portfolio_view"]))

        # Growth セクション
        if "growth_view" in data:
            html_parts.append(HTMLFormatter._generate_growth_section(data["growth_view"]))

        # Theme セクション
        if "theme_view" in data:
            html_parts.append(HTMLFormatter._generate_theme_section(data["theme_view"]))

        # フッターセクション
        html_parts.append(HTMLFormatter._generate_footer(data.get("generated_at", "")))

        # Body 終了
        html_parts.append("</div>")
        html_parts.append("</body>")
        html_parts.append("</html>")

        return "\n".join(html_parts)

    @staticmethod
    def _generate_header(title: str) -> str:
        """HTML ヘッダー生成"""
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>"""

    @staticmethod
    def _generate_css() -> str:
        """CSS スタイル生成"""
        return """    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', 'メイリオ', sans-serif;
            background-color: #f5f5f5;
            color: #333333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .page-header {{
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            color: #1a73e8;
        }}

        h2 {{
            font-size: 20px;
            font-weight: 600;
            margin-top: 30px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #1a73e8;
        }}

        h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #1a73e8;
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        p {{
            margin-bottom: 10px;
            font-size: 14px;
        }}

        .meta-info {{
            font-size: 13px;
            color: #666666;
            margin-bottom: 5px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        /* Portfolio Table */
        .portfolio-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}

        .portfolio-table thead {{
            background-color: #1a73e8;
            color: white;
        }}

        .portfolio-table thead th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
        }}

        .portfolio-table tbody td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 13px;
        }}

        .portfolio-table tbody tr:hover {{
            background-color: #e8f0fe;
        }}

        .text-right {{
            text-align: right;
        }}

        .text-center {{
            text-align: center;
        }}

        .metric-positive {{
            color: #34a853;
            font-weight: 600;
        }}

        .metric-negative {{
            color: #ea4335;
            font-weight: 600;
        }}

        /* Summary Section */
        .summary {{
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #1a73e8;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 14px;
        }}

        /* Growth Section */
        .growth-section {{
            background-color: #f9f9f9;
            padding: 20px;
            border-left: 4px solid #34a853;
            border-radius: 4px;
        }}

        .period {{
            font-size: 13px;
            color: #666666;
            margin-bottom: 15px;
        }}

        .growth-items {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .growth-item {{
            background-color: white;
            padding: 15px;
            border-left: 3px solid #34a853;
            border-radius: 4px;
        }}

        .growth-item h4 {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .growth-metric {{
            display: flex;
            gap: 15px;
            margin-bottom: 8px;
        }}

        .delta {{
            color: #34a853;
            font-weight: 600;
        }}

        .growth-rate {{
            color: #34a853;
            font-weight: 600;
        }}

        .engagement-delta {{
            font-size: 12px;
            color: #666666;
        }}

        .no-growth-message {{
            background-color: white;
            padding: 15px;
            border-left: 3px solid #999999;
            border-radius: 4px;
            color: #666666;
            font-style: italic;
        }}

        /* Theme Section */
        .theme-item {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}

        .courses {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .course {{
            background-color: white;
            padding: 15px;
            border-left: 3px solid #1a73e8;
            border-radius: 4px;
        }}

        .course h4 {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .course-metrics {{
            display: flex;
            gap: 15px;
            font-size: 13px;
            margin-bottom: 10px;
            color: #666666;
        }}

        .representative-pin {{
            background-color: #f9f9f9;
            font-size: 13px;
            padding: 10px;
            border-left: 3px solid #1a73e8;
            border-radius: 4px;
            margin-top: 10px;
            line-height: 1.5;
        }}

        .courses-overflow {{
            font-size: 12px;
            color: #999999;
            font-style: italic;
            margin-top: 10px;
        }}

        .footer {{
            border-top: 2px solid #e0e0e0;
            padding-top: 20px;
            margin-top: 40px;
            text-align: right;
        }}

        .footer p {{
            font-size: 12px;
            color: #999999;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}

            h1 {{
                font-size: 22px;
            }}

            h2 {{
                font-size: 18px;
            }}

            .portfolio-table {{
                font-size: 12px;
                overflow-x: auto;
            }}

            .portfolio-table thead th,
            .portfolio-table tbody td {{
                padding: 8px;
            }}

            .growth-metric {{
                flex-direction: column;
                gap: 5px;
            }}

            .course-metrics {{
                flex-direction: column;
                gap: 5px;
            }}
        }}
    </style>
</head>"""

    @staticmethod
    def _generate_page_header(data: Dict[str, Any], channel_info: str = "自社講座セット") -> str:
        """ページヘッダーセクション生成（メタ情報：Target, Period, Generated）"""
        generated_at_str = data.get("generated_at", "")
        generated_timestamp = HTMLFormatter._format_jst_timestamp(generated_at_str)

        # 期間情報を成長データから取得
        growth_view = data.get("growth_view", {})
        period_str = HTMLFormatter._format_period_html(growth_view.get("period", ""))

        return f"""
    <div class="page-header">
        <h1>📊 COMPETITOR ANALYTICS REPORT</h1>
        <p class="meta-info">Generated: {generated_timestamp}</p>
        <p class="meta-info">Target: {channel_info}</p>
        <p class="meta-info">{period_str}</p>
    </div>"""

    @staticmethod
    def _generate_portfolio_section(portfolio_view: List[Dict[str, Any]]) -> str:
        """Portfolio セクション生成（要約行付き）"""
        html_parts = [
            '<section class="section">',
            '<h2>📈 PORTFOLIO OVERVIEW</h2>'
        ]

        # 要約行を追加
        summary = HTMLFormatter._generate_portfolio_summary(portfolio_view)
        html_parts.append(f'<div class="summary"><strong>{HTMLFormatter.SUMMARY_LABEL}:</strong> {summary}</div>')

        # テーブル生成
        html_parts.append(HTMLFormatter._generate_portfolio_table(portfolio_view))

        html_parts.append('</section>')

        return "\n".join(html_parts)

    @staticmethod
    def _generate_portfolio_summary(portfolio_view: List[Dict[str, Any]]) -> str:
        """Portfolio の要約行を生成"""
        num_lectures = len(portfolio_view)
        total_views = sum(lecture.get("view_count", 0) for lecture in portfolio_view)
        avg_engagement = (
            sum(lecture.get("engagement_rate", 0) for lecture in portfolio_view) / num_lectures
            if num_lectures > 0
            else 0
        )

        total_views_formatted = HTMLFormatter._format_view_count(total_views)
        avg_engagement_pct = HTMLFormatter._format_engagement_rate(avg_engagement)

        return f"{num_lectures}講座 / 合計 {total_views_formatted} views / 平均エンゲージメント率 {avg_engagement_pct}"

    @staticmethod
    def _generate_portfolio_table(portfolio_view: List[Dict[str, Any]]) -> str:
        """Portfolio テーブル生成"""
        table_rows = [
            '<table class="portfolio-table">',
            '<thead>',
            '<tr>',
            '<th>Lecture ID</th>',
            '<th>Title</th>',
            '<th class="text-right">Views</th>',
            '<th class="text-right">Engagement Rate</th>',
            '<th>Funnel Stage</th>',
            '<th>Difficulty</th>',
            '<th class="text-center">Pins</th>',
            '</tr>',
            '</thead>',
            '<tbody>'
        ]

        for lecture in portfolio_view:
            lecture_id = lecture.get("lecture_id", "")
            title = lecture.get("title", "")
            title_short = HTMLFormatter._truncate_text(title, max_length=35)
            view_count = HTMLFormatter._format_view_count(lecture.get("view_count", 0))
            engagement_rate = HTMLFormatter._format_engagement_rate(lecture.get("engagement_rate", 0))
            funnel_stage = lecture.get("dominant_funnel_stage", "")
            difficulty = lecture.get("dominant_difficulty", "")
            pins = lecture.get("total_center_pins", 0)

            table_rows.append('<tr>')
            table_rows.append(f'<td>{lecture_id}</td>')
            table_rows.append(f'<td title="{title}">{title_short}</td>')
            table_rows.append(f'<td class="text-right">{view_count}</td>')
            table_rows.append(f'<td class="text-right metric-positive">{engagement_rate}</td>')
            table_rows.append(f'<td>{funnel_stage}</td>')
            table_rows.append(f'<td>{difficulty}</td>')
            table_rows.append(f'<td class="text-center">{pins}</td>')
            table_rows.append('</tr>')

        table_rows.append('</tbody>')
        table_rows.append('</table>')

        return "\n".join(table_rows)

    @staticmethod
    def _generate_growth_section(growth_view: Dict[str, Any]) -> str:
        """Growth セクション生成"""
        html_parts = [
            '<section class="section">',
            '<h2>📊 GROWTH HIGHLIGHTS</h2>'
        ]

        period = growth_view.get("period", "")
        period_formatted = HTMLFormatter._format_period_html(period)
        html_parts.append(f'<div class="growth-section">')
        html_parts.append(f'<div class="period">{period_formatted}</div>')
        html_parts.append('<div class="growth-items">')

        top_by_view_growth = growth_view.get("top_by_view_growth", [])

        # 成長なしの場合
        if not top_by_view_growth:
            html_parts.append(f'<div class="no-growth-message">{HTMLFormatter.NO_GROWTH_MESSAGE}</div>')
        else:
            # 成長講座を表示
            for course in top_by_view_growth:
                lecture_id = course.get("lecture_id", "")
                title = course.get("title", "")
                view_delta = HTMLFormatter._format_view_count(course.get("view_count_delta", 0))
                growth_rate = HTMLFormatter._format_engagement_rate(course.get("view_count_growth_rate", 0))
                engagement_delta = HTMLFormatter._format_engagement_rate(course.get("engagement_rate_delta", 0))

                html_parts.append('<div class="growth-item">')
                html_parts.append(f'<h4>Lecture {lecture_id}: {title}</h4>')
                html_parts.append('<div class="growth-metric">')
                html_parts.append(f'<span class="delta">+{view_delta} views</span>')
                html_parts.append(f'<span class="growth-rate">+{growth_rate}</span>')
                html_parts.append('</div>')
                html_parts.append(f'<div class="engagement-delta">Engagement: +{engagement_delta}</div>')
                html_parts.append('</div>')

        html_parts.append('</div>')
        html_parts.append('</div>')
        html_parts.append('</section>')

        return "\n".join(html_parts)

    @staticmethod
    def _generate_theme_section(theme_view: Dict[str, Any]) -> str:
        """Theme セクション生成（要約＋代表講座表示）"""
        html_parts = [
            '<section class="section">',
            '<h2>🎨 THEME ANALYSIS</h2>'
        ]

        for theme_name in theme_view.keys():
            theme_courses = theme_view[theme_name]

            if isinstance(theme_courses, list):
                courses = sorted(theme_courses, key=lambda x: x.get("view_count", 0), reverse=True)
            else:
                continue

            html_parts.append('<div class="theme-item">')
            html_parts.append(f'<h3>{theme_name}</h3>')

            # テーマの要約を生成
            theme_summary = HTMLFormatter._generate_theme_summary(theme_name, courses)
            html_parts.append(f'<p><strong>{HTMLFormatter.SUMMARY_LABEL}:</strong> {theme_summary}</p>')

            html_parts.append('<div class="courses">')

            # 上位3講座を表示
            for course in courses[:3]:
                lecture_id = course.get("lecture_id", "")
                view_count = HTMLFormatter._format_view_count(course.get("view_count", 0))
                engagement_rate = HTMLFormatter._format_engagement_rate(course.get("engagement_rate", 0))
                representative_pin = course.get("representative_pin", {})
                pin_content = representative_pin.get("content", "") if isinstance(representative_pin, dict) else ""

                html_parts.append('<div class="course">')
                html_parts.append(f'<h4>Lecture {lecture_id}</h4>')
                html_parts.append(f'<div class="course-metrics">')
                html_parts.append(f'<span>{view_count} views</span>')
                html_parts.append(f'<span class="metric-positive">{engagement_rate} engagement</span>')
                html_parts.append('</div>')

                if pin_content:
                    pin_short = HTMLFormatter._truncate_insight(pin_content)
                    html_parts.append(f'<blockquote class="representative-pin">{pin_short}</blockquote>')

                html_parts.append('</div>')

            # 超過分の表示
            if len(courses) > 3:
                overflow_count = len(courses) - 3
                html_parts.append(f'<div class="courses-overflow">他 {overflow_count} 講座あり</div>')

            # 代表講座を表示
            if courses:
                top_lecture_id = courses[0].get("lecture_id", "")
                html_parts.append(f'<p><strong>{HTMLFormatter.KEY_LECTURE_LABEL}:</strong> Lecture {top_lecture_id}</p>')

            html_parts.append('</div>')
            html_parts.append('</div>')

        html_parts.append('</section>')
        return "\n".join(html_parts)

    @staticmethod
    def _generate_theme_summary(theme_name: str, courses: List[Dict[str, Any]]) -> str:
        """テーマの要約行を生成"""
        if not courses:
            return f"{theme_name}テーマの講座群。"

        top_lecture = courses[0]
        top_lecture_id = top_lecture.get("lecture_id", "")
        top_view_count = top_lecture.get("view_count", 0)

        return f"{theme_name}テーマの講座が全体を牽引。特に Lecture {top_lecture_id} が中核（{HTMLFormatter._format_view_count(top_view_count)} views）。"

    @staticmethod
    def _generate_footer(generated_at: str) -> str:
        """フッターセクション生成（JST表記）"""
        last_updated_timestamp = HTMLFormatter._format_jst_timestamp(generated_at)
        return f"""
    <div class="footer">
        <p>Last Updated: {last_updated_timestamp}</p>
    </div>"""

    @staticmethod
    def _format_jst_timestamp(iso_timestamp: str) -> str:
        """ISO 8601 形式のタイムスタンプを JST 表記にフォーマット"""
        if not iso_timestamp:
            now_jst = datetime.now(HTMLFormatter.JST_TIMEZONE)
            return now_jst.strftime("%Y-%m-%d %H:%M:%S (JST)")

        try:
            if "+" in iso_timestamp or iso_timestamp.endswith("Z"):
                dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
                dt_jst = dt.astimezone(HTMLFormatter.JST_TIMEZONE)
            else:
                dt = datetime.fromisoformat(iso_timestamp)
                dt_jst = dt.replace(tzinfo=HTMLFormatter.JST_TIMEZONE)

            return dt_jst.strftime("%Y-%m-%d %H:%M:%S (JST)")

        except Exception as e:
            return iso_timestamp

    @staticmethod
    def _format_period_html(period_str: str) -> str:
        """期間表記を HTML 用にフォーマット"""
        if not period_str or "to" not in period_str:
            return f"Period: 直近{HTMLFormatter.LOOKBACK_DAYS}日間"

        try:
            parts = period_str.split(" to ")
            start_date = parts[0].strip()
            end_date = parts[1].strip()
            return f"Period: 直近{HTMLFormatter.LOOKBACK_DAYS}日間（{start_date}〜{end_date}）"
        except:
            return f"Period: 直近{HTMLFormatter.LOOKBACK_DAYS}日間"

    @staticmethod
    def _format_view_count(count: int) -> str:
        """ビュー数をカンマ区切りでフォーマット"""
        return "{:,}".format(int(count))

    @staticmethod
    def _format_engagement_rate(rate: float) -> str:
        """エンゲージメント率をパーセント表示でフォーマット"""
        return "{:.2f}%".format(float(rate) * 100)

    @staticmethod
    def _truncate_text(text: str, max_length: int = 130) -> str:
        """テキストを指定文字数で省略"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "…"

    @staticmethod
    def _truncate_insight(text: str) -> str:
        """representative insight を適切に切断"""
        max_len = HTMLFormatter.MAX_INSIGHT_LENGTH

        if len(text) <= max_len:
            result = text
        else:
            truncated = text[:max_len]
            sentence_idx = truncated.rfind(HTMLFormatter.SENTENCE_END_MARKER)

            if sentence_idx > 0:
                result = text[:sentence_idx + 1]
            else:
                result = truncated + "…"

        return result

