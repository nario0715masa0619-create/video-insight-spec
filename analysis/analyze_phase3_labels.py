import json
import os
from collections import Counter

def analyze_phase3_labels(archive_dir):
    results = {
        'total_pins': 0,
        'business_themes': Counter(),
        'funnel_stages': Counter(),
        'difficulties': Counter(),
        'lecture_details': {}
    }
    
    for i in range(1, 6):
        lecture_id = f"{i:02d}"
        filepath = os.path.join(archive_dir, f"insight_spec_{lecture_id}.json")
        
        if not os.path.exists(filepath):
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pins = data.get('knowledge_core', {}).get('center_pins', [])
        results['total_pins'] += len(pins)
        
        lecture_stats = {
            'pin_count': len(pins),
            'themes': Counter(),
            'stages': Counter(),
            'difficulties': Counter()
        }
        
        for pin in pins:
            labels = pin.get('labels', {})
            themes = labels.get('business_theme', [])
            if isinstance(themes, list):
                for theme in themes:
                    results['business_themes'][theme] += 1
                    lecture_stats['themes'][theme] += 1
            
            stage = labels.get('funnel_stage', 'unknown')
            results['funnel_stages'][stage] += 1
            lecture_stats['stages'][stage] += 1
            
            difficulty = labels.get('difficulty', 'unknown')
            results['difficulties'][difficulty] += 1
            lecture_stats['difficulties'][difficulty] += 1
        
        results['lecture_details'][lecture_id] = lecture_stats
    
    return results

def print_results(results):
    print("\n" + "="*60)
    print("Phase 3 ラベル分析結果")
    print("="*60)
    
    print(f"\n総ピン数: {results['total_pins']}")
    
    print("\nbusiness_theme 分布:")
    for theme, count in results['business_themes'].most_common(10):
        pct = 100 * count / results['total_pins']
        print(f"  {theme:20} {count:3} ({pct:5.1f}%)")
    
    print("\nfunnel_stage 分布:")
    for stage, count in results['funnel_stages'].most_common(10):
        pct = 100 * count / results['total_pins']
        print(f"  {stage:20} {count:3} ({pct:5.1f}%)")
    
    print("\ndifficulty 分布:")
    for difficulty, count in results['difficulties'].most_common(10):
        pct = 100 * count / results['total_pins']
        print(f"  {difficulty:20} {count:3} ({pct:5.1f}%)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    import sys
    archive_dir = sys.argv[1] if len(sys.argv) > 1 else r"D:\AI_Data\video-insight-spec\archive"
    print(f"分析対象: {archive_dir}")
    results = analyze_phase3_labels(archive_dir)
    print_results(results)
