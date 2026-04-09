#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Pipeline Full (Modified): 既存 MP4 から処理開始
フロー:
  0. 既存 MP4 を VIDEOS_INPUT_DIR にコピー
  1. master_batch_refiner.py (MP4 → Mk2_Core + Mk2_Sidecar)
  2. convert_to_insight_spec_phase1.py (Mk2 → insight_spec)
  3. generate_video_mapping.py (ファイル → video_mapping.csv)
  4. enrich_insight_spec_with_youtube_metadata.py (API → YouTube メタデータ追加)
  5. expand_insight_spec_with_gemini.py (Gemini ラベル付与)
  6. quality_check_phase4.py (検査)
"""

import os
import sys
import subprocess
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# ========== ログ設定 ==========
load_dotenv()
LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
os.makedirs(LOGS_DIR, exist_ok=True)

log_file = os.path.join(LOGS_DIR, f"youtube_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ========== パイプライン実行 ==========
def run_command(cmd, description):
    """コマンド実行（エラーハンドリング付き）"""
    logger.info(f"\n{'='*60}")
    logger.info(f"📌 ステップ: {description}")
    logger.info(f"{'='*60}")
    logger.info(f"実行: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=True)
        logger.info(f"✅ {description} 完了")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} 失敗: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} エラー: {e}")
        return False

def copy_existing_videos():
    """既存 MP4 を VIDEOS_INPUT_DIR にコピー"""
    logger.info(f"\n{'='*60}")
    logger.info("📌 ステップ 0: 既存 MP4 ファイルを準備中")
    logger.info(f"{'='*60}")
    
    videos_input_dir = os.getenv("VIDEOS_INPUT_DIR", r"D:\AI_Data\video-insight-spec\downloaded_videos")
    source_root = Path(videos_input_dir)
    
    # mirirepi フォルダから MP4 をコピー
    mirirepi_dir = source_root / "mirirepi"
    if mirirepi_dir.exists():
        mp4_files = list(mirirepi_dir.glob("*.mp4"))
        logger.info(f"✅ {len(mp4_files)} 個の MP4 ファイルを検出 (mirirepi フォルダ)")
        
        # ファイルを VIDEOS_INPUT_DIR の直下にコピー（ファイル名の重複を避ける）
        copied_count = 0
        for mp4_file in mp4_files:
            dest_file = source_root / f"mirirepi_{mp4_file.name}"
            if not dest_file.exists():
                shutil.copy2(mp4_file, dest_file)
                logger.info(f"  📋 コピー: {mp4_file.name} → {dest_file.name}")
                copied_count += 1
        
        logger.info(f"✅ {copied_count} 個のファイルをコピーしました")
        return True
    else:
        logger.warning(f"⚠️ mirirepi フォルダが見つかりません: {mirirepi_dir}")
        return False

def main():
    logger.info("="*60)
    logger.info("🚀 YouTube Pipeline Full (既存 MP4 から処理)")
    logger.info("="*60)
    
    start_time = datetime.now()
    results = {
        "started_at": start_time.isoformat(),
        "steps": {}
    }
    
    # ========== ステップ 0: MP4 準備 ==========
    prep_success = copy_existing_videos()
    results["steps"]["step0_prepare_videos"] = "✅ 完了" if prep_success else "❌ 失敗"
    
    if not prep_success:
        logger.warning("⚠️ MP4 ファイルが見つかりませんが処理を続行します")
    
    # ========== ステップ 1: Mk2 処理 ==========
    step1_success = run_command(
        ["python", "scripts/master_batch_refiner.py", "D:\AI_Data\video-insight-spec\downloaded_videos\mirirepi"],
        "Step 1: MP4 → Mk2_Core + Mk2_Sidecar DB 生成"
    )
    results["steps"]["step1_mk2_processing"] = "✅ 完了" if step1_success else "❌ 失敗"
    
    if not step1_success:
        logger.warning("⚠️ Mk2 処理が失敗しましたが、次のステップに進みます")
    
    # ========== ステップ 2: Phase 1 変換 ==========
    logger.info("\n✅ Step 2: Mk2_Core + Mk2_Sidecar → insight_spec 変換")
    archive_dir = os.getenv("ARCHIVE_OUTPUT_DIR", r"D:\AI_Data\video-insight-spec\archive")
    os.makedirs(archive_dir, exist_ok=True)
    
    mirirepi_archive_dir = Path(archive_dir) / "mirirepi"
    core_files = sorted(mirirepi_archive_dir.glob("Mk2_Core_*.json"))
    
    if core_files:
        phase1_success = True
        for core_file in core_files:
            lecture_id = core_file.stem.replace("Mk2_Core_", "")
            sidecar_db = Path(archive_dir) / f"Mk2_Sidecar_{lecture_id}.db"
            
            if sidecar_db.exists():
                success = run_command(
                    ["python", "scripts/convert_to_insight_spec_phase1.py",
                     "--lecture-id", lecture_id,
                     "--core-json", str(core_file),
                     "--sidecar-db", str(sidecar_db)],
                    f"Phase 1: Lecture {lecture_id}"
                )
                phase1_success = phase1_success and success
            else:
                logger.warning(f"Sidecar DB が見つかりません: {sidecar_db}")
                phase1_success = False
        
        results["steps"]["step2_phase1_conversion"] = "✅ 完了" if phase1_success else "❌ 失敗"
    else:
        logger.warning("Mk2_Core_*.json ファイルが見つかりません")
        results["steps"]["step2_phase1_conversion"] = "⏭️ スキップ"
    
    # ========== ステップ 3: Video Mapping 生成 ==========
    step3_success = run_command(
        ["python", "scripts/generate_video_mapping.py"],
        "Step 3: video_mapping.csv 生成（YouTube API で検索）"
    )
    results["steps"]["step3_video_mapping"] = "✅ 完了" if step3_success else "❌ 失敗"
    
    # ========== ステップ 4: YouTube メタデータ追加 ==========
    if step3_success:
        step4_success = run_command(
            ["python", "scripts/enrich_insight_spec_with_youtube_metadata.py"],
            "Step 4: YouTube メタデータ追加（views セクション拡張）"
        )
        results["steps"]["step4_youtube_enrichment"] = "✅ 完了" if step4_success else "❌ 失敗"
    else:
        logger.warning("video_mapping.csv が生成されていないため、Step 4 をスキップ")
        results["steps"]["step4_youtube_enrichment"] = "⏭️ スキップ"
    
    # ========== ステップ 5: Gemini ラベル付与 ==========
    gemini_success = True
    insight_files = sorted(Path(archive_dir).glob("insight_spec_*.json"))
    
    if insight_files:
        for insight_file in insight_files:
            lecture_id = insight_file.stem.replace("insight_spec_", "")
            success = run_command(
                ["python", "scripts/expand_insight_spec_with_gemini.py",
                 "--lecture-id", lecture_id,
                 "--archive-dir", archive_dir],
                f"Step 5: Gemini ラベル付与 (Lecture {lecture_id})"
            )
            gemini_success = gemini_success and success
        
        results["steps"]["step5_gemini_labeling"] = "✅ 完了" if gemini_success else "❌ 失敗"
    else:
        logger.warning("insight_spec_*.json ファイルが見つかりません")
        results["steps"]["step5_gemini_labeling"] = "⏭️ スキップ"
    
    # ========== ステップ 6: 品質検査 ==========
    step6_success = run_command(
        ["python", "scripts/quality_check_phase4.py"],
        "Step 6: 品質検査 (Phase 4)"
    )
    results["steps"]["step6_quality_check"] = "✅ 完了" if step6_success else "❌ 失敗"
    
    # ========== 結果保存 ==========
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    results["completed_at"] = end_time.isoformat()
    results["duration_seconds"] = duration
    
    results_file = os.path.join(LOGS_DIR, f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info("\n" + "="*60)
    logger.info("✅ パイプライン完了")
    logger.info("="*60)
    logger.info(f"実行時間: {duration:.1f} 秒")
    logger.info(f"ログファイル: {log_file}")
    logger.info(f"結果ファイル: {results_file}")
    logger.info(f"アーカイブ: {archive_dir}")
    logger.info("="*60)
    
    return True

if __name__ == "__main__":
    main()






