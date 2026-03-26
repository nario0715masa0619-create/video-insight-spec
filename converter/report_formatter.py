# converter/report_formatter.py

import json
from datetime import datetime
from typing import Dict, Any, List
from converter.report_utils import format_metric, get_trend_indicator

class ReportFormatter:
    """レポートを複数フォーマットで出力"""
    
    @staticmethod
    def to_html(reports: List[Dict[str, Any]], title: str = "Weekly Report") -> str:
        """
        レポートを HTML に変換
        
        Args:
            reports: レポートリスト
            title: レポートタイトル
        
        Returns:
            HTML 文字列
        """
        html_parts = []
        
        # HTML ヘッダ
        html_parts.append(f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            color: #2c3e50;
        }}
        .report-period {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .lecture-section {{
            margin-bottom: 40px;
            border: 1px solid #ecf0f1;
            padding: 20px;
            border-radius: 4px;
        }}
        .lecture-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #3498db;
        }}
        .metric-label {{
            font-size: 0.85em;
            color: #7f8c8d;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-delta {{
            font-size: 0.9em;
            color: #27ae60;
            margin-top: 5px;
        }}
        .metric-delta.negative {{
            color: #e74c3c;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-top: 10px;
        }}
        .status-up {{
            background-color: #d5f4e6;
            color: #27ae60;
        }}
        .status-neutral {{
            background-color: #fef5e7;
            color: #f39c12;
        }}
        .status-down {{
            background-color: #fadbd8;
            color: #e74c3c;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #95a5a6;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="report-period">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
        </div>
""")
        
        # 各レポートセクション
        for report in reports:
            if report.get("status") == "INSUFFICIENT_DATA":
                html_parts.append(f"""
        <div class="lecture-section">
            <div class="lecture-title">Lecture {report['lecture_id']}: {report.get('title', 'N/A')}</div>
            <p style="color: #e74c3c;">⚠️ {report['message']}</p>
        </div>
""")
            else:
                key_metrics = report.get("key_metrics", {})
                view_metric = key_metrics.get("view_count", {})
                growth = view_metric.get("growth_percent", 0)
                delta = view_metric.get("delta", 0)
                
                # ステータスバッジを決定
                if growth > 2.0:
                    status_class = "status-up"
                    trend = "📈 上昇傾向"
                elif growth > -2.0:
                    status_class = "status-neutral"
                    trend = "→ 横ばい"
                else:
                    status_class = "status-down"
                    trend = "📉 下降傾向"
                
                delta_class = "metric-delta" if delta >= 0 else "metric-delta negative"
                delta_sign = "+" if delta >= 0 else ""
                
                html_parts.append(f"""
        <div class="lecture-section">
            <div class="lecture-title">Lecture {report['lecture_id']}</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Views</div>
                    <div class="metric-value">{format_metric(view_metric.get('value', 0))}</div>
                    <div class="{delta_class}">{delta_sign}{format_metric(delta)} ({delta_sign}{growth:.2f}%)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Report Period</div>
                    <div class="metric-value" style="font-size: 1.2em;">{report['report_period']['start'][:10]}</div>
                    <div style="color: #7f8c8d; margin-top: 5px;">to {report['report_period']['end'][:10]}</div>
                </div>
            </div>
            <span class="status-badge {status_class}">{trend}</span>
        </div>
""")
        
        # HTML フッタ
        html_parts.append("""
        <div class="footer">
            <p>This report was automatically generated by video-insight-spec Phase 4.1 Weekly Report Generator.</p>
        </div>
    </div>
</body>
</html>
""")
        
        return "".join(html_parts)
    
    @staticmethod
    def to_json(reports: List[Dict[str, Any]]) -> str:
        """
        レポートを JSON に変換
        
        Args:
            reports: レポートリスト
        
        Returns:
            JSON 文字列
        """
        return json.dumps(reports, ensure_ascii=False, indent=2)
    
    @staticmethod
    def to_text(reports: List[Dict[str, Any]]) -> str:
        """
        レポートをプレーンテキストに変換
        
        Args:
            reports: レポートリスト
        
        Returns:
            テキスト文字列
        """
        lines = []
        lines.append("=" * 80)
        lines.append("Weekly Report - Video Insight Spec Phase 4.1")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("=" * 80)
        lines.append("")
        
        for report in reports:
            lines.append(f"Lecture {report['lecture_id']}")
            lines.append("-" * 80)
            
            if report.get("status") == "INSUFFICIENT_DATA":
                lines.append(f"  ⚠️  {report['message']}")
            else:
                key_metrics = report.get("key_metrics", {})
                view_metric = key_metrics.get("view_count", {})
                growth = view_metric.get("growth_percent", 0)
                delta = view_metric.get("delta", 0)
                
                lines.append(f"  Period: {report['report_period']['start'][:10]} to {report['report_period']['end'][:10]}")
                lines.append(f"  Views: {format_metric(view_metric.get('value', 0))}")
                lines.append(f"  Delta: +{delta:,} (+{growth:.2f}%)")
                lines.append(f"  Trend: {get_trend_indicator(growth)}")
            
            lines.append("")
        
        return "\n".join(lines)
