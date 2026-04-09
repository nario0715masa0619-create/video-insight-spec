import json
import sys
sys.path.insert(0, 'scripts')

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def load_config_and_unmapped():
    """config と unmapped テーマを読み込む"""
    with open('config/scoring_rules.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    with open('data/remaining_unmapped_themes.json', 'r', encoding='utf-8') as f:
        unmapped = json.load(f)
    
    return rules, unmapped

def get_canonical_examples(rules):
    """各 canonical の代表テーマを取得"""
    canonical_examples = {}
    
    groups = rules['theme_normalization']['groups']
    for canonical, group_data in groups.items():
        # raw_themes から代表テーマを取得
        raw_themes = group_data.get('raw_themes', [])
        canonical_examples[canonical] = raw_themes[:5]  # 最初の5個
    
    return canonical_examples

def map_unmapped_to_canonical(model, unmapped_themes, canonical_examples):
    """Embedding を使用して unmapped テーマを canonical に割り当て"""
    
    print("=== Embedding ベース自動マッピング ===\n")
    
    # 全テーマと canonical をエンコード
    all_themes = unmapped_themes + [t for examples in canonical_examples.values() for t in examples]
    embeddings = model.encode(all_themes)
    
    unmapped_embeddings = embeddings[:len(unmapped_themes)]
    
    mappings = []
    
    for idx, unmapped_theme in enumerate(unmapped_themes):
        unmapped_emb = unmapped_embeddings[idx:idx+1]
        
        # 各 canonical との類似度を計算
        similarities = {}
        offset = len(unmapped_themes)
        
        for canonical, examples in canonical_examples.items():
            example_count = len(examples)
            canonical_embs = embeddings[offset:offset+example_count]
            
            # canonical 内の全テーマとの最大類似度を取得
            sims = cosine_similarity(unmapped_emb, canonical_embs)[0]
            similarities[canonical] = max(sims)
            
            offset += example_count
        
        # 最高スコアの canonical を選択
        best_canonical = max(similarities, key=similarities.get)
        confidence = similarities[best_canonical]
        
        mappings.append({
            'raw_theme': unmapped_theme,
            'recommended_canonical': best_canonical,
            'confidence': float(confidence),
            'similarities': {k: float(v) for k, v in similarities.items()}
        })
        
        print(f"▸ {unmapped_theme}")
        print(f"  → {best_canonical} (confidence: {confidence:.3f})")
    
    return mappings

def main():
    print("=== Phase 7-4 Embedding ベースマッピング開始 ===\n")
    
    # 1. Config と unmapped テーマ読み込み
    print("【Step 1: Config 読み込み】")
    rules, unmapped = load_config_and_unmapped()
    print(f"✅ unmapped テーマ: {len(unmapped)} 個\n")
    
    # 2. Embedding モデル読み込み
    print("【Step 2: Embedding モデル読み込み】")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print(f"✅ モデルロード完了\n")
    
    # 3. Canonical 代表テーマ取得
    print("【Step 3: Canonical 代表テーマ取得】")
    canonical_examples = get_canonical_examples(rules)
    for canonical, examples in canonical_examples.items():
        print(f"  {canonical}: {len(examples)} テーマ")
    print()
    
    # 4. 自動マッピング実行
    print("【Step 4: 自動マッピング実行】")
    mappings = map_unmapped_to_canonical(model, unmapped, canonical_examples)
    print()
    
    # 5. 結果保存
    print("【Step 5: 結果保存】")
    result = {
        'total_unmapped': len(unmapped),
        'mappings': mappings,
        'generation_timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    with open('data/embedding_mapping_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("✅ data/embedding_mapping_result.json に保存")
    print(f"\n=== 処理完了 ===")

if __name__ == '__main__':
    main()
