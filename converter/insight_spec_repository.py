"""
InsightSpecRepository - insight_spec JSON の I/O と video_meta 更新

責務:
- insight_spec JSON ファイルの読み込み・保存
- video_meta の更新
- エラーハンドリング
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

class InsightSpecLoadError(Exception):
    pass

class InsightSpecSaveError(Exception):
    pass

class InsightSpecRepository:
    def __init__(self, archive_dir: str):
        self.archive_dir = Path(archive_dir)
        self.logger = logging.getLogger(__name__)
        
        if not self.archive_dir.exists():
            raise ValueError(f"❌ アーカイブディレクトリが存在しません: {self.archive_dir}")
        
        self.logger.info(f"✅ InsightSpecRepository を初期化しました: {self.archive_dir}")
    
    def _get_file_path(self, lecture_id: str) -> Path:
        """insight_spec ファイルパスを構築"""
        return self.archive_dir / f"insight_spec_{lecture_id}.json"
    
    def load(self, lecture_id: str) -> Dict[str, Any]:
        """insight_spec JSON を読み込み"""
        file_path = self._get_file_path(lecture_id)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"✅ {file_path} を読み込みました")
            return data
        except FileNotFoundError:
            raise InsightSpecLoadError(f"❌ ファイルが見つかりません: {file_path}")
        except json.JSONDecodeError as e:
            raise InsightSpecLoadError(f"❌ JSON デコードエラー: {file_path}: {e}")
    
    def save(self, lecture_id: str, data: Dict[str, Any]) -> Path:
        """insight_spec JSON を保存"""
        file_path = self._get_file_path(lecture_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"✅ {file_path} を保存しました")
            return file_path
        except Exception as e:
            raise InsightSpecSaveError(f"❌ ファイル保存エラー: {file_path}: {e}")
    
    def get_center_pins(self, lecture_id: str) -> list:
        """center_pins を取得"""
        data = self.load(lecture_id)
        center_pins = data.get('knowledge_core', {}).get('center_pins', [])
        return center_pins
    
    def update_center_pins(self, lecture_id: str, center_pins: list) -> Path:
        """center_pins を更新して保存"""
        data = self.load(lecture_id)
        if 'knowledge_core' not in data:
            data['knowledge_core'] = {}
        data['knowledge_core']['center_pins'] = center_pins
        return self.save(lecture_id, data)
    
    def update_video_meta(self, lecture_id: str, video_meta: Dict[str, Any]) -> Path:
        """video_meta を更新して保存"""
        data = self.load(lecture_id)
        data['video_meta'] = video_meta
        self.logger.info(f"✅ Lecture {lecture_id} の video_meta を更新しました")
        return self.save(lecture_id, data)
    
    def get_video_meta(self, lecture_id: str) -> Dict[str, Any]:
        """video_meta を取得"""
        data = self.load(lecture_id)
        return data.get('video_meta', {})
