from janome.tokenizer import Tokenizer
import json

tokenizer = Tokenizer()

with open('D:/Knowledge_Base/Brain_Marketing/archive/Mk2_Core_01.json', encoding='utf-8') as f:
    center_pins = json.load(f)

content_texts = [pin["content"] for pin in center_pins]
full_content = " ".join(content_texts)

print("テキスト:", full_content[:100])
print("テキスト長:", len(full_content))
print()

# 全トークンを表示
print("全トークン:")
count = 0
for token in tokenizer.tokenize(full_content):
    print(f"  '{token.surface}' ({token.part_of_speech[0]})")
    count += 1
    if count >= 30:
        break

print(f"\n総トークン数: {count}...")