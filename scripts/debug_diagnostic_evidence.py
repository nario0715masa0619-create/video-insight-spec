import os
import sys
import argparse
import json
from pathlib import Path

# Add project root and streamlit_app to sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
streamlit_app_dir = repo_root / "streamlit_app"
if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

from streamlit_app.diagnostic_evidence import (
    extract_diagnostic_evidence,
    format_evidence_for_prompt,
)
from streamlit_app.data_loader import load_insight_specs
from streamlit_app.narrative_engine import NarrativeEngine

def main():
    parser = argparse.ArgumentParser(description="診断用中間材料のコンソール出力")
    parser.add_argument("--lecture-id", default=None, help="対象 lecture ID (例: 01)")
    parser.add_argument("--channel", action="store_true", help="チャンネル全体分析")
    parser.add_argument("--show-raw", action="store_true", help="生の insight_spec を表示")
    parser.add_argument("--show-evidence", action="store_true", help="診断用中間材料を表示")
    parser.add_argument("--show-prompt", action="store_true", help="AI プロンプトを表示")
    parser.add_argument("--no-llm", action="store_true", help="LLM を使わず、中間材料だけ出力")
    
    args = parser.parse_args()
    
    # Load data
    insight_specs = load_insight_specs()
    specs_list = list(insight_specs.values())
    
    if not specs_list:
        print("No specs found in config.DATA_DIR. Trying sample_archive...")
        sample_dir = repo_root / "sample_archive"
        for i in range(1, 6):
            fpath = sample_dir / f"insight_spec_{i:02d}.json"
            print(f"Checking {fpath}...")
            if fpath.exists():
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data['lecture_id'] = f"{i:02d}"
                    insight_specs[f"{i:02d}"] = data
                    print(f"Loaded {fpath.name}")
                    
    # Inject lecture_id from keys into the specs
    specs_list = []
    for k, v in insight_specs.items():
        v['lecture_id'] = k
        specs_list.append(v)
                    
    if not args.channel and args.lecture_id:
        target_specs = [s for s in specs_list if s.get('lecture_id') == args.lecture_id]
    else:
        target_specs = specs_list

    # [INPUT SUMMARY]
    print("\n" + "="*60)
    print("[INPUT SUMMARY]")
    print("="*60)
    print(f"Target lecture_id: {args.lecture_id or 'all (Channel Mode)'}")
    print(f"Channel mode: {args.channel}")
    print(f"Found insight specs: {len(target_specs)} files")
    
    if not target_specs:
        print("No matching specs found.")
        return

    if args.show_raw:
        print("\n" + "="*60)
        print("[RAW INSIGHT SPEC PREVIEW (First item)]")
        print("="*60)
        print(json.dumps(target_specs[0], ensure_ascii=False, indent=2)[:1000] + "\n... (truncated)")

    # [DIAGNOSTIC EVIDENCE]
    evidence = extract_diagnostic_evidence(target_specs)
    
    print("\n" + "="*60)
    print("[DIAGNOSTIC EVIDENCE]")
    print("="*60)
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    
    formatted_evidence = format_evidence_for_prompt(evidence)
    
    # [PROMPT PREVIEW]
    prompt = f"""
以下の診断用中間材料を元に、このコンテンツ（またはチャンネル全体）の現状を診断してください。

{formatted_evidence}

以下の点について、ビジネス上の視点から回答してください：
1) 現在の強みと、果たしている役割
2) 構造上の弱点（不足している要素や橋渡し）
3) 次に優先して制作すべきコンテンツの方向性

※数字ではなく、状態・意味・キーワードを中心に、自然な日本語で説明してください。
"""

    if args.show_prompt or (not args.no_llm and not args.show_raw):
        print("\n" + "="*60)
        print("[PROMPT PREVIEW]")
        print("="*60)
        print(prompt)
    
    # [DIAGNOSIS RESULT]
    if not args.no_llm:
        print("\n" + "="*60)
        print("[DIAGNOSIS RESULT]")
        print("="*60)
        
        try:
            engine = NarrativeEngine()
            if not getattr(engine, 'available', False):
                print("NarrativeEngine is disabled (no API key).")
                return
                
            print("Thinking...")
            result = engine._call_gpt(prompt)
            print("-" * 40)
            print(result)
            print("-" * 40)
        except Exception as e:
            print(f"Error calling LLM: {e}")

if __name__ == "__main__":
    main()
