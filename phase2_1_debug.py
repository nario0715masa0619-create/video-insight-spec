import json
from janome.tokenizer import Tokenizer

tokenizer = Tokenizer()

with open('D:/Knowledge_Base/Brain_Marketing/archive/Mk2_Core_01.json', encoding='utf-8') as f:
    center_pins = json.load(f)

content_texts = [pin["content"] for pin in center_pins]
full_content = " ".join(content_texts)

print("=" * 80)
print("🔍 抽出前の全トークン")
print("=" * 80)

all_tokens = []
for token in tokenizer.tokenize(full_content):
    word = token.surface
    pos = token.part_of_speech[0]
    all_tokens.append((word, pos))

# 品詞別に表示
print("\n【名詞】")
nouns = [(w, p) for w, p in all_tokens if p == "名詞" and len(w) >= 2]
print(f"  {nouns[:30]}")

print("\n【動詞】")
verbs = [(w, p) for w, p in all_tokens if p == "動詞" and len(w) >= 2]
print(f"  {verbs[:30]}")

print("\n【形容詞】")
adjs = [(w, p) for w, p in all_tokens if p == "形容詞" and len(w) >= 2]
print(f"  {adjs[:30]}")
