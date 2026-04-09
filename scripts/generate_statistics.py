import os
import json
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, 'scripts')

def load_all_scored_insights():
    """全スコアファイルを読み込む"""
    results_dir = 'results'
    scored_files = [f for f in os.listdir(results_dir) if f.endswith('_scored.json')]
    
    insights = {}
    for filename in sorted(scored_files):
        with open(os.path.join(results_dir, filename), 'r', encoding='utf-8') as f:
            insights[filename.replace('_scored.json', '')] = json.load(f)
    
    return insights

def calculate_statistics(insights):
    """統計計算"""
    stats = {
        'total_files': len(insights),
        'semantic_purity': [],
        'quality_score': [],
        'ranking_score': [],
        'canonical_distribution': {},
        'source_distribution': {},
        'unmapped_themes': []
    }
    
    for filename, insight in insights.items():
        # スコア収集
        scoring = insight['scoring']
        stats['semantic_purity'].append(scoring['semantic_purity_score'])
        stats['quality_score'].append(scoring['quality_score'])
        stats['ranking_score'].append(scoring['ranking_score'])
        
        # テーマ分析
        if 'normalization_log' in insight['score_details']:
            for log_entry in insight['score_details']['normalization_log']:
                canonical = log_entry.get('canonical', 'unknown')
                source = log_entry.get('source', 'unknown')
                
                if canonical not in stats['canonical_distribution']:
                    stats['canonical_distribution'][canonical] = 0
                stats['canonical_distribution'][canonical] += 1
                
                if source not in stats['source_distribution']:
                    stats['source_distribution'][source] = 0
                stats['source_distribution'][source] += 1
                
                if source == 'unmapped':
                    stats['unmapped_themes'].append(log_entry.get('raw', 'unknown'))
    
    # 統計量計算
    stats['semantic_purity_mean'] = round(np.mean(stats['semantic_purity']), 2)
    stats['semantic_purity_std'] = round(np.std(stats['semantic_purity']), 2)
    stats['semantic_purity_min'] = round(min(stats['semantic_purity']), 2)
    stats['semantic_purity_max'] = round(max(stats['semantic_purity']), 2)
    
    return stats

def generate_report(stats):
    """統計レポート生成"""
    report = {
        'generation_timestamp': datetime.now().isoformat(),
        'phase': 'Phase 7-5 Final Statistics',
        'summary': {
            'total_files': stats['total_files'],
            'avg_semantic_purity': stats['semantic_purity_mean'],
            'std_semantic_purity': stats['semantic_purity_std'],
            'min_semantic_purity': stats['semantic_purity_min'],
            'max_semantic_purity': stats['semantic_purity_max'],
            'total_unmapped': len(stats['unmapped_themes'])
        },
        'detailed_stats': stats
    }
    
    return report

def main():
    print("=== Phase 7-5 Final Statistics Generation ===\n")
    
    print("Step 1: Load scored insights")
    insights = load_all_scored_insights()
    print(f"OK Loaded {len(insights)} files\n")
    
    print("Step 2: Calculate statistics")
    stats = calculate_statistics(insights)
    print(f"OK Calculated\n")
    
    print("Step 3: Generate report")
    report = generate_report(stats)
    
    with open('data/final_statistics_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("OK Report saved to data/final_statistics_report.json\n")
    
    print("=== Statistics Summary ===")
    print(f"Total files: {stats['total_files']}")
    print(f"Avg semantic_purity: {stats['semantic_purity_mean']} (std: {stats['semantic_purity_std']})")
    print(f"Range: {stats['semantic_purity_min']} - {stats['semantic_purity_max']}")
    print(f"Total unmapped themes: {len(stats['unmapped_themes'])}")
    
    print("\nCanonical distribution:")
    for canonical, count in sorted(stats['canonical_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {canonical}: {count}")
    
    print("\nSource distribution:")
    for source, count in sorted(stats['source_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}")

if __name__ == '__main__':
    main()
