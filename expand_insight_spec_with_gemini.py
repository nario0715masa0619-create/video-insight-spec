#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3: Label insight_spec_XX.json with Gemini Knowledge
各 center_pin にビジネステーマ・ファネルステージ・難易度のラベルを自動付与
"""

import os, sys, argparse, logging
from pathlib import Path
from dotenv import load_dotenv
from converter.gemini_knowledge_labeler import GeminiKnowledgeLabeler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Label insight_spec_XX.json with Gemini Knowledge (Phase 3)")
    parser.add_argument("--lecture-id", type=str, required=True, help="Lecture ID (e.g., '01')")
    parser.add_argument("--input", type=str, help="Path to insight_spec_XX.json (auto-detect if not specified)")
    parser.add_argument("--output", type=str, help="Output path for labeled insight_spec (same as input if not specified)")
    parser.add_argument("--archive-dir", type=str, default=r"D:\Knowledge_Base\Brain_Marketing\archive", help="Archive directory containing insight_spec files")
    parser.add_argument("--top-n", type=int, default=5, help="Number of top center_pins to label (default: 5)")
    parser.add_argument("--api-key", type=str, help="Gemini API key (from .env if not specified)")
    args = parser.parse_args()

    lecture_id = args.lecture_id
    input_path = args.input or os.path.join(args.archive_dir, f"insight_spec_{lecture_id}.json")
    output_path = args.output or input_path

    if not os.path.exists(input_path):
        logger.error(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    logger.info("="*80)
    logger.info("Phase 3: Gemini Knowledge Labeling Started")
    logger.info("="*80)
    logger.info(f"Lecture ID: {lecture_id}")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Top N: {args.top_n}")

    try:
        api_key = args.api_key or os.getenv("GEMINI_API_KEY")
        labeler = GeminiKnowledgeLabeler(api_key=api_key)
        logger.info(f"\nLabeling insight_spec_{lecture_id}.json...")
        labeled_spec = labeler.label_insight_spec(input_path, top_n=args.top_n)
        logger.info(f"\nSaving to {output_path}...")
        if labeler.save_insight_spec(labeled_spec, output_path):
            logger.info("\n" + "="*80)
            logger.info("✅ Phase 3: Gemini Knowledge Labeling Completed Successfully")
            logger.info("="*80)
            logger.info(f"Output file: {output_path}")
            return 0
        else:
            logger.error("Failed to save output file")
            return 1
    except Exception as e:
        logger.error(f"Error during labeling: {e}", exc_info=True)
        logger.error("="*80)
        logger.error("❌ Phase 3: Gemini Knowledge Labeling Failed")
        logger.error("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
