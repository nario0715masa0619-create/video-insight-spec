import os
import json
import sys
import re
from dotenv import load_dotenv

sys.path.insert(0, 'scripts')

# .env から API キーを読み込み
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    print("❌ google-generativeai をインストールしてください:")
    print("   pip install google-generativeai")
    sys.exit(1)

def run_gemini_clustering():
    """Gemini API を使用して unmapped テーマをクラスタリング"""
    
    # API キー設定（.env から取得）
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ .env に GEMINI_API_KEY が設定されていません")
        sys.exit(1)
    
    # モデルID設定（.env から取得）
    model_id = os.getenv('GEMINI_MODEL_ID')
    if not model_id:
        print("❌ .env に GEMINI_MODEL_ID が設定されていません")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    print(f"✅ API キー読み込み完了（先頭: {api_key[:10]}...）")
    print(f"✅ モデル: {model_id}\n")
    
    # プロンプト読み込み
    with open('data/gemini_prompt_phase2.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    print("=== Gemini API クラスタリング実行 ===\n")
    print("プロンプト送信中...\n")
    
    try:
        model = genai.GenerativeModel(model_id)
        response = model.generate_content(prompt)
        
        response_text = response.text
        print("✅ Gemini レスポンス受信完了\n")
        
        # JSON 部分を抽出
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            try:
                classifications = json.loads(json_str)
                print(f"✅ JSON パース成功")
                print(f"   分類テーマ数: {len(classifications.get('classifications', []))}")
                
                # 結果保存
                with open('data/gemini_clustering_result.json', 'w', encoding='utf-8') as f:
                    json.dump(classifications, f, ensure_ascii=False, indent=2)
                
                print(f"✅ data/gemini_clustering_result.json に保存")
                
                # サマリー表示
                if 'phase2_summary' in classifications:
                    summary = classifications['phase2_summary']
                    print(f"\n【Phase 2 サマリー】")
                    print(f"  分類テーマ数: {summary.get('total_classified', 0)}")
                    print(f"  新規クラスタ提案: {summary.get('new_clusters_proposed', 0)}")
                    print(f"  平均信頼度: {summary.get('confidence_average', 0):.2f}")
                
                return classifications
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON パースエラー: {e}")
                print("レスポンス全文を保存します...\n")
        
        # レスポンス全文保存
        with open('data/gemini_response_raw.txt', 'w', encoding='utf-8') as f:
            f.write(response_text)
        
        print("✅ data/gemini_response_raw.txt にレスポンス全文を保存")
        return None
        
    except Exception as e:
        print(f"❌ Gemini API エラー: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_gemini_clustering()
