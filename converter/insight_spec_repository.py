"""
InsightSpecRepository - ファイル I/O 層

責務：
- insight_spec JSON の読み込み・保存
- ファイルパスの管理
- center_pins の取得・更新メソッド

このクラスはファイル I/O と JSON 構造検証のみを担当します。
ビジネスロジック（ラベル付与など）は含まれません。
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class InsightSpecLoadError(Exception):
    """insight_spec ロードエラー"""
    pass


class InsightSpecSaveError(Exception):
    """insight_spec セーブエラー"""
    pass


class InsightSpecRepository:
    """ファイル I/O 層: insight_spec JSON ファイルの読み書きを担当する"""

    def __init__(self, archive_dir: Optional[str] = None):
        """
        初期化

        Args:
            archive_dir (str, optional): アーカイブディレクトリパス
                指定されない場合は環境変数 ARCHIVE_OUTPUT_DIR から取得
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
            lecture_id (str): 講座 ID（例: "01"）

        Returns:
            Dict: insight_spec オブジェクト

        Raises:
            InsightSpecLoadError: ファイルが見つからない、JSON パースに失敗した場合
        """
        file_path = self._get_file_path(lecture_id)

        if not file_path.exists():
            error_msg = f"❌ ファイルが見つかりません: {file_path}"
            logging.error(error_msg)
            raise InsightSpecLoadError(error_msg)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logging.info(f"✅ {file_path} を読み込みました")
            return data
        except json.JSONDecodeError as e:
            error_msg = f"❌ JSON パースに失敗: {file_path} - {e}"
            logging.error(error_msg)
            raise InsightSpecLoadError(error_msg) from e
        except IOError as e:
            error_msg = f"❌ ファイル読み込みエラー: {file_path} - {e}"
            logging.error(error_msg)
            raise InsightSpecLoadError(error_msg) from e

    def save(self, lecture_id: str, insight_spec: Dict[str, Any]) -> None:
        """
        insight_spec JSON を保存

        Args:
            lecture_id (str): 講座 ID（例: "01"）
            insight_spec (Dict): insight_spec オブジェクト

        Raises:
            InsightSpecSaveError: ファイル保存に失敗した場合
        """
        file_path = self._get_file_path(lecture_id)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(insight_spec, f, ensure_ascii=False, indent=2)
            logging.info(f"✅ {file_path} に保存しました")
        except IOError as e:
            error_msg = f"❌ ファイル保存に失敗: {file_path} - {e}"
            logging.error(error_msg)
            raise InsightSpecSaveError(error_msg) from e

    def get_center_pins(self, lecture_id: str) -> list:
        """
        insight_spec から center_pins を取得

        Args:
            lecture_id (str): 講座 ID（例: "01"）

        Returns:
            list: center_pins リスト

        Raises:
            InsightSpecLoadError: ファイルロード失敗時
            ValueError: knowledge_core.center_pins が見つからない場合
        """
        insight_spec = self.load(lecture_id)
        
        try:
            center_pins = insight_spec["knowledge_core"]["center_pins"]
            if not isinstance(center_pins, list):
                raise ValueError("center_pins は list である必要があります")
            logging.info(f"📌 Lecture {lecture_id}: {len(center_pins)} 件の center_pins を取得")
            return center_pins
        except (KeyError, TypeError) as e:
            error_msg = f"❌ center_pins の取得に失敗: {lecture_id} - {e}"
            logging.error(error_msg)
            raise ValueError(error_msg) from e

    def update_center_pins(self, lecture_id: str, center_pins: list) -> None:
        """
        insight_spec の center_pins を更新して保存

        Args:
            lecture_id (str): 講座 ID（例: "01"）
            center_pins (list): 更新された center_pins リスト

        Raises:
            InsightSpecLoadError: ロード失敗時
            InsightSpecSaveError: セーブ失敗時
            ValueError: center_pins が list でない場合
        """
        if not isinstance(center_pins, list):
            raise ValueError("center_pins は list である必要があります")

        insight_spec = self.load(lecture_id)
        insight_spec["knowledge_core"]["center_pins"] = center_pins
        self.save(lecture_id, insight_spec)
        logging.info(f"✅ Lecture {lecture_id}: {len(center_pins)} 件の center_pins を更新保存")
