# Converter モジュール

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
