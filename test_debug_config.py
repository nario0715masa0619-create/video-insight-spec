import sys
sys.path.insert(0, 'scripts')
from quality_scoring_engine import load_scoring_config
import json

# 設定ロード確認
print("=== load_scoring_config() テスト ===")
try:
    weights, rules = load_scoring_config('config/scoring_weights.json', 'config/scoring_rules.json')
    print(f"weights type: {type(weights)}")
    print(f"weights keys: {list(weights.keys()) if weights else 'None'}")
    print(f"rules type: {type(rules)}")
    print(f"rules keys: {list(rules.keys()) if rules else 'None'}")
    print(f"rules is None: {rules is None}")
    if rules:
        print(f"theme_normalization exists: {'theme_normalization' in rules}")
except Exception as e:
    print(f"Error loading config: {e}")
    import traceback
    traceback.print_exc()
