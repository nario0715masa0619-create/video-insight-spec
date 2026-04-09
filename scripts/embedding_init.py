import os
import json
import sys
sys.path.insert(0, 'scripts')

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers インストール済み")
except ImportError:
    print("❌ sentence-transformers をインストール中...")
    os.system("pip install sentence-transformers")
    from sentence_transformers import SentenceTransformer

def initialize_embedding_model():
    """Embedding モデルを初期化"""
    # 日本語対応の軽量モデル
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    print(f"=== Embedding モデル初期化 ===\n")
    print(f"モデル: {model_name}")
    print("ロード中...\n")
    
    model = SentenceTransformer(model_name)
    print(f"✅ モデルロード完了")
    print(f"Embedding 次元数: {model.get_sentence_embedding_dimension()}")
    
    return model

def test_embedding(model, test_themes):
    """Embedding テスト"""
    print(f"\n=== Embedding テスト ===\n")
    
    embeddings = model.encode(test_themes)
    
    for theme, emb in zip(test_themes, embeddings):
        print(f"▸ {theme}")
        print(f"  Shape: {emb.shape}, Norm: {(emb**2).sum():.4f}")
    
    return embeddings

if __name__ == '__main__':
    # モデル初期化
    model = initialize_embedding_model()
    
    # テストテーマ
    test_themes = [
        "コンテンツ制作",
        "マーケティング",
        "動画編集",
        "プロダクト開発",
        "分析"
    ]
    
    # Embedding テスト
    embeddings = test_embedding(model, test_themes)
    
    print("\n✅ Embedding 初期化完了")
