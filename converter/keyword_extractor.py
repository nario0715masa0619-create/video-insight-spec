"""
keyword_extractor.py - キーワード抽出モジュール（Phase 2.1 修正版）

JANOME 対応（品詞コード「名」「動」「形」を正しく処理）
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from janome.tokenizer import Tokenizer
    JANOME_AVAILABLE = True
    _janome_tokenizer = Tokenizer()
except ImportError:
    JANOME_AVAILABLE = False
    logger.warning("JANOME not available. Falling back to regex mode.")


class KeywordExtractor:
    """キーワード抽出クラス（Phase 2.1 修正版）"""
    
    def __init__(
        self,
        db_path: str,
        evidence_records: List[Dict],
        use_nlp: bool = True,
        stopwords: Optional[List[str]] = None
    ):
        """初期化"""
        self.db_path = db_path
        self.evidence_records = evidence_records
        self.use_nlp = use_nlp and JANOME_AVAILABLE
        
        # デフォルト stopwords（拡張版）
        self.stopwords = stopwords or {
            "が", "を", "に", "は", "の", "で", "と", "も", "から", "まで",
            "など", "および", "または", "ため", "こと", "もの", "ある", "いる",
            "する", "なる", "いく", "くる", "おく", "しまう", "みる", "やる",
            "できる", "いった", "いう", "あった", "あるいは",
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "of", "by", "for", "with", "from", "is", "are", "be", "have",
        }
        
        logger.info(f"KeywordExtractor initialized (use_nlp={self.use_nlp})")
    
    def extract_keywords(self, title: str, min_length: int = 2) -> List[str]:
        """タイトルからキーワードを抽出"""
        if not title:
            return []
        
        if self.use_nlp:
            return self._extract_keywords_janome(title, min_length)
        else:
            return self._extract_keywords_regex(title, min_length)
    
    def _extract_keywords_janome(self, title: str, min_length: int = 2) -> List[str]:
        """JANOME による形態素解析キーワード抽出（修正版）"""
        try:
            keywords = set()
            
            for token in _janome_tokenizer.tokenize(title):
                word = token.surface
                pos = token.part_of_speech[0]  # 修正: 「名」「動」「形」
                
                # 名詞、動詞、形容詞を抽出（修正版）
                if pos in ("名", "動", "形"):
                    if len(word) >= min_length and word not in self.stopwords:
                        keywords.add(word)
            
            return sorted(list(keywords))
        
        except Exception as e:
            logger.warning(f"JANOME extraction failed: {e}")
            return self._extract_keywords_regex(title, min_length)
    
    def _extract_keywords_regex(self, title: str, min_length: int = 2) -> List[str]:
        """正規表現によるキーワード抽出（Phase 1 互換）"""
        pattern = r'[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF\w]+'
        keywords = set()
        
        for match in re.finditer(pattern, title, re.UNICODE):
            word = match.group()
            if len(word) >= min_length and word not in self.stopwords:
                keywords.add(word)
        
        return sorted(list(keywords))
    
    def get_keyword_mention_frequency(self, title: str, db_records: List[Dict]) -> Dict[str, int]:
        """キーワード出現頻度を計算"""
        keywords = self.extract_keywords(title)
        frequency = {kw: 0 for kw in keywords}
        
        for kw in keywords:
            frequency[kw] += title.count(kw)
            for record in db_records:
                frequency[kw] += record.get("visual_text", "").count(kw)
        
        return {k: v for k, v in frequency.items() if v > 0}
    
    def get_keyword_segment_count(self, keyword: str, db_records: List[Dict]) -> int:
        """キーワードが出現するセグメント数を計算"""
        return sum(1 for record in db_records if keyword in record.get("visual_text", ""))
    
    def get_keyword_first_appearance_ms(self, keyword: str, db_records: List[Dict]) -> Optional[int]:
        """キーワードの最初の出現タイムスタンプを取得"""
        for record in sorted(db_records, key=lambda r: r.get("start_ms", 0)):
            if keyword in record.get("visual_text", ""):
                return record.get("start_ms")
        return None
    
    def get_primary_theme_keywords(self, title: str, db_records: List[Dict], top_n: int = 5) -> List[str]:
        """プライマリテーマキーワード（出現頻度上位 N 個）を抽出"""
        freq = self.get_keyword_mention_frequency(title, db_records)
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords[:top_n]]
