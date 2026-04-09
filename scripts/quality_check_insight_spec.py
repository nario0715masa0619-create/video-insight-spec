#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
insight_spec JSON の品質チェック統合スクリプト
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class InsightSpecQualityChecker:
    """insight_spec JSON の品質検査"""
    
    def __init__(self, archive_dir):
        self.archive_dir = Path(archive_dir)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "archive_dir": str(self.archive_dir),
            "files": [],
            "summary": {
                "total_files": 0,
                "passed": 0,
                "failed": 0,
                "average_purity_score": 0.0,
                "total_center_pins": 0
            }
        }
    
    def check_file(self, file_path):
        """単一ファイルの品質チェック"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_result = {
                "filename": file_path.name,
                "path": str(file_path),
                "checks": {},
                "metrics": {}
            }
            
            # 1. 基本構造チェック
            has_video_meta = "video_meta" in data
            has_knowledge_core = "knowledge_core" in data
            file_result["checks"]["structure"] = has_video_meta and has_knowledge_core
            
            # 2. video_meta チェック
            video_meta = data.get("video_meta", {})
            video_id = video_meta.get("video_id")
            file_result["checks"]["has_video_id"] = bool(video_id)
            file_result["metrics"]["video_id"] = video_id
            
            # 3. center_pins チェック
            center_pins = data.get("knowledge_core", {}).get("center_pins", [])
            file_result["checks"]["has_center_pins"] = len(center_pins) > 0
            file_result["metrics"]["center_pins_count"] = len(center_pins)
            
            # 4. Purity Score 統計
            scores = [cp.get("base_purity_score", 0) for cp in center_pins]
            if scores:
                avg_score = sum(scores) / len(scores)
                file_result["metrics"]["purity_score_avg"] = round(avg_score, 2)
                file_result["metrics"]["purity_score_min"] = min(scores)
                file_result["metrics"]["purity_score_max"] = max(scores)
                file_result["checks"]["purity_score_quality"] = avg_score >= 80
            
            # 5. ラベリング チェック
            labeled_count = sum(1 for cp in center_pins if cp.get("labels"))
            file_result["checks"]["all_labeled"] = labeled_count == len(center_pins)
            file_result["metrics"]["labeled_count"] = labeled_count
            
            # 6. ビジネステーマ分布
            themes = {}
            for cp in center_pins:
                biz_themes = cp.get("labels", {}).get("business_theme", [])
                for theme in biz_themes:
                    themes[theme] = themes.get(theme, 0) + 1
            file_result["metrics"]["business_themes"] = themes
            
            # 総合判定
            all_checks_passed = all(file_result["checks"].values())
            file_result["status"] = "PASS" if all_checks_passed else "FAIL"
            
            logger.info(f"✅ {file_path.name}: {file_result['status']}")
            logger.info(f"   - center_pins: {len(center_pins)}, Purity Avg: {file_result['metrics'].get('purity_score_avg', 'N/A')}")
            
            return file_result
        
        except Exception as e:
            logger.error(f"❌ {file_path.name}: {str(e)}")
            return {
                "filename": file_path.name,
                "status": "ERROR",
                "error": str(e)
            }
    
    def run(self):
        """全ファイルの品質チェック実行"""
        logger.info("=" * 70)
        logger.info("【insight_spec JSON 品質チェック開始】")
        logger.info("=" * 70)
        
        # insight_spec_*.json を全て検出
        insight_files = list(self.archive_dir.glob("insight_spec_*.json"))
        
        if not insight_files:
            logger.warning("⚠️ insight_spec_*.json ファイルが見つかりません")
            return self.results
        
        logger.info(f"📋 検出ファイル数: {len(insight_files)}")
        
        # 各ファイルをチェック
        for file_path in sorted(insight_files):
            result = self.check_file(file_path)
            self.results["files"].append(result)
            
            if result.get("status") == "PASS":
                self.results["summary"]["passed"] += 1
            else:
                self.results["summary"]["failed"] += 1
        
        # サマリー集計
        self.results["summary"]["total_files"] = len(insight_files)
        
        all_scores = []
        for file_result in self.results["files"]:
            if "purity_score_avg" in file_result.get("metrics", {}):
                all_scores.append(file_result["metrics"]["purity_score_avg"])
            if "center_pins_count" in file_result.get("metrics", {}):
                self.results["summary"]["total_center_pins"] += file_result["metrics"]["center_pins_count"]
        
        if all_scores:
            self.results["summary"]["average_purity_score"] = round(sum(all_scores) / len(all_scores), 2)
        
        # 結果表示
        self._print_summary()
        
        return self.results
    
    def _print_summary(self):
        """結果サマリーを表示"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("【チェック結果サマリー】")
        logger.info("=" * 70)
        
        summary = self.results["summary"]
        logger.info(f"✅ 成功: {summary['passed']}/{summary['total_files']}")
        logger.info(f"❌ 失敗: {summary['failed']}/{summary['total_files']}")
        logger.info(f"📊 総 center_pins 数: {summary['total_center_pins']}")
        logger.info(f"⭐ 平均 Purity Score: {summary['average_purity_score']}/100")
        
        if summary['failed'] == 0 and summary['average_purity_score'] >= 85:
            logger.info("🎉 品質判定: EXCELLENT")
        elif summary['failed'] == 0 and summary['average_purity_score'] >= 75:
            logger.info("✅ 品質判定: GOOD")
        else:
            logger.info("⚠️ 品質判定: NEEDS IMPROVEMENT")
        
        logger.info("=" * 70)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='insight_spec JSON 品質チェック')
    parser.add_argument('--archive-dir', 
                       default=r'D:\AI_Data\video-insight-spec\archive',
                       help='archive ディレクトリパス')
    parser.add_argument('--output-json',
                       default='quality_check_results.json',
                       help='結果出力 JSON ファイル')
    
    args = parser.parse_args()
    
    checker = InsightSpecQualityChecker(args.archive_dir)
    results = checker.run()
    
    # 結果を JSON に保存
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ 結果を保存: {args.output_json}")

if __name__ == '__main__':
    main()
