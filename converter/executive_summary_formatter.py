"""
Phase 5.1: Executive Summary Formatter
経営者向け 1枚レポート（A4 相当）自動生成
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone


class ExecutiveSummaryFormatter:
    """Executive Summary (1ページレポ) を生成"""

    JST_TIMEZONE = timezone(timedelta(hours=9))

    # 理由生成用テンプレート
    REASON_TEMPLATES = {
        "high_growth": "直近で急成長中。テーマの関心度が急速に上昇",
        "high_engagement": "視聴者の関心が高く、深く見られている質の高い講座",
        "stable_popular": "基礎ニーズが継続的に強い。安定した人気講座",
        "steady_growth": "着実な成長を見せている講座",
        "leading_theme": "全体を牽引する最優先テーマ",
        "high_demand_theme": "視聴者のニーズが高いテーマ",
        "volume_zone_theme": "ボリュームゾーン。継続強化推奨",
        "growth_potential_theme": "成長ポテンシャルのあるテーマ",
    }

    @staticmethod
    def generate_executive_summary(data: Dict[str, Any]) -> Dict[str, str]:
        """Executive Summary を生成"""
        portfolio_view = data.get("portfolio_view", [])
        growth_view = data.get("growth_view", {})
        theme_view = data.get("theme_view", {})
        generated_at = data.get("generated_at", "")

        html_output = ExecutiveSummaryFormatter._generate_html(
            portfolio_view, growth_view, theme_view, generated_at
        )
        text_output = ExecutiveSummaryFormatter._generate_text(
            portfolio_view, growth_view, theme_view, generated_at
        )

        return {"html": html_output, "text": text_output}

    @staticmethod
    def _generate_html(
        portfolio_view: List[Dict],
        growth_view: Dict,
        theme_view: Dict,
        generated_at: str,
    ) -> str:
        """HTML版の1枚レポートを生成"""
        timestamp = ExecutiveSummaryFormatter._format_jst_timestamp(generated_at)
        period_str = ExecutiveSummaryFormatter._format_period(growth_view)
        num_lectures = len(portfolio_view)
        channel_info = f"自社Webマーケ講座（全{num_lectures}講座セット）"

        total_views = sum(l.get("view_count", 0) for l in portfolio_view)
        avg_engagement = (
            sum(l.get("engagement_rate", 0) for l in portfolio_view) / num_lectures
            if num_lectures > 0
            else 0
        )
        growth_count = len(
            [
                l
                for l in growth_view.get("top_by_view_growth", [])
                if l.get("view_count_growth_rate", 0) >= 0.01
            ]
        )

        top3_lectures = sorted(portfolio_view, key=lambda x: x.get("view_count", 0), reverse=True)[:3]
        top3_html = ExecutiveSummaryFormatter._generate_top3_html(top3_lectures)

        top3_themes = ExecutiveSummaryFormatter._get_top3_themes(theme_view)
        themes_html = ExecutiveSummaryFormatter._generate_themes_html(top3_themes)

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Summary</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', 'メイリオ', sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            line-height: 1.6;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 24px;
            color: #1a73e8;
            margin-bottom: 5px;
        }}
        .header p {{
            font-size: 12px;
            color: #666;
        }}
        .summary-row {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
            background: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #34a853;
        }}
        .summary-item {{
            text-align: center;
        }}
        .summary-item .value {{
            font-size: 20px;
            font-weight: bold;
            color: #1a73e8;
        }}
        .summary-item .label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            margin: 25px 0;
        }}
        .section h2 {{
            font-size: 16px;
            color: #1a73e8;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}
        .lecture-item {{
            background: #f9f9f9;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 3px solid #34a853;
        }}
        .lecture-item .title {{
            font-weight: bold;
            font-size: 13px;
        }}
        .lecture-item .metrics {{
            font-size: 12px;
            color: #666;
            margin: 5px 0;
        }}
        .lecture-item .reason {{
            font-size: 12px;
            color: #555;
            font-style: italic;
            margin-top: 5px;
        }}
        .theme-item {{
            background: #f9f9f9;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 3px solid #ea4335;
        }}
        .theme-item .name {{
            font-weight: bold;
            font-size: 13px;
        }}
        .theme-item .summary {{
            font-size: 12px;
            color: #666;
            margin: 3px 0;
        }}
        .theme-item .top-course {{
            font-size: 12px;
            color: #1a73e8;
            margin-top: 5px;
        }}
        .actions {{
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        .actions h3 {{
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
        }}
        .action-item {{
            margin: 8px 0;
            font-size: 12px;
        }}
        .action-placeholder {{
            background: white;
            border: 1px dashed #ccc;
            padding: 8px;
            border-radius: 4px;
        }}
        .footer {{
            text-align: center;
            font-size: 11px;
            color: #999;
            margin-top: 30px;
            border-top: 1px solid #e0e0e0;
            padding-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Competitor Analytics Report</h1>
            <p>{channel_info} / {period_str}</p>
            <p>Generated: {timestamp}</p>
        </div>

        <div class="section">
            <h2>全体サマリ</h2>
            <div class="summary-row">
                <div class="summary-item">
                    <div class="value">{total_views:,}</div>
                    <div class="label">総ビュー数</div>
                </div>
                <div class="summary-item">
                    <div class="value">{avg_engagement*100:.2f}%</div>
                    <div class="label">平均エンゲージメント率</div>
                </div>
                <div class="summary-item">
                    <div class="value">{growth_count}</div>
                    <div class="label">成長テーマ数</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🏆 Top 3 講座</h2>
            {top3_html}
        </div>

        <div class="section">
            <h2>🎯 重要テーマ ×3</h2>
            {themes_html}
        </div>

        <div class="actions">
            <h3>📌 今月のアクション提案</h3>
            <div class="action-item">
                1. <div class="action-placeholder">（例：Lecture 01 の応用編コンテンツ追加を検討）</div>
            </div>
            <div class="action-item">
                2. <div class="action-placeholder">（例：LPO系テーマの動画を月内に新規制作開始）</div>
            </div>
            <div class="action-item">
                3. <div class="action-placeholder">（例：Data分析講座の字幕・多言語対応を優先）</div>
            </div>
        </div>

        <div class="footer">
            <p>Last Updated: {timestamp}</p>
        </div>
    </div>
</body>
</html>"""

        return html

    @staticmethod
    def _generate_text(
        portfolio_view: List[Dict],
        growth_view: Dict,
        theme_view: Dict,
        generated_at: str,
    ) -> str:
        """テキスト版の1枚レポートを生成"""
        timestamp = ExecutiveSummaryFormatter._format_jst_timestamp(generated_at)
        period_str = ExecutiveSummaryFormatter._format_period(growth_view)
        num_lectures = len(portfolio_view)
        channel_info = f"自社Webマーケ講座（全{num_lectures}講座セット）"

        total_views = sum(l.get("view_count", 0) for l in portfolio_view)
        avg_engagement = (
            sum(l.get("engagement_rate", 0) for l in portfolio_view) / num_lectures
            if num_lectures > 0
            else 0
        )
        growth_count = len(
            [
                l
                for l in growth_view.get("top_by_view_growth", [])
                if l.get("view_count_growth_rate", 0) >= 0.01
            ]
        )

        top3_lectures = sorted(portfolio_view, key=lambda x: x.get("view_count", 0), reverse=True)[:3]
        top3_text = ExecutiveSummaryFormatter._generate_top3_text(top3_lectures)

        top3_themes = ExecutiveSummaryFormatter._get_top3_themes(theme_view)
        themes_text = ExecutiveSummaryFormatter._generate_themes_text(top3_themes)

        separator = "=" * 80

        text = f"""{separator}
📊 Competitor Analytics Report
{channel_info} / {period_str}
Generated: {timestamp}
{separator}

【全体サマリ】
  • 総ビュー数：{total_views:,} views
  • 平均エンゲージメント率：{avg_engagement*100:.2f}%
  • 成長テーマ数：{growth_count}テーマ

【Top 3 講座】
{top3_text}

【重要テーマ ×3】
{themes_text}

【今月のアクション提案】
  1. ____________________
     （例：Lecture 01 の応用編コンテンツ追加を検討）

  2. ____________________
     （例：LPO系テーマの動画を月内に新規制作開始）

  3. ____________________
     （例：Data分析講座の字幕・多言語対応を優先）

{separator}
Last Updated: {timestamp}
{separator}"""

        return text

    @staticmethod
    def _generate_top3_html(lectures: List[Dict]) -> str:
        """Top 3 講座の HTML を生成"""
        html = ""
        for rank, lecture in enumerate(lectures, 1):
            lecture_id = lecture.get("lecture_id", "N/A")
            title = lecture.get("title", "N/A")[:40]
            view_count = lecture.get("view_count", 0)
            engagement = lecture.get("engagement_rate", 0)
            reason = ExecutiveSummaryFormatter._generate_lecture_reason(lecture)

            html += f"""<div class="lecture-item">
    <div class="title">{rank}️⃣ Lecture {lecture_id}: {title}</div>
    <div class="metrics">{view_count:,} views / {engagement*100:.2f}% engagement</div>
    <div class="reason">💡 {reason}</div>
</div>
"""
        return html

    @staticmethod
    def _generate_top3_text(lectures: List[Dict]) -> str:
        """Top 3 講座のテキストを生成"""
        text = ""
        for rank, lecture in enumerate(lectures, 1):
            lecture_id = lecture.get("lecture_id", "N/A")
            title = lecture.get("title", "N/A")[:40]
            view_count = lecture.get("view_count", 0)
            engagement = lecture.get("engagement_rate", 0)
            reason = ExecutiveSummaryFormatter._generate_lecture_reason(lecture)

            text += f"""  {rank}️⃣ Lecture {lecture_id}: {title}
     {view_count:,} views ({engagement*100:.2f}% engagement)
     💡 {reason}

"""
        return text

    @staticmethod
    def _get_top3_themes(theme_view: Dict) -> List[Dict]:
        """トップ3テーマを取得 - theme_data は直接リスト"""
        theme_list = []

        for theme_name, theme_data in theme_view.items():
            # theme_data は直接リスト（Array）
            if isinstance(theme_data, list) and len(theme_data) > 0:
                courses = theme_data
                top_course = max(courses, key=lambda c: c.get("view_count", 0))
                theme_list.append({
                    "name": theme_name,
                    "courses": courses,
                    "top_course": top_course,
                })

        # ビュー数でソートしてトップ3を取得
        top3 = sorted(
            theme_list,
            key=lambda t: t["top_course"].get("view_count", 0),
            reverse=True,
        )[:3]

        return top3

    @staticmethod
    def _generate_themes_html(themes: List[Dict]) -> str:
        """テーマのHTMLを生成"""
        if not themes:
            return "<p>テーマデータなし</p>"
        
        html = ""
        for rank, theme in enumerate(themes, 1):
            theme_name = theme["name"]
            top_course = theme["top_course"]
            reason = ExecutiveSummaryFormatter._generate_theme_reason(theme, rank)
            top_course_id = top_course.get("lecture_id", "N/A")

            html += f"""<div class="theme-item">
    <div class="name">{rank}🎯 {theme_name}</div>
    <div class="summary">💡 {reason}</div>
    <div class="top-course">代表講座：Lecture {top_course_id}</div>
</div>
"""
        return html

    @staticmethod
    def _generate_themes_text(themes: List[Dict]) -> str:
        """テーマのテキストを生成"""
        if not themes:
            return "  テーマデータなし\n"
        
        text = ""
        for rank, theme in enumerate(themes, 1):
            theme_name = theme["name"]
            top_course = theme["top_course"]
            reason = ExecutiveSummaryFormatter._generate_theme_reason(theme, rank)
            top_course_id = top_course.get("lecture_id", "N/A")

            text += f"""  {rank}🎯 {theme_name}
     💡 {reason}
     代表講座：Lecture {top_course_id}

"""
        return text

    @staticmethod
    def _generate_lecture_reason(lecture: Dict[str, Any]) -> str:
        """講座の理由を生成（簡易ルール駆動）"""
        engagement = lecture.get("engagement_rate", 0)
        view_count = lecture.get("view_count", 0)
        growth_rate = lecture.get("view_count_growth_rate", 0)

        if growth_rate >= 0.02:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["high_growth"]
        elif engagement >= 0.02:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["high_engagement"]
        elif view_count >= 100000:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["stable_popular"]
        else:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["steady_growth"]

    @staticmethod
    def _generate_theme_reason(theme: Dict[str, Any], rank: int) -> str:
        """テーマの理由を生成（簡易ルール駆動）"""
        top_course = theme["top_course"]
        engagement = top_course.get("engagement_rate", 0)
        view_count = top_course.get("view_count", 0)

        if rank == 1:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["leading_theme"]
        elif engagement >= 0.02:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["high_demand_theme"]
        elif view_count >= 80000:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["volume_zone_theme"]
        else:
            return ExecutiveSummaryFormatter.REASON_TEMPLATES["growth_potential_theme"]

    @staticmethod
    def _format_jst_timestamp(dt_str: str) -> str:
        """JST タイムスタンプをフォーマット"""
        if not dt_str:
            return datetime.now(ExecutiveSummaryFormatter.JST_TIMEZONE).strftime(
                "%Y-%m-%d %H:%M:%S (JST)"
            )

        try:
            if "T" in dt_str:
                if "+" in dt_str or dt_str.endswith("Z"):
                    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                else:
                    dt = datetime.fromisoformat(dt_str)
                    dt = dt.replace(tzinfo=ExecutiveSummaryFormatter.JST_TIMEZONE)
            else:
                return dt_str

            dt_jst = dt.astimezone(ExecutiveSummaryFormatter.JST_TIMEZONE)
            return dt_jst.strftime("%Y-%m-%d %H:%M:%S (JST)")
        except:
            return dt_str

    @staticmethod
    def _format_period(growth_view: Dict[str, Any]) -> str:
        """期間をフォーマット"""
        period = growth_view.get("period", "")
        if not period:
            return "直近7日間"

        try:
            parts = period.split(" to ")
            if len(parts) == 2:
                return f"直近7日間（{parts[0]}〜{parts[1]}）"
        except:
            pass

        return period
