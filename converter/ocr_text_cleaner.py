import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class OCRTextCleaner:
    """OCR テキストのノイズ除去と誤認識補正"""

    # UI ノイズパターン（完全一致で削除）
    UI_NOISE_PATTERNS = [
        "ウィンドウ", "zoom", "Mindieis", "mindmeistercomlappimapl",
        "チャット", "更新", "日決済", "ブラットフォーム",
    ]

    # 日本語 OCR 誤認識修正辞書
    OCR_CORRECTIONS = {
        "アブリ": "アプリ",
        "Youlube": "YouTube",
        "youlube": "youtube",
        "中業": "事業",
        "その池": "その他",
        "日テザイン": "デザイン",
        "日デザイン": "デザイン",
        "迎営": "営業",
        "事菜": "事業",
        "ココナラ中業": "ココナラ事業",
        "ココナラ事菜": "ココナラ事業",
        "ブックマー": "ブックマーク",
        "その化": "その他",
        "緩巣": "",
        "儀が": "",
        "儀合め": "つまり",
    }

    @staticmethod
    def clean(visual_text: str) -> Tuple[str, Dict]:
        """
        visual_text をクリーニングして返す
        
        Returns:
            (cleaned_text, metadata)
        """
        if not visual_text:
            return "", {"original_length": 0, "cleaned_length": 0, "changes": 0}

        original = visual_text
        text = visual_text
        changes = 0

        # Step 1: UI ノイズ除去
        for pattern in OCRTextCleaner.UI_NOISE_PATTERNS:
            if pattern in text:
                text = text.replace(pattern, "")
                changes += 1

        # Step 2: 日本語誤認識補正
        for wrong, correct in OCRTextCleaner.OCR_CORRECTIONS.items():
            if wrong in text:
                text = text.replace(wrong, correct)
                changes += 1

        # Step 3: 正規化
        text = re.sub(r" +", " ", text)
        text = text.strip()

        # Step 4: 重複単語除去
        words = text.split()
        deduped = []
        prev_word = None
        for word in words:
            if word != prev_word:
                deduped.append(word)
                prev_word = word
        text = " ".join(deduped)

        metadata = {
            "original_length": len(original),
            "cleaned_length": len(text),
            "changes": changes,
            "reduction_ratio": round((1 - len(text) / max(len(original), 1)) * 100, 2),
        }

        return text, metadata
