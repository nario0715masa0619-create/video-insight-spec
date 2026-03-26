"""
Phase 4.2: Competitor Analytics Generator
"""

import argparse
import json
import os
from datetime import datetime, timezone, timedelta
from converter.portfolio_view_service import PortfolioViewService
from converter.growth_view_service import GrowthViewService
from converter.insight_spec_repository import InsightSpecRepository


def main():
    parser = argparse.ArgumentParser(description="Phase 4.2 Competitor Analytics Generator")
    parser.add_argument("--lecture-ids", required=True, help="Lecture IDs (comma-separated, e.g., '01,02,03')")
    parser.add_argument("--archive-dir", required=True, help="Archive directory path")
    parser.add_argument("--output-dir", default="reports/competitor_analytics", help="Output directory for reports")
    
    args = parser.parse_args()
    
    lecture_ids = [lid.strip() for lid in args.lecture_ids.split(",")]
    archive_dir = args.archive_dir
    output_dir = args.output_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    repo = InsightSpecRepository(archive_dir)
    
    print("【Phase 4.2: Competitor Analytics Generation】")
    print(f"Archive dir: {archive_dir}")
    print(f"Processing lectures: {', '.join(lecture_ids)}\n")
    
    insight_specs = []
    for lecture_id in lecture_ids:
        try:
            spec = repo.load(lecture_id)
            spec["lecture_id"] = lecture_id
            insight_specs.append(spec)
            print(f"✅ Lecture {lecture_id}: loaded")
        except Exception as e:
            print(f"❌ Lecture {lecture_id}: {str(e)}")
    
    if not insight_specs:
        print("❌ No specs loaded. Exiting.")
        return
    
    print("\n【Portfolio View Generation】")
    portfolio_view = PortfolioViewService.generate_portfolio_view(insight_specs, role="self")
    print(f"✅ Portfolio view generated: {len(portfolio_view)} lectures")
    # ✅ INFO: snapshot_history < 2 の講座をスキップ
    skipped_lectures = [
        spec.get("lecture_id", "unknown") 
        for spec in insight_specs 
        if len(spec.get("views", {}).get("competitive", {}).get("snapshot_history", [])) < 2
    ]
    if skipped_lectures:
        print(f"ℹ️  INFO: snapshot_history < 2 の講座はスキップ: {', '.join(skipped_lectures)}")


    
    print("\n【Growth View Generation】")
    growth_view = GrowthViewService.generate_growth_view(insight_specs, role="self")
    print(f"✅ Growth view generated: {len(growth_view.get('top_by_view_growth', []))} lectures with growth data")
    
    # ✅ FIX: JST timezone を正しく指定
    JST = timezone(timedelta(hours=9))
    generated_at = datetime.now(JST).isoformat()
    
    competitor_analytics = {
        "generated_at": generated_at,
        "portfolio_view": portfolio_view,
        "growth_view": growth_view
    }
    
    output_file = os.path.join(output_dir, f"competitor_analytics_{datetime.now().strftime('%Y%m%d')}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(competitor_analytics, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Competitor analytics generated: {output_file}")
    
    print("\n【Summary】")
    print(f"Portfolio items: {len(portfolio_view)}")
    print(f"Growth items: {len(growth_view.get('top_by_view_growth', []))}")
    print(f"Period: {growth_view.get('period', 'unknown')}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()




