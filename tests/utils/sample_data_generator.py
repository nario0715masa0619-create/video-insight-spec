"""
将来用：lecture_id 02, 03 等のダミー JSON/DB を自動生成する utility スクリプト。
Phase 2.0 では未実装。スケルトン提供。
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional


class SampleDataGenerator:
    """ダミーサンプルデータを生成（lecture_id 拡張用）"""
    
    @staticmethod
    def generate_core_json(
        lecture_id: str,
        num_elements: int = 10,
        output_dir: Optional[str] = None
    ) -> str:
        """
        ダミー Mk2_Core_XX.json を生成
        
        Args:
            lecture_id: 講座ID（例: "02"）
            num_elements: 生成する center_pins 数
            output_dir: 出力ディレクトリ（デフォルト: カレント）
        
        Returns:
            生成されたファイルパス
        
        将来実装:
        - element_id を "elem_{lecture_id}_{index}" として生成
        - type を FACT/LOGIC/SOP/CASE にランダム割当
        - purity_score を 60-100 の範囲でランダム生成
        - 複数の content テンプレートを用意
        """
        raise NotImplementedError("Phase 2 にて実装予定")
    
    @staticmethod
    def generate_sidecar_db(
        lecture_id: str,
        num_records: int = 20,
        duration_sec: int = 3600,
        output_dir: Optional[str] = None
    ) -> str:
        """
        ダミー Mk2_Sidecar_XX.db を生成
        
        Args:
            lecture_id: 講座ID（例: "02"）
            num_records: 生成する evidence_index レコード数
            duration_sec: 動画総長（秒）
            output_dir: 出力ディレクトリ
        
        Returns:
            生成されたファイルパス
        
        将来実装:
        - evidence_index テーブルを作成
        - start_ms / end_ms を duration_sec に応じて均等配置
        - visual_text のテンプレートを複数用意
        - visual_score を 0.5-1.0 の範囲で生成
        """
        raise NotImplementedError("Phase 2 にて実装予定")
    
    @staticmethod
    def generate_pair(
        lecture_id: str,
        num_elements: int = 10,
        num_records: int = 20,
        output_dir: Optional[str] = None
    ) -> tuple[str, str]:
        """
        JSON + DB のペアを同時生成
        
        Returns:
            (json_path, db_path)
        """
        raise NotImplementedError("Phase 2 にて実装予定")


if __name__ == "__main__":
    # 使用例（未実装）
    # json_path, db_path = SampleDataGenerator.generate_pair(
    #     lecture_id="02",
    #     output_dir="./test_samples"
    # )
    # print(f"Generated: {json_path}, {db_path}")
    pass
