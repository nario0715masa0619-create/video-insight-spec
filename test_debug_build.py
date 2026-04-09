import sys
sys.path.insert(0, 'scripts')
from quality_scoring_engine import load_scoring_config, build_scoring_result
import json

# サンプル insight_spec を読み込む
with open(r'D:\AI_Data\video-insight-spec\archive\insight_spec_01.json', 'r', encoding='utf-8') as f:
    sample_insight = json.load(f)

# 設定ロード
weights, rules = load_scoring_config('config/scoring_weights.json', 'config/scoring_rules.json')

print("=== build_scoring_result() テスト ===")
print(f"rules type before: {type(rules)}")
print(f"rules is None before: {rules is None}")

try:
    result = build_scoring_result(sample_insight, weights, rules)
    print("Success!")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
