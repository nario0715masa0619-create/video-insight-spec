"""
CenterPinLabelingService - center_pin 単位のラベル付与ロジック

責務：
- center_pin 単位のラベル付与
- center_pins 配列への一括適用
- プロンプト構築
"""

import json
import logging
from typing import List, Dict, Any, Optional
from converter.gemini_llm_client import GeminiLLMClient


class CenterPinLabelingService:
    """center_pin のラベル付与を担当するサービス"""

    def __init__(self, llm_client: Optional[GeminiLLMClient] = None):
        """
        初期化

        Args:
            llm_client (GeminiLLMClient, optional): LLM クライアント
        """
        self.llm_client = llm_client or GeminiLLMClient()

    def _build_labeling_prompt(self, center_pin: Dict[str, Any]) -> str:
        """
        center_pin のラベル付与プロンプトを構築

        Args:
            center_pin (Dict): center_pin オブジェクト

        Returns:
            str: プロンプト
        """
        content = center_pin.get("content", "")
        element_id = center_pin.get("element_id", "unknown")

        prompt = f"""
以下の content から、ビジネスコンテキストでのラベルを抽出してください。

【content】
{content}

【要件】
1. business_theme: ビジネスの主要テーマ（複数可、配列で返す）
   例: マーケティング、セールス、データ分析、コピーライティング など
   
2. funnel_stage: 購買ファネルのステージ
   選択肢: 認知, 興味・関心, 比較検討, クロージング, 継続・LTV, 教育
   
3. difficulty: コンテンツの難易度
   選択肢: beginner, intermediate, advanced

【出力形式】
必ず以下の JSON 形式で返してください（他の説明テキストは不要）：
{{
  "element_id": "{element_id}",
  "business_theme": ["テーマ1", "テーマ2"],
  "funnel_stage": "ステージ",
  "difficulty": "難易度"
}}
"""
        return prompt

    def label_center_pin(self, center_pin: Dict[str, Any]) -> Dict[str, Any]:
        """
        単一の center_pin をラベル付与

        Args:
            center_pin (Dict): center_pin オブジェクト

        Returns:
            Dict: ラベル付与済み center_pin
        """
        try:
            prompt = self._build_labeling_prompt(center_pin)
            labels_json = self.llm_client.call_json(prompt)

            # labels フィールドがなければ作成
            if "labels" not in center_pin:
                center_pin["labels"] = {}

            # Gemini の JSON レスポンスからラベルを抽出
            center_pin["labels"]["business_theme"] = labels_json.get("business_theme", [])
            center_pin["labels"]["funnel_stage"] = labels_json.get("funnel_stage", "unknown")
            center_pin["labels"]["difficulty"] = labels_json.get("difficulty", "unknown")

            logging.info(f"✅ {center_pin['element_id']} をラベル付与しました")
            return center_pin

        except Exception as e:
            logging.error(f"❌ {center_pin.get('element_id', 'unknown')} のラベル付与に失敗: {e}")
            raise

    def label_center_pins(
        self, center_pins: List[Dict[str, Any]], top_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        center_pins 配列に対して一括ラベル付与

        Args:
            center_pins (List[Dict]): center_pins リスト
            top_n (int, optional): 処理する上位 N 件（None = すべて）

        Returns:
            List[Dict]: ラベル付与済み center_pins
        """
        # top_n に基づいて処理対象を決定
        if top_n is None:
            target_pins = center_pins
            mode = "FULL"
        else:
            target_pins = center_pins[:top_n]
            mode = f"SAMPLE (top {top_n})"

        logging.info(f"🎯 {mode} モード: {len(target_pins)} 件をラベル付与開始")

        labeled_pins = []
        success_count = 0
        failure_count = 0

        for i, pin in enumerate(target_pins, 1):
            try:
                labeled_pin = self.label_center_pin(pin)
                labeled_pins.append(labeled_pin)
                success_count += 1
                logging.debug(f"   [{i}/{len(target_pins)}] ✅ {pin['element_id']}")
            except Exception as e:
                logging.warning(f"   [{i}/{len(target_pins)}] ❌ {pin['element_id']}: {e}")
                failure_count += 1
                # 失敗した場合も元のピンを追加（ラベルなし）
                labeled_pins.append(pin)

        logging.info(f"✅ ラベル付与完了: 成功 {success_count}, 失敗 {failure_count}")
        return labeled_pins
