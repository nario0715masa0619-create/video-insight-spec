# weekly_report_generator.py

import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from converter.report_utils import calculate_delta, calculate_growth_percentage

class WeeklyReportGenerator:
    """週次レポート生成エンジン"""
    
    JST = timezone(timedelta(hours=9))
    
    def __init__(self, archive_dir: str, api_key: Optional[str] = None):
        self.archive_dir = Path(archive_dir)
        self.api_key = api_key
    
    def load_insight_spec(self, lecture_id: str) -> Dict[str, Any]:
        """insight_spec JSON を読み込む"""
        file_path = self.archive_dir / f"insight_spec_{lecture_id}.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_snapshot_history(self, insight_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """snapshot_history を取得"""
        return insight_spec.get('views', {}).get('competitive', {}).get('snapshot_history', [])
    
    def generate_weekly_report(self, lecture_id: str) -> Dict[str, Any]:
        """週次レポートを生成"""
        spec = self.load_insight_spec(lecture_id)
        snapshot_history = self.get_snapshot_history(spec)
        
        # スナップショット数の確認
        if len(snapshot_history) == 0:
            return {
                "lecture_id": lecture_id,
                "status": "NO_SNAPSHOT",
                "message": "スナップショットデータが見つかりません"
            }
        
        # 初回実行時（スナップショット 1 つ）
        if len(snapshot_history) == 1:
            snapshot = snapshot_history[0]
            return {
                "lecture_id": lecture_id,
                "title": spec['video_meta']['title'],
                "status": "BASELINE_SET",
                "baseline_timestamp": snapshot['timestamp'],
                "baseline_metrics": {"view_count": snapshot.get("view_count", 0), "like_count": snapshot.get("like_count", 0), "comment_count": snapshot.get("comment_count", 0), "engagement_rate": snapshot.get("engagement_rate", 0)},
                "message": "初回ベースラインスナップショットを記録しました。次週のレポートで増減を表示します。"
            }
        
        # 2 つ以上のスナップショットがある場合（差分計算可能）
        previous = snapshot_history[-2]
        current = snapshot_history[-1]
        
        # Delta を計算
        delta = calculate_delta(previous, current)
        growth_percentage = calculate_growth_percentage(previous, delta)
        
        # レポート構築
        report = {
            "lecture_id": lecture_id,
            "title": spec['video_meta']['title'],
            "report_period": {
                "start": snapshot_history[-2]['timestamp'],
                "end": snapshot_history[-1]['timestamp']
            },
            "baseline": previous,
            "current": current,
            "delta": delta,
            "growth_percentage": growth_percentage,
            "key_metrics": {
                "view_count": {
                    "value": current['view_count'],
                    "delta": delta['view_count'],
                    "growth_percent": growth_percentage['view_count']
                },
                "engagement_rate": {
                    "value": current['engagement_rate'],
                    "status": "STABLE" if growth_percentage['view_count'] > -5 else "DECLINING"
                }
            }
        }
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Phase 4.1: Weekly Report Generator")
    parser.add_argument("--lecture-ids", default="01,02,03,04,05", help="Lecture IDs (comma-separated)")
    parser.add_argument("--archive-dir", required=True, help="Archive directory path")
    parser.add_argument("--api-key", help="YouTube API key")
    parser.add_argument("--output-dir", default="reports/weekly", help="Output directory for reports")
    
    args = parser.parse_args()
    
    lecture_ids = args.lecture_ids.split(",")
    generator = WeeklyReportGenerator(args.archive_dir, args.api_key)
    
    print("【Phase 4.1: Weekly Report Generation】")
    print(f"Archive dir: {args.archive_dir}")
    print(f"Processing lectures: {', '.join(lecture_ids)}\n")
    
    reports = []
    success_count = 0
    baseline_count = 0
    
    for lecture_id in lecture_ids:
        try:
            report = generator.generate_weekly_report(lecture_id)
            reports.append(report)
            
            if report.get("status") == "BASELINE_SET":
                print(f"📊 Lecture {lecture_id}: Baseline set (ready for next weekly report)")
                baseline_count += 1
            elif report.get("status") in ["NO_SNAPSHOT", None]:
                if "delta" in report:
                    growth = report['key_metrics']['view_count']['growth_percent']
                    delta = report['key_metrics']['view_count']['delta']
                    print(f"✅ Lecture {lecture_id}: +{growth:.2f}% views (+{delta})")
                    success_count += 1
        except Exception as e:
            print(f"❌ Lecture {lecture_id}: {str(e)}")
    
    print(f"\n✅ Phase 4.1 completed:")
    print(f"   - {success_count} reports with delta")
    print(f"   - {baseline_count} baseline snapshots set")
    
    # レポートを JSON で保存
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = output_dir / f"weekly_report_{datetime.now(generator.JST).strftime('%Y%m%d')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print(f"Report saved: {report_file}")

if __name__ == "__main__":
    main()


