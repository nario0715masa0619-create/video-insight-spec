# generate_views.py

import os
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from converter.insight_spec_repository import InsightSpecRepository
from converter.youtube_metadata_service import YouTubeMetadataService
from converter.views_generator_service import ViewsGeneratorService

def main():
    parser = argparse.ArgumentParser(description="Phase 4: Views Generation")
    parser.add_argument("--lecture-ids", default="01,02,03,04,05", help="Lecture IDs (comma-separated)")
    parser.add_argument("--archive-dir", required=True, help="Archive directory path")
    parser.add_argument("--api-key", help="YouTube API key")
    
    args = parser.parse_args()
    
    lecture_ids = args.lecture_ids.split(",")
    repo = InsightSpecRepository(args.archive_dir)
    youtube_service = YouTubeMetadataService(args.api_key)
    
    print("【Phase 4: Views Generation】")
    print(f"Archive dir: {args.archive_dir}")
    print(f"Processing lectures: {', '.join(lecture_ids)}\n")
    
    JST = timezone(timedelta(hours=9))
    success_count = 0
    
    for lecture_id in lecture_ids:
        try:
            spec = repo.load(lecture_id)
            video_id = spec['video_meta']['video_id']
            
            # YouTube Analytics API でメトリクスを取得
            youtube_metrics = youtube_service.get_video_analytics(video_id)
            
            # center_pins を取得
            center_pins = spec.get('knowledge_core', {}).get('center_pins', [])
            
            # Views を生成
            views = ViewsGeneratorService.generate_views(spec['video_meta'], center_pins, youtube_metrics)
            
            # insight_spec に views を追加
            spec['views'] = views
            spec['_metadata']['converted_at'] = datetime.now(JST).isoformat()
            spec['_metadata']['conversion_phase'] = "Phase 4"
            
            # 保存
            repo.save(lecture_id, spec)
            
            print(f"✅ Lecture {lecture_id}: views generated")
            success_count += 1
        
        except Exception as e:
            print(f"❌ Lecture {lecture_id}: {str(e)}")
    
    print(f"\n✅ Phase 4 completed: {success_count} success, {len(lecture_ids) - success_count} failed")

if __name__ == "__main__":
    main()
