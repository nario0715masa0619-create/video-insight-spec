import json

with open('config/scoring_rules.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

print("Keys:", list(rules.keys()))
print("theme_normalization exists:", "theme_normalization" in rules)

if "theme_normalization" in rules:
    print("mapping keys:", list(rules["theme_normalization"]["mapping"].keys())[:5])
else:
    print("ERROR: theme_normalization not found in rules")
