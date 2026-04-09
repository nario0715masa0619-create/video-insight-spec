import json
from collections import Counter

with open(r'D:\AI_Data\video-insight-spec\archive\insight_spec_01.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# center_pins のテーマ分布を確認
themes = []
for pin in data['knowledge_core']['center_pins']:
    if 'labels' in pin and 'business_theme' in pin['labels']:
        themes.extend(pin['labels']['business_theme'])

theme_counts = Counter(themes)

print("=== テーマ分布 ===")
for theme, count in theme_counts.most_common():
    print(f"{theme}: {count}個")

print(f"\n総テーマ数: {len(themes)}")
print(f"ユニークテーマ: {len(theme_counts)}")
print(f"最多テーマの占有率: {theme_counts.most_common(1)[0][1] / len(themes) * 100:.1f}%")
