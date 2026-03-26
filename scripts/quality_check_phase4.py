# quality_check_phase4.py

import json
import pathlib

def check_phase4_quality():
    archive_dir = pathlib.Path(r"D:\AI_Data\video-insight-spec\archive")
    
    print("【Phase 4 品質検査】\n")
    
    total_passed = 0
    total_failed = 0
    
    for lecture_id in ["01", "02", "03", "04", "05"]:
        file_path = archive_dir / f"insight_spec_{lecture_id}.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Views セクションの存在確認
            views = data.get('views', {})
            
            checks = {
                "views.competitive": bool(views.get('competitive')),
                "views.education": bool(views.get('education')),
                "views.self_improvement": bool(views.get('self_improvement')),
                "competitive.metrics": bool(views.get('competitive', {}).get('metrics')),
                "competitive.top_pins_by_engagement": bool(views.get('competitive', {}).get('top_pins_by_engagement')),
                "education.difficulty_distribution": bool(views.get('education', {}).get('difficulty_distribution')),
                "education.top_pins_by_difficulty": bool(views.get('education', {}).get('top_pins_by_difficulty')),
                "self_improvement.funnel_flow": bool(views.get('self_improvement', {}).get('funnel_flow')),
            }
            
            passed = sum(1 for v in checks.values() if v)
            failed = len(checks) - passed
            total_passed += passed
            total_failed += failed
            
            status = "✅" if failed == 0 else "⚠️"
            print(f"{status} Lecture {lecture_id}: {passed}/{len(checks)} 合格")
            
            if failed > 0:
                for check_name, result in checks.items():
                    if not result:
                        print(f"   ❌ {check_name} が欠損")
            
            # メトリクスの詳細表示
            if views.get('competitive', {}).get('metrics'):
                metrics = views['competitive']['metrics']
                print(f"   📊 Metrics: views={metrics.get('view_count')}, likes={metrics.get('like_count')}, comments={metrics.get('comment_count')}")
                
                if views['competitive'].get('top_pins_by_engagement'):
                    top_pins = views['competitive']['top_pins_by_engagement']
                    print(f"   🏆 Top {len(top_pins)} pins by engagement score")
                    for pin in top_pins[:1]:
                        print(f"      - {pin['element_id']}: {pin['engagement_score']}")
        
        except Exception as e:
            print(f"❌ Lecture {lecture_id}: {str(e)}")
            total_failed += 8
    
    print(f"\n【結果】")
    print(f"✅ 合格: {total_passed}")
    print(f"❌ 不合格: {total_failed}")
    
    if total_failed == 0:
        print(f"\n🎉 Phase 4 品質検査: PASSED (5/5)")
        return 0
    else:
        print(f"\n⚠️  Phase 4 品質検査: FAILED")
        return 1

if __name__ == '__main__':
    exit(check_phase4_quality())
