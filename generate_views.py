# generate_views.py

import os
import argparse
from datetime import datetime
from converter.insight_spec_repository import InsightSpecRepository
from converter.youtube_metadata_service import YouTubeMetadataService
from converter.views_generator_service import ViewsGeneratorService


def main():
    parser = argparse.ArgumentParser(description="Generate views for insight_spec (Phase 4)")
    parser.add_argument('--lecture-ids', default='01,02,03,04,05', help='Comma-separated lecture IDs')
    parser.add_argument('--archive-dir', default=os.getenv('ARCHIVE_OUTPUT_DIR'), help='Archive directory')
    parser.add_argument('--api-key', default=os.getenv('YOUTUBE_API_KEY'), help='YouTube API key')
    
    args = parser.parse_args()
    
    lecture_ids = [lid.strip() for lid in args.lecture_ids.split(',')]
    repo = InsightSpecRepository(args.archive_dir)
    youtube_service = YouTubeMetadataService(args.api_key)
    views_service = ViewsGeneratorService()
    
    success_count = 0
    failed_count = 0
    
    print("【Phase 4: Views Generation】")
    print(f"Archive dir: {args.archive_dir}")
    print(f"Processing lectures: {', '.join(lecture_ids)}\n")
    
    for lecture_id in lecture_ids:
        try:
            # Load insight_spec
            insight_spec = repo.load(lecture_id)
            
            # Fetch YouTube metrics
            video_id = insight_spec['video_meta']['video_id']
            metrics = youtube_service.get_video_stats(video_id)
            
            # Generate views
            views = views_service.generate_views(
                insight_spec['video_meta'],
                insight_spec['knowledge_core']['center_pins'],
                metrics
            )
            
            # Update and save
            insight_spec['views'] = views
            insight_spec['_metadata']['converted_at'] = datetime.utcnow().isoformat() + "Z"
            insight_spec['_metadata']['conversion_phase'] = "Phase 4"
            
            repo.save(lecture_id, insight_spec)
            
            print(f"✅ Lecture {lecture_id}: views generated (competitive, education, self_improvement)")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Lecture {lecture_id}: {str(e)}")
            failed_count += 1
    
    print(f"\n✅ Phase 4 completed: {success_count} success, {failed_count} failed")
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    exit(main())
