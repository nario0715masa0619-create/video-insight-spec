#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3: Label insight_spec_XX.json with Gemini Knowledge
各 center_pin にビジネステーマ・ファネルステージ・難易度のラベルを自動付与

【責務分離設計】
- GeminiLLMClient: Gemini API 呼び出し・リトライ・JSON パース
- CenterPinLabelingService: center_pin ラベル付与ロジック
- InsightSpecRepository: insight_spec JSON ファイル I/O
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

from converter.gemini_llm_client import GeminiLLMClient
from converter.center_pin_labeling_service import CenterPinLabelingService
from converter.insight_spec_repository import InsightSpecRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()


def main():
    """Phase 3: Gemini Knowledge Labeling (New Class-Based Design)"""
    parser = argparse.ArgumentParser(
        description="Label insight_spec_XX.json with Gemini Knowledge (Phase 3)"
    )
    parser.add_argument(
        "--lecture-id",
        type=str,
        required=True,
        help="Lecture ID (e.g., '01')"
    )
    parser.add_argument(
        "--archive-dir",
        type=str,
        default=None,
        help="Archive directory containing insight_spec files (uses ARCHIVE_OUTPUT_DIR from .env if not specified)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=None,
        help="Number of top center_pins to label (default: all)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Gemini API key (from .env if not specified)"
    )
    args = parser.parse_args()

    lecture_id = args.lecture_id
    # ARCHIVE_OUTPUT_DIR を優先、なければ引数、なければデフォルト
    archive_dir = args.archive_dir or os.getenv("ARCHIVE_OUTPUT_DIR", r"D:\Knowledge_Base\Brain_Marketing\archive")

    # ============================================================================
    # STEP 1: Initialize Components
    # ============================================================================
    logger.info("=" * 80)
    logger.info("Phase 3: Gemini Knowledge Labeling Started (New Design)")
    logger.info("=" * 80)
    logger.info(f"Lecture ID: {lecture_id}")
    logger.info(f"Archive Dir: {archive_dir}")
    logger.info(f"Top N: {args.top_n if args.top_n else 'All'}")

    try:
        # Initialize GeminiLLMClient
        api_key = args.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found in environment or arguments")
            return 1

        logger.info("\n[Step 1] Initializing GeminiLLMClient...")
        llm_client = GeminiLLMClient(api_key=api_key)
        logger.info("✅ GeminiLLMClient initialized")

        # Initialize InsightSpecRepository
        logger.info("[Step 2] Initializing InsightSpecRepository...")
        repository = InsightSpecRepository(archive_dir=archive_dir)
        logger.info("✅ InsightSpecRepository initialized")

        # Initialize CenterPinLabelingService with injected LLM client
        logger.info("[Step 3] Initializing CenterPinLabelingService...")
        labeling_service = CenterPinLabelingService(llm_client=llm_client)
        logger.info("✅ CenterPinLabelingService initialized")

        # ====================================================================
        # STEP 2: Load insight_spec
        # ====================================================================
        logger.info(f"\n[Step 4] Loading insight_spec_{lecture_id}.json...")
        center_pins = repository.get_center_pins(lecture_id)
        logger.info(f"✅ Loaded {len(center_pins)} center_pins")

        # ====================================================================
        # STEP 3: Label center_pins
        # ====================================================================
        logger.info(f"\n[Step 5] Labeling center_pins (top_n={args.top_n})...")
        labeled_pins = labeling_service.label_center_pins(
            center_pins,
            top_n=args.top_n
        )
        logger.info(f"✅ Labeling completed")

        # ====================================================================
        # STEP 4: Save labeled insight_spec
        # ====================================================================
        logger.info(f"\n[Step 6] Saving labeled insight_spec_{lecture_id}.json...")
        repository.update_center_pins(lecture_id, labeled_pins)
        logger.info(f"✅ Saved {len(labeled_pins)} labeled center_pins")

        # ====================================================================
        # SUCCESS
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("✅ Phase 3: Gemini Knowledge Labeling Completed Successfully")
        logger.info("=" * 80)
        logger.info(f"Output: {repository._get_file_path(lecture_id)}")
        return 0

    except ImportError as e:
        logger.error(f"❌ Import error: {e}", exc_info=True)
        logger.error("Make sure converter modules are available")
        return 1

    except Exception as e:
        logger.error(f"❌ Error during labeling: {e}", exc_info=True)
        logger.error("=" * 80)
        logger.error("❌ Phase 3: Gemini Knowledge Labeling Failed")
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
