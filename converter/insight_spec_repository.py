"""
InsightSpecRepository - insight_spec JSON の I/O を担当

責務：
- insight_spec JSON の読み込み
- insight_spec JSON の保存
- ファイルパスの管理
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class InsightSpecRepository:
    """insight_spec JSON ファイルの読み書きを担当するリポジトリ"""

    def __init__(self, archive_dir: Optional[str] = None):
        """
        初期化

        Args:
            archive_dir (str, optional): アーカイブディレクトリパス
        """
        if archive_dir:
            self.archive_dir = Path(archive_dir)
        else:
            import os
            self.archive_dir = Path(os.getenv("ARCHIVE_OUTPUT_DIR", "./archive"))

        self.archive_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"✅ InsightSpecRepository を初期化（アーカイブ: {self.archive_dir}）")

    def _get_file_path(self, lecture_id: str) -> Path:
        """
        insight_spec ファイルパスを構築

        Args:
            lecture_id (str): 講座 ID（例: "01"）

        Returns:
            Path: ファイルパス
        """
        return self.archive_dir / f"insight_spec_{lecture_id}.json"

    def load(self, lecture_id: str) -> Dict[str, Any]:
        """
        insight_spec JSON を読み込む

        Args:
            lecture_id (str): 講座 ID

        Returns:
            Dict: insight_spec オブジェクト

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            json.JSONDecodeError: JSON パースに失敗した場合
        """
        file_path = self._get_file_path(lecture_id)

        if not file_path.exists():
            raise FileNotFoundError(f"❌ ファイルが見つかりません: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logging.info(f"✅ {file_path} を読み込みました")
            return data
        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON パースに失敗: {file_path} - {e}")
            raise

    def save(self, lecture_id: str, insight_spec: Dict[str, Any]) -> None:
        """
        insight_spec JSON を保存

        Args:
            lecture_id (str): 講座 ID
            insight_spec (Dict): insight_spec オブジェクト
        """
        file_path = self._get_file_path(lecture_id)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(insight_spec, f, ensure_ascii=False, indent=2)
            logging.info(f"✅ {file_path} に保存しました")
        except IOError as e:
            logging.error(f"❌ ファイル保存に失敗: {file_path} - {e}")
            raise

    def get_center_pins(self, lecture_id: str) -> list:
        """
        insight_spec から center_pins を取得

        Args:
            lecture_id (str): 講座 ID

        Returns:
            list: center_pins リスト
        """
        insight_spec = self.load(lecture_id)
        center_pins = insight_spec.get("knowledge_core", {}).get("center_pins", [])
        logging.info(f"📌 Lecture {lecture_id}: {len(center_pins)} 件の center_pins を取得")
        return center_pins

    def update_center_pins(self, lecture_id: str, center_pins: list) -> None:
        """
        insight_spec の center_pins を更新して保存

        Args:
            lecture_id (str): 講座 ID
            center_pins (list): 更新された center_pins リスト
        """
        insight_spec = self.load(lecture_id)
        insight_spec["knowledge_core"]["center_pins"] = center_pins
        self.save(lecture_id, insight_spec)
        logging.info(f"✅ Lecture {lecture_id}: {len(center_pins)} 件の center_pins を更新保存")
