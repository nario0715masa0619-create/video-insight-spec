import os
import json
import sys
import io

# Unicode 対応
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, 'scripts')

from quality_scoring_engine import load_scoring_config, score_insight_json

def load_all_insights():
    """6つのinsight_spec JSONを読み込む"""
    archive_path = r'D:\AI_Data\video-insight-spec\archive'
    filenames = [
        'insight_spec_01.json',
        'insight_spec_02.json',
        'insight_spec_03.json',
        'insight_spec_04.json',
        'insight_spec_05.json',
        'insight_spec_mirirepi.json'
    ]
    
    insights = []
    for filename in filenames:
        filepath = os.path.join(archive_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                insight = json.load(f)
                insight['_filename'] = filename
                insights.append(insight)
                print(f"OK {filename} read")
        except Exception as e:
            print(f"NG {filename}: {e}")
    
    return insights, filenames

def apply_scoring_batch(insights, filenames, weights, rules):
    """全insights にスコアリングを適用"""
    
    scored_insights = []
    scores = []
    
    for insight, filename in zip(insights, filenames):
        score_result = score_insight_json(insight, weights, rules)
        
        scored_insights.append(score_result)
        scores.append({
            'filename': filename,
            'semantic_purity_score': score_result['scoring'].get('semantic_purity_score', 0),
            'quality_score': score_result['scoring'].get('quality_score', 0),
            'ranking_score': score_result['scoring'].get('ranking_score', 0)
        })
        
        print(f"   semantic_purity: {score_result['scoring'].get('semantic_purity_score', 0):.2f}")
    
    return scored_insights, scores

def save_scored_insights(scored_insights):
    """スコア付きinsightsを保存"""
    output_dir = 'results'
    
    for idx, insight in enumerate(scored_insights):
        filenames = ['insight_spec_01', 'insight_spec_02', 'insight_spec_03', 'insight_spec_04', 'insight_spec_05', 'insight_spec_mirirepi']
        output_filename = f"{filenames[idx]}_scored.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insight, f, ensure_ascii=False, indent=2)
        
        print(f"OK {output_filename} saved")

def generate_summary(scores):
    """サマリー JSON生成"""
    summary = {
        'total_files': len(scores),
        'average_semantic_purity': round(sum(s['semantic_purity_score'] for s in scores) / len(scores), 2),
        'generation_timestamp': __import__('datetime').datetime.now().isoformat(),
        'scores': scores
    }
    
    with open('results/summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return summary

def main():
    print("=== Scoring batch process start ===\n")
    
    print("Step 0: Load config")
    weights, rules = load_scoring_config('config/scoring_weights.json', 'config/scoring_rules.json')
    print(f"OK Config loaded\n")
    
    print("Step 1: Load insights")
    insights, filenames = load_all_insights()
    print(f"OK {len(insights)} files loaded\n")
    
    print("Step 2: Apply scoring")
    scored_insights, scores = apply_scoring_batch(insights, filenames, weights, rules)
    print(f"OK Scoring complete\n")
    
    print("Step 3: Save results")
    save_scored_insights(scored_insights)
    print(f"OK Save complete\n")
    
    print("Step 4: Generate summary")
    summary = generate_summary(scores)
    print(f"OK summary.json generated\n")
    
    print("=== Process complete ===")
    print(f"Average semantic_purity_score: {summary['average_semantic_purity']}")
    print(f"Output directory: results/")

if __name__ == '__main__':
    main()
