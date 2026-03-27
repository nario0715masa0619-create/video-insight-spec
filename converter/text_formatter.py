import json
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

class TextFormatter:
    """JSON レポートをテキスト形式に変換（経営者向け読みやすさ重視）"""

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
    def generate_text(
        data: Dict[str, Any],
        title: str = "Competitor Analytics",
        include_detail_note: bool = True
    ) -> str:
        """JSON データをテキストレポートに変換"""
        
        # portfolio_view から講座数を自動取得し、Target を動的生成
        portfolio_view = data.get("portfolio_view", [])
        num_lectures = len(portfolio_view)
        channel_info = f"自社Webマーケ講座（全{num_lectures}講座セット）"
        
        text_parts = []
        text_parts.append(TextFormatter._generate_header(title, channel_info, data))
        text_parts.append(TextFormatter._generate_portfolio_section(portfolio_view))
        text_parts.append(TextFormatter._generate_growth_section(data.get("growth_view", {})))
        text_parts.append(TextFormatter._generate_theme_section(data.get("theme_view", {})))
        text_parts.append(TextFormatter._generate_footer(data.get("generated_at", "")))

        return "\n".join(text_parts)

    @staticmethod
    def _generate_header(title: str, channel_info: str, data: Dict[str, Any]) -> str:
        """ヘッダーセクション生成"""
        timestamp = TextFormatter._format_jst_timestamp(data.get("generated_at", ""))
        separator = TextFormatter._draw_separator("=", 80)
        
        period_str = TextFormatter._format_period(data.get("growth_view", {}))
        
        return f"""{separator}
📊 {title}
Generated: {timestamp}
{separator}

Target: {channel_info}
Period: {period_str}
Last Updated: {timestamp}

{separator}"""

    @staticmethod
    def _generate_portfolio_section(portfolio_view: List[Dict[str, Any]]) -> str:
        """ポートフォリオセクション生成"""
        if not portfolio_view:
            return ""

        summary = TextFormatter._generate_portfolio_summary(portfolio_view)
        
        lines = [
            TextFormatter._draw_separator("─", 80),
            "📈 PORTFOLIO OVERVIEW",
            TextFormatter._draw_separator("─", 80),
            summary,
            ""
        ]

        for lecture in portfolio_view:
            lecture_id = lecture.get("lecture_id", "N/A")
            title = lecture.get("title", "N/A")[:50]
            view_count = TextFormatter._format_view_count(lecture.get("view_count", 0))
            engagement = TextFormatter._format_engagement_rate(lecture.get("engagement_rate", 0))
            
            lines.append(f"  • Lecture {lecture_id}: {view_count} views ({engagement} engagement)")

        return "\n".join(lines)

    @staticmethod
    def _generate_portfolio_summary(portfolio_view: List[Dict[str, Any]]) -> str:
        """ポートフォリオ集計行生成"""
        num_lectures = len(portfolio_view)
        total_views = sum(lec.get("view_count", 0) for lec in portfolio_view)
        avg_engagement = sum(lec.get("engagement_rate", 0) for lec in portfolio_view) / num_lectures if num_lectures > 0 else 0

        return f"要約: {num_lectures}講座 / 合計 {TextFormatter._format_view_count(total_views)} views / 平均エンゲージメント率 {avg_engagement*100:.2f}%"

    @staticmethod
    def _generate_growth_section(growth_view: Dict[str, Any]) -> str:
        """成長ハイライトセクション生成"""
        lines = [
            TextFormatter._draw_separator("─", 80),
            "📈 GROWTH HIGHLIGHTS",
            TextFormatter._draw_separator("─", 80),
        ]

        period = growth_view.get("period", "N/A")
        period_str = TextFormatter._format_period(growth_view)
        lines.append(f"Period: {period_str}")
        lines.append("")

        top_growth = growth_view.get("top_by_view_growth", [])
        if not top_growth:
            lines.append(TextFormatter.NO_GROWTH_MESSAGE)
        else:
            for entry in top_growth:
                lecture_id = entry.get("lecture_id", "N/A")
                view_delta = entry.get("view_count_delta", 0)
                growth_rate = entry.get("view_count_growth_rate", 0)
                
                if view_delta > 0 and growth_rate >= 0.01:
                    lines.append(f"  • Lecture {lecture_id}: +{TextFormatter._format_view_count(view_delta)} views (+{growth_rate*100:.2f}%)")

        return "\n".join(lines)

    @staticmethod
    def _generate_theme_section(theme_view: Dict[str, Any]) -> str:
        """テーマ分析セクション生成"""
        if not theme_view:
            return ""

        lines = [
            TextFormatter._draw_separator("─", 80),
            "🎨 THEME ANALYSIS",
            TextFormatter._draw_separator("─", 80),
            ""
        ]

        for theme_name, theme_data in theme_view.items():
            if isinstance(theme_data, dict) and "courses" in theme_data:
                courses = theme_data.get("courses", [])
                
                lines.append(f"【{theme_name}】")
                
                # 要約行を生成
                if courses:
                    top_course = max(courses, key=lambda c: c.get("view_count", 0))
                    summary = f"要約: {top_course.get('title', 'N/A')[:30]} が中核"
                    lines.append(f"  {summary}")
                
                # 上位 3 講座を表示
                sorted_courses = sorted(courses, key=lambda c: c.get("view_count", 0), reverse=True)[:3]
                for course in sorted_courses:
                    lecture_id = course.get("lecture_id", "N/A")
                    view_count = TextFormatter._format_view_count(course.get("view_count", 0))
                    engagement = TextFormatter._format_engagement_rate(course.get("engagement_rate", 0))
                    
                    lines.append(f"    • Lecture {lecture_id}: {view_count} views ({engagement} engagement)")
                
                # representative_pin を表示
                if "representative_pin" in top_course and top_course["representative_pin"]:
                    insight = top_course["representative_pin"].get("content", "")
                    truncated = TextFormatter._truncate_insight(insight)
                    lines.append(f"      └ Representative insight: {truncated}")
                
                # 代表講座を表示
                if sorted_courses:
                    top_id = sorted_courses[0].get("lecture_id", "N/A")
                    lines.append(f"  代表講座: Lecture {top_id}")
                
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _generate_footer(generated_at: str) -> str:
        """フッター生成"""
        timestamp = TextFormatter._format_jst_timestamp(generated_at)
        separator = TextFormatter._draw_separator("=", 80)
        
        return f"""{separator}
Last Updated: {timestamp}
{separator}"""

    @staticmethod
    def _format_jst_timestamp(dt_str: str) -> str:
        """JST タイムスタンプをフォーマット"""
        if not dt_str:
            return datetime.now(TextFormatter.JST_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S (JST)")
        
        try:
            # ISO 8601 フォーマットをパース
            if "T" in dt_str:
                if "+" in dt_str or dt_str.endswith("Z"):
                    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                else:
                    dt = datetime.fromisoformat(dt_str)
                    dt = dt.replace(tzinfo=TextFormatter.JST_TIMEZONE)
            else:
                return dt_str
            
            # JST に変換
            dt_jst = dt.astimezone(TextFormatter.JST_TIMEZONE)
            return dt_jst.strftime("%Y-%m-%d %H:%M:%S (JST)")
        except:
            return dt_str

    @staticmethod
    def _format_period(growth_view: Dict[str, Any]) -> str:
        """期間をフォーマット"""
        period = growth_view.get("period", "")
        if not period:
            return f"直近{TextFormatter.LOOKBACK_DAYS}日間"
        
        try:
            parts = period.split(" to ")
            if len(parts) == 2:
                return f"直近{TextFormatter.LOOKBACK_DAYS}日間（{parts[0]}〜{parts[1]}）"
        except:
            pass
        
        return period

    @staticmethod
    def _format_view_count(count: int) -> str:
        """ビュー数をフォーマット"""
        return f"{count:,}"

    @staticmethod
    def _format_engagement_rate(rate: float) -> str:
        """エンゲージメント率をフォーマット"""
        return f"{rate*100:.2f}%"

    @staticmethod
    def _truncate_insight(text: str, max_length: int = 120) -> str:
        """インサイトを指定文字数で切断"""
        if len(text) <= max_length:
            return text
        
        # 句点で切断
        truncated = text[:max_length]
        if TextFormatter.SENTENCE_END_MARKER in truncated:
            truncated = truncated[:truncated.rfind(TextFormatter.SENTENCE_END_MARKER) + 1]
        else:
            truncated = truncated.rstrip() + "…"
        
        return truncated

    @staticmethod
    def _draw_separator(char: str = "─", width: int = 80) -> str:
        """セパレータ行を描画"""
        return char * width
