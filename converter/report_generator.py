# converter/report_generator.py

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from converter.html_formatter import HTMLFormatter
from converter.text_formatter import TextFormatter


class ReportGenerator:
    """HTML/Text レポート生成メインクラス"""

    @staticmethod
    def generate(json_file_path: str, output_dir: str = "reports") -> Dict[str, str]:
        """
        JSON ファイルから HTML と Text レポートを生成

        Args:
            json_file_path: 入力 JSON ファイルパス
            output_dir: 出力ディレクトリ（デフォルト："reports"）

        Returns:
            生成ファイルパスの辞書
            {
                "html": "reports/html/competitor_analytics_20260326.html",
                "text": "reports/text/competitor_analytics_20260326.txt"
            }
        """
        try:
            # JSON ファイル読み込み
            data = ReportGenerator._load_json(json_file_path)

            # 出力ディレクトリ作成
            dirs = ReportGenerator._ensure_directories(output_dir)

            # ファイル名生成
            output_filename = ReportGenerator._get_output_filename()

            # HTML レポート生成
            html_content = HTMLFormatter.generate_html(data)
            html_file = dirs["html_dir"] / f"{output_filename}.html"
            html_path = ReportGenerator._save_file(html_content, html_file)

            # Text レポート生成
            text_content = TextFormatter.generate_text(data)
            text_file = dirs["text_dir"] / f"{output_filename}.txt"
            text_path = ReportGenerator._save_file(text_content, text_file)

            return {
                "html": str(html_path),
                "text": str(text_path)
            }

        except Exception as e:
            raise RuntimeError(f"レポート生成エラー: {e}")

    @staticmethod
    def _load_json(json_file_path: str) -> Dict[str, Any]:
        """
        JSON ファイルを読み込み

        Args:
            json_file_path: JSON ファイルパス

        Returns:
            JSON データ（辞書）

        Raises:
            ValueError: ファイルが見つからない場合
            json.JSONDecodeError: JSON が無効な場合
        """
        file_path = Path(json_file_path)

        if not file_path.exists():
            raise ValueError(f"ファイルが見つかりません: {json_file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    @staticmethod
    def _ensure_directories(output_dir: str) -> Dict[str, Path]:
        """
        出力ディレクトリを作成（存在しない場合）

        Args:
            output_dir: 出力ディレクトリ

        Returns:
            ディレクトリパスの辞書
            {
                "html_dir": Path("reports/html"),
                "text_dir": Path("reports/text")
            }
        """
        base_dir = Path(output_dir)
        html_dir = base_dir / "html"
        text_dir = base_dir / "text"

        html_dir.mkdir(parents=True, exist_ok=True)
        text_dir.mkdir(parents=True, exist_ok=True)

        return {
            "html_dir": html_dir,
            "text_dir": text_dir
        }

    @staticmethod
    def _get_output_filename(prefix: str = "competitor_analytics") -> str:
        """
        タイムスタンプ付きファイル名を生成

        Args:
            prefix: ファイル名プレフィックス

        Returns:
            ファイル名（タイムスタンプ付き）
            例: competitor_analytics_20260326
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{prefix}_{timestamp}"

    @staticmethod
    def _save_file(content: str, file_path: Path) -> Path:
        """
        ファイルを保存

        Args:
            content: ファイル内容
            file_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        # 親ディレクトリを作成
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # ファイルに保存（UTF-8）
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path
