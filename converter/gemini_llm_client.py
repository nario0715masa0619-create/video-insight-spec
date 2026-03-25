"""
GeminiLLMClient - LLM クライアント層

責務：
- Gemini API キーの管理
- モデルの初期化
- API 呼び出しのリトライロジック
- JSON レスポンス処理

このクラスが google.generativeai に唯一直接依存します。
外部には「dict を返すメソッド」のみを公開します。
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
except ImportError:
    raise ImportError("google-generativeai がインストールされていません。pip install google-generativeai を実行してください。")


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
            max_retries (int): 最大リトライ回数（デフォルト: 3）
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_id = model_id or os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")
        self.max_retries = max_retries

        if not self.api_key:
            raise ValueError(
                "❌ GEMINI_API_KEY が設定されていません。"
                ".env ファイルまたは環境変数で設定してください。"
            )

        genai.configure(api_key=self.api_key)
        self.gen_model = genai.GenerativeModel(self.model_id)

        logging.info(f"✅ Gemini モデル '{self.model_id}' を初期化しました（max_retries={self.max_retries}）")

    def _call_with_retry(
        self,
        prompt: str,
        response_mime_type: str = "application/json",
    ) -> str:
        """
        リトライロジック付き Gemini API 呼び出し（内部使用）

        Args:
            prompt (str): プロンプト
            response_mime_type (str): レスポンス MIME タイプ

        Returns:
            str: Gemini からのレスポンステキスト

        Raises:
            GeminiAPIError: 最大リトライ回数超過時
        """
        for attempt in range(self.max_retries):
            try:
                logging.debug(f"   [API 呼び出し試行 {attempt + 1}/{self.max_retries}]")
                response = self.gen_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type=response_mime_type
                    ),
                )
                logging.debug(f"✅ API 呼び出し成功（試行 {attempt + 1}/{self.max_retries}）")
                return response.text

            except google_exceptions.GoogleAPIError as e:
                # Google API エラー（一時的エラーの可能性）
                wait_time = 2 ** attempt
                if attempt < self.max_retries - 1:
                    logging.warning(
                        f"⚠️ Google API エラー（試行 {attempt + 1}/{self.max_retries}）: {e}\n"
                        f"   {wait_time} 秒待機後に再試行します..."
                    )
                    time.sleep(wait_time)
                else:
                    error_msg = f"❌ Gemini API 呼び出し失敗（最大リトライ回数 {self.max_retries} 超過）: {e}"
                    logging.error(error_msg)
                    raise GeminiAPIError(error_msg) from e

            except (TimeoutError, ConnectionError) as e:
                # タイムアウト・接続エラー（一時的エラーの可能性）
                wait_time = 2 ** attempt
                if attempt < self.max_retries - 1:
                    logging.warning(
                        f"⚠️ ネットワークエラー（試行 {attempt + 1}/{self.max_retries}）: {e}\n"
                        f"   {wait_time} 秒待機後に再試行します..."
                    )
                    time.sleep(wait_time)
                else:
                    error_msg = f"❌ ネットワークエラー（最大リトライ回数 {self.max_retries} 超過）: {e}"
                    logging.error(error_msg)
                    raise GeminiAPIError(error_msg) from e

            except Exception as e:
                # その他の予期しないエラー（リトライしない）
                error_msg = f"❌ 予期しないエラー: {type(e).__name__}: {e}"
                logging.error(error_msg)
                raise GeminiAPIError(error_msg) from e

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        JSON レスポンスを期待する Gemini API 呼び出し

        このクラスの公開メソッドです。
        内部では _call_with_retry でリトライロジックを実行し、
        JSON パースして dict を返します。

        Args:
            prompt (str): プロンプト

        Returns:
            Dict[str, Any]: パースされた JSON オブジェクト

        Raises:
            GeminiAPIError: API 呼び出し失敗時
            json.JSONDecodeError: JSON パース失敗時
        """
        response_text = self._call_with_retry(prompt)
        try:
            parsed = json.loads(response_text)
            logging.debug(f"✅ JSON パース成功")
            return parsed
        except json.JSONDecodeError as e:
            error_msg = f"❌ JSON パース失敗: {e}\nレスポンス: {response_text[:200]}..."
            logging.error(error_msg)
            raise GeminiAPIError(error_msg) from e
