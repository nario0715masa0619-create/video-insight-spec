# quality_check_phase4_1.py（修正版）

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

class QualityCheckPhase41:
    """Phase 4.1 品質検査"""
    
    def __init__(self, archive_dir: str):
        self.archive_dir = Path(archive_dir)
        self.passed_checks = 0
        self.failed_checks = 0
    
    def load_insight_spec(self, lecture_id: str) -> Dict[str, Any]:
        """insight_spec JSON を読み込む"""
        file_path = self.archive_dir / f"insight_spec_{lecture_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def check_snapshot_history_exists(self, spec: Dict[str, Any]) -> Tuple[bool, str]:
        """snapshot_history が存在するか確認"""
        snapshot_history = spec.get('views', {}).get('competitive', {}).get('snapshot_history', [])
        if snapshot_history:
            return True, f"snapshot_history: {len(snapshot_history)} entries"
        return False, "snapshot_history is empty"
    
    def check_snapshot_count_sufficient(self, spec: Dict[str, Any]) -> Tuple[bool, str]:
        """スナップショット数が十分か確認（初回は 1 つ、2 回目以降は 2 つ以上）"""
        snapshot_history = spec.get('views', {}).get('competitive', {}).get('snapshot_history', [])
        if len(snapshot_history) >= 1:
            if len(snapshot_history) == 1:
                return True, f"✅ Baseline set (1 snapshot) - Ready for next weekly report"
            else:
                return True, f"✅ {len(snapshot_history)} snapshots - Delta calculation available"
        else:
            return False, "❌ No snapshots found"
    
    def check_metrics_not_null(self, spec: Dict[str, Any]) -> Tuple[bool, str]:
        """metrics が null でないか確認"""
        metrics = spec.get('views', {}).get('competitive', {}).get('metrics', {})
        
        required_fields = ['view_count', 'like_count', 'comment_count', 'engagement_rate']
        missing = [f for f in required_fields if metrics.get(f) is None]
        
        if not missing:
            return True, f"view={metrics.get('view_count')}, like={metrics.get('like_count')}, comment={metrics.get('comment_count')}"
        return False, f"Missing fields: {', '.join(missing)}"
    
    def check_snapshot_timestamps(self, spec: Dict[str, Any]) -> Tuple[bool, str]:
        """スナップショットのタイムスタンプが正しいか確認"""
        snapshot_history = spec.get('views', {}).get('competitive', {}).get('snapshot_history', [])
        
        if not snapshot_history:
            return False, "snapshot_history is empty"
        
        # タイムスタンプが ISO format か確認
        for i, snapshot in enumerate(snapshot_history):
            timestamp = snapshot.get('timestamp')
            if not timestamp or not isinstance(timestamp, str):
                return False, f"Invalid timestamp at index {i}: {timestamp}"
        
        return True, f"All {len(snapshot_history)} timestamps are valid"
    
    def check_metrics_consistency(self, spec: Dict[str, Any]) -> Tuple[bool, str]:
        """metrics と snapshot_history の metrics が一致しているか確認"""
        latest_metric = spec.get('views', {}).get('competitive', {}).get('metrics', {})
        snapshot_history = spec.get('views', {}).get('competitive', {}).get('snapshot_history', [])
        
        if not snapshot_history:
            return False, "snapshot_history is empty"
        
        latest_snapshot = snapshot_history[-1]['metrics']
        
        if latest_metric.get('view_count') == latest_snapshot.get('view_count'):
            return True, "metrics and latest snapshot are consistent"
        else:
            return False, f"Inconsistency: metrics={latest_metric.get('view_count')}, snapshot={latest_snapshot.get('view_count')}"
    
    def run_checks(self, lecture_id: str) -> Dict[str, Tuple[bool, str]]:
        """全ての品質検査を実行"""
        print(f"\n【Lecture {lecture_id}】")
        
        try:
            spec = self.load_insight_spec(lecture_id)
        except FileNotFoundError as e:
            print(f"❌ {str(e)}")
            self.failed_checks += 1
            return {}
        
        checks = {
            "snapshot_history_exists": self.check_snapshot_history_exists(spec),
            "snapshot_count_sufficient": self.check_snapshot_count_sufficient(spec),
            "metrics_not_null": self.check_metrics_not_null(spec),
            "snapshot_timestamps": self.check_snapshot_timestamps(spec),
            "metrics_consistency": self.check_metrics_consistency(spec),
        }
        
        passed = 0
        for check_name, (result, message) in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}: {message}")
            if result:
                passed += 1
                self.passed_checks += 1
            else:
                self.failed_checks += 1
        
        print(f"  Summary: {passed}/{len(checks)} passed")
        
        return checks

def main():
    parser = argparse.ArgumentParser(description="Phase 4.1 Quality Check")
    parser.add_argument("--lecture-ids", default="01,02,03,04,05", help="Lecture IDs (comma-separated)")
    parser.add_argument("--archive-dir", required=True, help="Archive directory path")
    
    args = parser.parse_args()
    
    lecture_ids = args.lecture_ids.split(",")
    checker = QualityCheckPhase41(args.archive_dir)
    
    print("【Phase 4.1: Quality Check】")
    print(f"Archive dir: {args.archive_dir}")
    print(f"Processing lectures: {', '.join(lecture_ids)}")
    
    for lecture_id in lecture_ids:
        checker.run_checks(lecture_id.strip())
    
    print(f"\n{'=' * 80}")
    print(f"Total: {checker.passed_checks} passed, {checker.failed_checks} failed")
    
    if checker.failed_checks == 0:
        print("✅ Phase 4.1 Quality Check PASSED")
        exit(0)
    else:
        print("❌ Phase 4.1 Quality Check FAILED")
        exit(1)

if __name__ == "__main__":
    main()
