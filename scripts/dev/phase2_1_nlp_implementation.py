"""
Phase 2.1 NLP キーワード抽出実装スクリプト
- JANOME を requirements.txt に追加
- keyword_extractor.py を拡張（use_nlp フラグ追加）
- テストコード追加（JANOME版 + 正規表現版互換性テスト）
- ドキュメント更新
- テスト実行
- Git commit & push
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path.cwd()
CONVERTER_DIR = REPO_ROOT / "converter"
TESTS_DIR = REPO_ROOT / "tests"

GITHUB_USER = "nario0715masa0619-create"
GITHUB_EMAIL = "nari.o.0715.masa.0619@gmail.com"
GIT_BRANCH = "main"

print("=" * 80)
print("🚀 Phase 2.1 NLP キーワード抽出実装スクリプト")
print("=" * 80)

# =====================================
# Step 1: requirements.txt に JANOME を追加
# =====================================
print("\n[Step 1] requirements.txt に JANOME を追加中...")

with open(REPO_ROOT / "requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()

if "janome" not in requirements.lower():
    requirements += "janome>=0.4.2\n"
    
    with open(REPO_ROOT / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    
    print("✅ JANOME を requirements.txt に追加")
else:
    print("ℹ️  JANOME は既に requirements.txt に含まれています")

# =====================================
# Step 2: JANOME をインストール
# =====================================
print("\n[Step 2] JANOME をインストール中...")

try:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "janome>=0.4.2"],
        check=True,
        timeout=60
    )
    print("✅ JANOME インストール完了")
except Exception as e:
    print(f"⚠️  JANOME インストールに失敗（続行）: {e}")

# =====================================
# Step 3: keyword_extractor.py を拡張
# =====================================
print("\n[Step 3] keyword_extractor.py を拡張中...")

keyword_extractor_new = '''"""
keyword_extractor.py - キーワード抽出モジュール

Phase 2.1: NLP（JANOME）対応版
- use_nlp=True: JANOME による日本語形態素解析（推奨、高精度）
- use_nlp=False: 正規表現（Phase 1 互換、軽量）
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# JANOME のインポート（オプション）
try:
    from janome.tokenizer import Tokenizer
    JANOME_AVAILABLE = True
    _janome_tokenizer = Tokenizer()
except ImportError:
    JANOME_AVAILABLE = False
    logger.warning("JANOME not available. Falling back to regex mode.")


class KeywordExtractor:
    """キーワード抽出クラス（Phase 2.1: NLP 対応）"""
    
    def __init__(
        self,
        db_path: str,
        evidence_records: List[Dict],
        use_nlp: bool = True,
        stopwords: Optional[List[str]] = None
    ):
        """
        初期化
        
        Args:
            db_path: Mk2_Sidecar_XX.db のパス
            evidence_records: evidence_index テーブルのレコード一覧
            use_nlp: True=JANOME（推奨）, False=正規表現（フォールバック）
            stopwords: フィルタリング対象キーワード
        """
        self.db_path = db_path
        self.evidence_records = evidence_records
        self.use_nlp = use_nlp and JANOME_AVAILABLE
        
        # デフォルト stopwords
        self.stopwords = stopwords or {
            "が", "を", "に", "は", "の", "で", "と", "も", "から", "まで",
            "など", "および", "or", "and", "the", "a", "an"
        }
        
        logger.info(f"KeywordExtractor initialized (use_nlp={self.use_nlp})")
    
    def extract_keywords(self, title: str, min_length: int = 2) -> List[str]:
        """
        タイトルからキーワードを抽出
        
        Args:
            title: ビデオタイトル
            min_length: キーワード最小文字数
        
        Returns:
            キーワードリスト（重複なし、50音順）
        """
        if not title:
            return []
        
        if self.use_nlp:
            return self._extract_keywords_janome(title, min_length)
        else:
            return self._extract_keywords_regex(title, min_length)
    
    def _extract_keywords_janome(self, title: str, min_length: int = 2) -> List[str]:
        """
        JANOME による形態素解析キーワード抽出
        
        方針:
        - 名詞（Noun）、動詞（Verb）、形容詞（Adjective）を抽出
        - stopwords をフィルタリング
        - 最小文字数以上のみを返す
        
        精度: ★★★★★
        速度: ★★★★☆
        """
        try:
            keywords = set()
            
            for token in _janome_tokenizer.tokenize(title):
                word = token.surface
                pos = token.part_of_speech[0]
                
                # 名詞、動詞、形容詞を抽出
                if pos in ("名詞", "動詞", "形容詞"):
                    if len(word) >= min_length and word not in self.stopwords:
                        keywords.add(word)
            
            return sorted(list(keywords))
        
        except Exception as e:
            logger.warning(f"JANOME extraction failed, falling back to regex: {e}")
            return self._extract_keywords_regex(title, min_length)
    
    def _extract_keywords_regex(self, title: str, min_length: int = 2) -> List[str]:
        """
        正規表現によるキーワード抽出（Phase 1 互換）
        
        方針:
        - 日本語（CJK）と英数字（\w）を含むトークンを抽出
        - stopwords をフィルタリング
        - 最小文字数以上のみを返す
        
        精度: ★★★☆☆
        速度: ★★★★★
        """
        # 日本語（CJK Unified Ideographs）+ Hiragana + Katakana + 英数字
        pattern = r'[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF\w]+'
        
        keywords = set()
        for match in re.finditer(pattern, title, re.UNICODE):
            word = match.group()
            if len(word) >= min_length and word not in self.stopwords:
                keywords.add(word)
        
        return sorted(list(keywords))
    
    def get_keyword_mention_frequency(
        self,
        title: str,
        db_records: List[Dict]
    ) -> Dict[str, int]:
        """
        タイトルと visual_text におけるキーワード出現頻度を計算
        
        Args:
            title: タイトル
            db_records: evidence_index レコード一覧
        
        Returns:
            {keyword: frequency} の辞書
        """
        keywords = self.extract_keywords(title)
        frequency = {kw: 0 for kw in keywords}
        
        # タイトル中の出現を計数
        for kw in keywords:
            frequency[kw] += title.count(kw)
        
        # visual_text 中の出現を計数
        for record in db_records:
            visual_text = record.get("visual_text", "")
            for kw in keywords:
                frequency[kw] += visual_text.count(kw)
        
        # 0 の項目を削除
        return {k: v for k, v in frequency.items() if v > 0}
    
    def get_keyword_segment_count(
        self,
        keyword: str,
        db_records: List[Dict]
    ) -> int:
        """
        キーワードが出現するセグメント（evidence レコード）数を計算
        
        Args:
            keyword: 検索キーワード
            db_records: evidence_index レコード一覧
        
        Returns:
            セグメント数
        """
        count = 0
        for record in db_records:
            if keyword in record.get("visual_text", ""):
                count += 1
        return count
    
    def get_keyword_first_appearance_ms(
        self,
        keyword: str,
        db_records: List[Dict]
    ) -> Optional[int]:
        """
        キーワードの最初の出現タイムスタンプ（ミリ秒）を取得
        
        Args:
            keyword: 検索キーワード
            db_records: evidence_index レコード一覧
        
        Returns:
            最初の出現時刻（ms）、見つからない場合は None
        """
        for record in sorted(db_records, key=lambda r: r.get("start_ms", 0)):
            if keyword in record.get("visual_text", ""):
                return record.get("start_ms")
        return None
    
    def get_primary_theme_keywords(
        self,
        title: str,
        db_records: List[Dict],
        top_n: int = 5
    ) -> List[str]:
        """
        プライマリテーマキーワード（出現頻度上位 N 個）を抽出
        
        Args:
            title: タイトル
            db_records: evidence_index レコード一覧
            top_n: 返すキーワード数
        
        Returns:
            出現頻度でソートされたキーワードリスト
        """
        freq = self.get_keyword_mention_frequency(title, db_records)
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords[:top_n]]
'''

with open(CONVERTER_DIR / "keyword_extractor.py", "w", encoding="utf-8") as f:
    f.write(keyword_extractor_new)

print("✅ keyword_extractor.py を拡張（NLP/正規表現フラグ追加）")

# =====================================
# Step 4: テストコード追加（JANOME版 + 互換性テスト）
# =====================================
print("\n[Step 4] テストコード追加中...")

test_keyword_extractor_nlp = '''"""
keyword_extractor.py の unit tests (Phase 2.1: NLP 対応版)

テスト方針:
- JANOME 版（use_nlp=True）のテスト
- 正規表現版（use_nlp=False）のテスト
- 両者の互換性確認
"""

import pytest
from converter.keyword_extractor import KeywordExtractor


class TestKeywordExtractorNLPMode:
    """JANOME モード（use_nlp=True）のテスト"""
    
    def test_extract_keywords_janome_japanese(self, sample_sidecar_db_file):
        """JANOME で日本語キーワード抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=True
        )
        keywords = extractor.extract_keywords(
            title="Python マーケティング 戦略 ガイド"
        )
        
        assert len(keywords) > 0
        assert any("マーケティング" in kw or "戦略" in kw for kw in keywords)
    
    def test_extract_keywords_janome_english(self, sample_sidecar_db_file):
        """JANOME で英語キーワード抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=True
        )
        keywords = extractor.extract_keywords(
            title="Digital Marketing Strategy"
        )
        
        assert len(keywords) > 0
    
    def test_extract_keywords_janome_mixed(self, sample_sidecar_db_file):
        """JANOME で混合言語キーワード抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=True
        )
        keywords = extractor.extract_keywords(
            title="AI による営業戦略最適化"
        )
        
        assert len(keywords) > 0


class TestKeywordExtractorRegexMode:
    """正規表現モード（use_nlp=False）のテスト"""
    
    def test_extract_keywords_regex_japanese(self, sample_sidecar_db_file):
        """正規表現で日本語キーワード抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        keywords = extractor.extract_keywords(
            title="営業戦略とブランディング"
        )
        
        assert len(keywords) > 0
        assert any("営業" in kw or "戦略" in kw for kw in keywords)
    
    def test_extract_keywords_regex_english(self, sample_sidecar_db_file):
        """正規表現で英語キーワード抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        keywords = extractor.extract_keywords(
            title="Digital Marketing Strategy"
        )
        
        assert len(keywords) > 0
    
    def test_extract_keywords_minimum_length(self, sample_sidecar_db_file):
        """最小長（2文字）未満は除外"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        keywords = extractor.extract_keywords(
            title="a あ bc 定義"
        )
        
        assert all(len(kw) >= 2 for kw in keywords)


class TestKeywordExtractorCompatibility:
    """JANOME 版と正規表現版の互換性テスト"""
    
    def test_compatibility_both_modes(self, sample_sidecar_db_file):
        """両モードで共通キーワードが抽出されることを確認"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        
        title = "マーケティング戦略実装"
        
        extractor_nlp = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=True
        )
        extractor_regex = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        
        keywords_nlp = set(extractor_nlp.extract_keywords(title))
        keywords_regex = set(extractor_regex.extract_keywords(title))
        
        # 両方で抽出されたキーワード
        common = keywords_nlp & keywords_regex
        
        # 共通キーワードが存在することを確認
        assert len(common) > 0, "Both methods should extract common keywords"


class TestKeywordExtractorMentionFrequency:
    """キーワード出現頻度計算のテスト"""
    
    def test_get_keyword_mention_frequency(self, sample_sidecar_db_file):
        """キーワード出現頻度を計算"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        
        freq = extractor.get_keyword_mention_frequency(
            title="データ分析",
            db_records=[
                {"visual_text": "データ", "element_id": "e1"},
                {"visual_text": "分析ツール", "element_id": "e2"},
            ]
        )
        
        assert isinstance(freq, dict)


class TestKeywordExtractorSegmentCount:
    """キーワードセグメント数計算のテスト"""
    
    def test_get_keyword_segment_count(self, sample_sidecar_db_file):
        """キーワードが出現するセグメント数を計算"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        
        count = extractor.get_keyword_segment_count(
            keyword="テスト",
            db_records=[
                {"visual_text": "テスト1", "element_id": "e1"},
                {"visual_text": "テスト2", "element_id": "e2"},
                {"visual_text": "他の", "element_id": "e3"},
            ]
        )
        
        assert count == 2


class TestKeywordExtractorFirstAppearance:
    """キーワード初回出現タイムスタンプのテスト"""
    
    def test_get_keyword_first_appearance_ms(self, sample_sidecar_db_file):
        """キーワードの最初の出現タイムスタンプを取得"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        
        first_ms = extractor.get_keyword_first_appearance_ms(
            keyword="テスト",
            db_records=[
                {"visual_text": "他の", "start_ms": 0, "element_id": "e0"},
                {"visual_text": "テスト1", "start_ms": 15000, "element_id": "e1"},
                {"visual_text": "テスト2", "start_ms": 30000, "element_id": "e2"},
            ]
        )
        
        assert first_ms == 15000


class TestKeywordExtractorPrimaryTheme:
    """プライマリテーマキーワード抽出のテスト"""
    
    def test_get_primary_theme_keywords(self, sample_sidecar_db_file):
        """出現頻度上位 N キーワードを抽出"""
        from converter.db_helper import SidecarDBHelper
        
        records = SidecarDBHelper.load_evidence_index(sample_sidecar_db_file)
        extractor = KeywordExtractor(
            sample_sidecar_db_file, records, use_nlp=False
        )
        
        primary = extractor.get_primary_theme_keywords(
            title="マーケティング マーケティング 戦略",
            db_records=[
                {"visual_text": "マーケティング", "element_id": "e1"},
                {"visual_text": "戦略", "element_id": "e2"},
            ],
            top_n=3
        )
        
        assert isinstance(primary, list)
        assert len(primary) > 0
'''

with open(TESTS_DIR / "test_keyword_extractor_nlp.py", "w", encoding="utf-8") as f:
    f.write(test_keyword_extractor_nlp)

print("✅ tests/test_keyword_extractor_nlp.py を作成（NLP + 正規表現互換性テスト）")

# =====================================
# Step 5: converter/README.md を更新
# =====================================
print("\n[Step 5] ドキュメント更新中...")

converter_readme_update = '''# Converter モジュール

video-scraper の出力（Mk2_Core_XX.json + Mk2_Sidecar_XX.db）を video-insight-spec 仕様の JSON に変換するモジュール群。

## Phase 1 仕様

- **データ源**: Mk2_Core_XX.json（知識要素）+ Mk2_Sidecar_XX.db（エビデンスと timestamps）
- **出力**: video-insight-spec JSON（3層構造: video_meta, knowledge_core, views）

## Phase 2.0 拡張

- テストスイート: 39 個の Unit Tests
- API ドキュメント: 各モジュールの詳細仕様

## Phase 2.1 拡張（NLP キーワード抽出）

### keyword_extractor.py の新機能

**2 つのモード を選択可能：**

#### モード 1: JANOME（推奨）- `use_nlp=True`

```python
from converter.keyword_extractor import KeywordExtractor
from converter.db_helper import SidecarDBHelper

records = SidecarDBHelper.load_evidence_index("Mk2_Sidecar_01.db")
extractor = KeywordExtractor("Mk2_Sidecar_01.db", records, use_nlp=True)

keywords = extractor.extract_keywords("Python マーケティング 戦略")
# → ['マーケティング', '戦略', 'Python']  (形態素解析)
```

#### モード 2: 正規表現（互換）- `use_nlp=False`
```python
extractor = KeywordExtractor("Mk2_Sidecar_01.db", records, use_nlp=False)
```
'''

with open(CONVERTER_DIR / "README.md", "w", encoding="utf-8") as f:
    f.write(converter_readme_update)
print("✅ converter/README.md を更新完了")

# =====================================
# Step 6: テストの実行
# =====================================
print("\n[Step 6] pytest を実行中...")
print("=" * 80)

try:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "tests/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print("=" * 80)
    
    if result.returncode == 0:
        print("✅ テスト全パス！")
        test_passed = True
    else:
        print("❌ 一部テストが失敗（詳細は上記参照）")
        test_passed = False
        
except Exception as e:
    print(f"❌ テスト実行エラー: {e}")
    test_passed = False

# =====================================
# Step 7: Git commit & push
# =====================================
if test_passed:
    print("\n[Step 7] Git commit & push 中...")
    
    try:
        # Git ユーザー設定
        subprocess.run(["git", "config", "user.name", GITHUB_USER], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "config", "user.email", GITHUB_EMAIL], cwd=REPO_ROOT, check=True)
        
        # ファイル追加
        subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True)
        
        # コミットメッセージ
        commit_msg = f"""feat: Phase 2.1 NLP キーワード抽出関数の実装 (JANOME)

- `requirements.txt`: janome>=0.4.2 追加
- `converter/keyword_extractor.py`: JANOME 形態素解析モード実装 (`use_nlp=True`)
- `tests/test_keyword_extractor_nlp.py`: NLP 専用のテストケース追加
- `converter/README.md`: NLP モードの使い方についてドキュメント更新
- テスト結果: 全件のテスト通過

実装日時: {datetime.now().isoformat()}"""
        
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "push", "origin", GIT_BRANCH], cwd=REPO_ROOT, check=True)
        print("✅ Git commit & push 完了")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作に失敗: {e}")
else:
    print("\n⚠️ テストが失敗したため、Git push をスキップしました")

print("\n" + "=" * 80)
print("📋 Phase 2.1 実装完了レポート")
print("=" * 80)
