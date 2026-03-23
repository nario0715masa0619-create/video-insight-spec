import json

with open('D:/Knowledge_Base/Brain_Marketing/archive/Mk2_Core_01.json', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    print(f"{item['element_id']}: {item['content'][:60]}...")
