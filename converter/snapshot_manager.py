# converter/snapshot_manager.py

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class SnapshotManager:
    """スナップショット履歴を管理"""
    
    def __init__(self, archive_dir: str):
        self.archive_dir = Path(archive_dir)
    
    def load_insight_spec(self, lecture_id: str) -> Dict[str, Any]:
        """insight_spec JSON を読み込む"""
        file_path = self.archive_dir / f"insight_spec_{lecture_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_insight_spec(self, lecture_id: str, spec: Dict[str, Any]) -> None:
        """insight_spec JSON を保存"""
        file_path = self.archive_dir / f"insight_spec_{lecture_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
    
    def get_snapshot_history(self, insight_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """snapshot_history を取得"""
        return insight_spec.get('views', {}).get('competitive', {}).get('snapshot_history', [])
    
    def add_snapshot(self, lecture_id: str, metrics: Dict[str, Any], timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        新しいスナップショットを追加
        
        Args:
            lecture_id: 講座 ID
            metrics: メトリクス（view_count, like_count, comment_count など）
            timestamp: タイムスタンプ（デフォルト: 現在時刻）
        
        Returns:
            追加されたスナップショット
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        spec = self.load_insight_spec(lecture_id)
        
        # snapshot_history を初期化（存在しない場合）
        if 'views' not in spec:
            spec['views'] = {}
        if 'competitive' not in spec['views']:
            spec['views']['competitive'] = {}
        if 'snapshot_history' not in spec['views']['competitive']:
            spec['views']['competitive']['snapshot_history'] = []
        
        snapshot = {
            "timestamp": timestamp,
            "metrics": metrics
        }
        
        spec['views']['competitive']['snapshot_history'].append(snapshot)
        
        self.save_insight_spec(lecture_id, spec)
        
        return snapshot
    
    def get_latest_snapshot(self, insight_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """最新のスナップショットを取得"""
        snapshot_history = self.get_snapshot_history(insight_spec)
        if snapshot_history:
            return snapshot_history[-1]
        return None
    
    def get_previous_snapshot(self, insight_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """前回のスナップショットを取得"""
        snapshot_history = self.get_snapshot_history(insight_spec)
        if len(snapshot_history) >= 2:
            return snapshot_history[-2]
        return None
    
    def get_snapshot_by_timestamp(self, insight_spec: Dict[str, Any], timestamp: str) -> Optional[Dict[str, Any]]:
        """指定タイムスタンプのスナップショットを取得"""
        snapshot_history = self.get_snapshot_history(insight_spec)
        for snapshot in snapshot_history:
            if snapshot['timestamp'] == timestamp:
                return snapshot
        return None
    
    def get_snapshot_count(self, insight_spec: Dict[str, Any]) -> int:
        """スナップショット数を取得"""
        snapshot_history = self.get_snapshot_history(insight_spec)
        return len(snapshot_history)
