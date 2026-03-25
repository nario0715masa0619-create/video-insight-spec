"""
GeminiLLMClient - LLM クライアント層

責務：
- Gemini API キーの管理
- モデルの初期化
- API 呼び出しのリトライロジック
- JSON レスポンス処理

このクラスが google-genai に唯一直接依存します。
外部には「dict を返すメソッド」のみを公開します。
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any

try:
    from google.genai import Client
    from google.genai.types import GenerateContentConfig
except ImportError:
    raise ImportError("google-genai がインストールされていません。pip install google-genai を実行してください。")


class GeminiAPIError(Exception):
    """Gemini API 呼び出しエラー"""
    pass


class GeminiLLMClient:
    """LLM クライアント層: Gemini API 呼び出しを一元化する"""

    def __init__(self, api_key: Optional[str] = None, model_id: Optional[str] = None, max_retries: int = 3):
        """
        初期化

        Args:
            api_key (str, optional): Gemini API キー。指定されない場合は環境変数から取得
            model_id (str, optional): モデル ID。デフォルト: gemini-2.0-flash
            max_retries (int, optional): リトライ回数。デフォルト: 3
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_id = model_id or os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY が設定されていません。環境変数または引数で指定してください。")

        # google-genai の初期化（Client を直接作成）
        self.client = Client(api_key=self.api_key)
        
        self.logger.info(f"✅ Gemini モデル '{self.model_id}' を初期化しました（max_retries={self.max_retries}）")

    def _call_with_retry(self, prompt: str, response_mime_type: str = "application/json") -> str:
        """
        リトライロジック付きで API を呼び出す（プライベートメソッド）

        Args:
            prompt (str): プロンプト
            response_mime_type (str, optional): レスポンス MIME タイプ。デフォルト: application/json

        Returns:
            str: API レスポンステキスト

        Raises:
            GeminiAPIError: 最大リトライ回数超過時
        """
        for attempt in range(self.max_retries):
            try:
                # google-genai での API 呼び出し
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=GenerateContentConfig(
                        response_mime_type=response_mime_type,
                        temperature=0.7,
                        max_output_tokens=2048,
                    ),
                )
                
                self.logger.info(f"✅ Gemini API 呼び出し成功（試行 {attempt + 1}/{self.max_retries}）")
                return response.text

            except Exception as e:
                wait_time = 2 ** attempt
                error_type = type(e).__name__

                if attempt < self.max_retries - 1:
                    self.logger.warning(
                        f"⚠️ Gemini API エラー（試行 {attempt + 1}/{self.max_retries}）: {error_type}: {str(e)[:100]}. "
                        f"{wait_time} 秒後に再試行します..."
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(
                        f"❌ Gemini API 呼び出し失敗（{self.max_retries} 回試行後）: {error_type}: {str(e)}"
                    )
                    raise GeminiAPIError(f"API 呼び出し失敗: {error_type}: {str(e)}") from e

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        JSON 形式のレスポンスを生成（公開メソッド）

        Args:
            prompt (str): プロンプト

        Returns:
            Dict[str, Any]: パースされた JSON レスポンス

        Raises:
            GeminiAPIError: API 呼び出しエラー
            json.JSONDecodeError: JSON パースエラー
        """
        try:
            response_text = self._call_with_retry(prompt, response_mime_type="application/json")
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ JSON パースエラー: {e}. レスポンス: {response_text[:200]}")
                raise

        except GeminiAPIError:
            raise
        except Exception as e:
            self.logger.error(f"❌ 予期しないエラー: {type(e).__name__}: {e}")
            raise GeminiAPIError(f"予期しないエラー: {type(e).__name__}: {e}") from e
