import pytest
from converter.ocr_text_cleaner import OCRTextCleaner


def test_clean_ui_noise():
    """UI ノイズ除去"""
    text = "ウィンドウ zoom チャット Hello"
    cleaned, _ = OCRTextCleaner.clean(text)
    assert "ウィンドウ" not in cleaned
    assert "zoom" not in cleaned
    assert "チャット" not in cleaned
    assert "Hello" in cleaned


def test_clean_ocr_mistakes():
    """OCR 誤認識補正"""
    text = "アブリを使ってYoutubeで動画を見る"
    cleaned, _ = OCRTextCleaner.clean(text)
    assert "アプリ" in cleaned
    assert "アブリ" not in cleaned


def test_clean_spaces():
    """スペース正規化"""
    text = "Hello   World  Test"
    cleaned, _ = OCRTextCleaner.clean(text)
    assert "  " not in cleaned


def test_clean_duplicates():
    """重複単語の除去"""
    text = "Brain Brain Brain の セン ターピン"
    cleaned, _ = OCRTextCleaner.clean(text)
    assert cleaned.count("Brain") == 1


def test_clean_empty():
    """空文字列処理"""
    cleaned, metadata = OCRTextCleaner.clean("")
    assert cleaned == ""
    assert metadata["original_length"] == 0
