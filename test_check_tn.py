import sys
sys.path.insert(0, 'scripts')
from quality_scoring_engine import load_scoring_config
import json

weights, rules = load_scoring_config('config/scoring_weights.json', 'config/scoring_rules.json')

print("=== theme_normalization 確認 ===")
print(f"'theme_normalization' in rules: {'theme_normalization' in rules}")
print(f"rules['theme_normalization'] type: {type(rules.get('theme_normalization'))}")
print(f"rules['theme_normalization'] value: {rules.get('theme_normalization')}")

if rules.get('theme_normalization'):
    tn = rules['theme_normalization']
    print(f"'groups' in theme_normalization: {'groups' in tn}")
    print(f"'mapping' in theme_normalization: {'mapping' in tn}")
