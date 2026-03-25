"""
GeminiLLMClient - Gemini API の一元化された呼び出しインターフェース

責務：
- Gemini API キーの管理
- モデルの初期化
- API 呼び出しのリトライロジック
- JSON レスポンス処理
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("google-generativeai がインストールされていません。pip install google-generativeai を実行してください。")


class GeminiLLMClient:
    """Gemini API への統一されたアクセスポイント"""

    def __init__(self, api_key: Optional[str] = None, model_id: Optional[str] = None):
        """
        初期化

        Args:
            api_key (str, optional): Gemini API キー。指定されない場合は環境変数から取得
            model_id (str, optional): モデル ID。デフォルト: gemini-2.0-flash
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_id = model_id or os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")

        if not self.api_key:
            raise ValueError(
                "❌ GEMINI_API_KEY が設定されていません。"
                ".env ファイルまたは環境変数で設定してください。"
            )

        genai.configure(api_key=self.api_key)
        self.gen_model = genai.GenerativeModel(self.model_id)

        logging.info(f"✅ Gemini モデル '{self.model_id}' を初期化しました")

    def call_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        response_mime_type: str = "application/json",
    ) -> str:
        """
        リトライロジック付き Gemini API 呼び出し

        Args:
            prompt (str): プロンプト
            max_retries (int): 最大リトライ回数
            response_mime_type (str): レスポンス MIME タイプ

        Returns:
            str: Gemini からのレスポンステキスト
        """
        for attempt in range(max_retries):
            try:
                response = self.gen_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type=response_mime_type
                    ),
                )
                logging.info(f"✅ Gemini API 呼び出し成功（試行 {attempt + 1}/{max_retries}）")
                return response.text

            except Exception as e:
                wait_time = 2 ** attempt
                if attempt < max_retries - 1:
                    logging.warning(
                        f"⚠️ Gemini API エラー（試行 {attempt + 1}/{max_retries}）: {e}\n"
                        f"   {wait_time} 秒待機後に再試行します..."
                    )
                    time.sleep(wait_time)
                else:
                    logging.error(
                        f"❌ Gemini API 呼び出し失敗（最大リトライ回数 {max_retries} 超過）: {e}"
                    )
                    raise

    def call_json(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        JSON レスポンスを期待する Gemini API 呼び出し

        Args:
            prompt (str): プロンプト
            max_retries (int): 最大リトライ回数

        Returns:
            Dict[str, Any]: パースされた JSON オブジェクト
        """
        response_text = self.call_with_retry(prompt, max_retries)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON パース失敗: {e}\nレスポンス: {response_text}")
            raise
