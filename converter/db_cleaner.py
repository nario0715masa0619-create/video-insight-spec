import sqlite3
import pathlib
import logging
from typing import Dict
from converter.ocr_text_cleaner import OCRTextCleaner

logger = logging.getLogger(__name__)


class SidecarDBCleaner:
    """Mk2_Sidecar_XX.db の visual_text をクリーニング"""
    
    @staticmethod
    def clean_db(db_path: str, backup: bool = True) -> Dict:
        """
        evidence_index テーブルの visual_text をクリーニング
        
        Args:
            db_path: Mk2_Sidecar_XX.db のパス
            backup: バックアップを作成するか
            
        Returns:
            クリーニング結果の統計
        """
        db_path = pathlib.Path(db_path)
        
        # バックアップ作成
        if backup:
            backup_path = db_path.with_suffix(".db.backup")
            import shutil
            shutil.copy(db_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 全レコードを取得
        cursor.execute("SELECT element_id, visual_text FROM evidence_index")
        rows = cursor.fetchall()
        
        stats = {
            "total_records": len(rows),
            "cleaned_records": 0,
            "total_reduction_chars": 0,
            "avg_reduction_ratio": 0.0,
        }
        
        reduction_ratios = []
        
        # 各レコードをクリーニング
        for element_id, visual_text in rows:
            cleaned, metadata = OCRTextCleaner.clean(visual_text)
            
            # DB を更新
            cursor.execute(
                "UPDATE evidence_index SET visual_text = ? WHERE element_id = ?",
                (cleaned, element_id)
            )
            
            stats["cleaned_records"] += 1
            stats["total_reduction_chars"] += metadata["reduction_ratio"]
            reduction_ratios.append(metadata["reduction_ratio"])
        
        # 統計を計算
        if reduction_ratios:
            stats["avg_reduction_ratio"] = round(sum(reduction_ratios) / len(reduction_ratios), 2)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaning complete: {stats}")
        return stats
