"""
InsightSpecRepository - insight_spec JSON ファイルの I/O

責務：
- insight_spec JSON ファイルの読み込み・保存
- center_pins の取得・更新
- ファイルパス管理
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class InsightSpecLoadError(Exception):
    """insight_spec JSON 読み込みエラー"""
    pass


class InsightSpecSaveError(Exception):
    """insight_spec JSON 保存エラー"""
    pass


class InsightSpecRepository:
    """insight_spec JSON ファイルの I/O を担当するリポジトリクラス"""
    
    def __init__(self, archive_dir: str):
        """
        コンストラクタ
        
        Args:
            archive_dir (str): アーカイブディレクトリパス
        """
        self.archive_dir = Path(archive_dir)
        if not self.archive_dir.exists():
            raise ValueError(f"❌ Archive directory not found: {self.archive_dir}")
        logger.info(f"✅ InsightSpecRepository を初期化（アーカイブ: {self.archive_dir}）")

    def _get_file_path(self, lecture_id: str) -> Path:
        """insight_spec ファイルのパスを生成"""
        return self.archive_dir / f"insight_spec_{lecture_id}.json"

    def load(self, lecture_id: str) -> Dict[str, Any]:
        """
        insight_spec JSON ファイルを読み込む
        
        Args:
            lecture_id (str): Lecture ID (e.g., '01')
            
        Returns:
            Dict[str, Any]: insight_spec のデータ
            
        Raises:
            InsightSpecLoadError: ファイルが見つからないか、JSON パースエラー
        """
        file_path = self._get_file_path(lecture_id)
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ {file_path} を読み込みました")
            return data
        except FileNotFoundError as e:
            raise InsightSpecLoadError(f"File not found: {file_path}") from e
        except json.JSONDecodeError as e:
            raise InsightSpecLoadError(f"JSON parse error in {file_path}: {e}") from e
        except Exception as e:
            raise InsightSpecLoadError(f"Error loading {file_path}: {e}") from e

    def save(self, lecture_id: str, data: Dict[str, Any]) -> None:
        """
        insight_spec JSON ファイルに保存
        
        Args:
            lecture_id (str): Lecture ID
            data (Dict[str, Any]): 保存するデータ
            
        Raises:
            InsightSpecSaveError: 保存エラー
        """
        file_path = self._get_file_path(lecture_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ {file_path} に保存しました")
        except Exception as e:
            raise InsightSpecSaveError(f"Error saving {file_path}: {e}") from e

    def get_center_pins(self, lecture_id: str) -> List[Dict[str, Any]]:
        """
        center_pins を取得
        
        実際のスキーマ: data['knowledge_core']['center_pins']
        
        Args:
            lecture_id (str): Lecture ID
            
        Returns:
            List[Dict[str, Any]]: center_pins リスト
            
        Raises:
            InsightSpecLoadError: ファイル読み込みエラー
        """
        data = self.load(lecture_id)
        
        # スキーマ検証: knowledge_core.center_pins
        if 'knowledge_core' not in data:
            raise InsightSpecLoadError(f"'knowledge_core' not found in {lecture_id}")
        
        knowledge_core = data['knowledge_core']
        if not isinstance(knowledge_core, dict):
            raise InsightSpecLoadError(f"'knowledge_core' is not a dict in {lecture_id}")
        
        center_pins = knowledge_core.get('center_pins', [])
        if not isinstance(center_pins, list):
            raise InsightSpecLoadError(f"'center_pins' is not a list in {lecture_id}")
        
        logger.info(f"📌 Lecture {lecture_id}: {len(center_pins)} 件の center_pins を取得")
        return center_pins

    def update_center_pins(self, lecture_id: str, center_pins: List[Dict[str, Any]]) -> None:
        """
        center_pins を更新して保存
        
        Args:
            lecture_id (str): Lecture ID
            center_pins (List[Dict[str, Any]]): 更新後の center_pins リスト
            
        Raises:
            InsightSpecLoadError: ファイル読み込みエラー
            InsightSpecSaveError: 保存エラー
        """
        if not isinstance(center_pins, list):
            raise ValueError("center_pins must be a list")
        
        # 既存ファイルを読み込む
        data = self.load(lecture_id)
        
        # knowledge_core.center_pins を更新
        if 'knowledge_core' not in data:
            data['knowledge_core'] = {}
        
        data['knowledge_core']['center_pins'] = center_pins
        
        # 保存
        self.save(lecture_id, data)
        logger.info(f"✅ Lecture {lecture_id}: {len(center_pins)} 件の center_pins を更新保存")
