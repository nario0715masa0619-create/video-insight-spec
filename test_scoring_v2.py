import sys
sys.path.insert(0, 'scripts')
from quality_scoring_engine import score_insight_json
import json
import os

# カレントディレクトリ確認
print(f"Current directory: {os.getcwd()}")
print(f"Config weights exists: {os.path.exists('config/scoring_weights.json')}")
print(f"Config rules exists: {os.path.exists('config/scoring_rules.json')}")

# サンプル insight_spec を読み込む
with open(r'D:\AI_Data\video-insight-spec\archive\insight_spec_01.json', 'r', encoding='utf-8') as f:
    sample_insight = json.load(f)

# スコアリング実行
try:
    result = score_insight_json(
        sample_insight,
        'config/scoring_weights.json',
        'config/scoring_rules.json'
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
