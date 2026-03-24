\# PHASE2\_2\_3\_VIDEO\_ID\_ENRICHER.md



\## Phase 2.2.3: YouTube Video ID Enricher



\### 概要

`insight\_spec\_XX.json` の `video\_meta.title` フィールドから YouTube Data API v3 を使って実際の YouTube video\_id を検索し、JSON に自動補充するフェーズです。



\### 実装ファイル

\- `converter/youtube\_video\_id\_enricher.py` - Video ID 検索・キャッシング・JSON 更新ロジック

\- `tests/test\_youtube\_video\_id\_enricher.py` - ユニットテスト

\- `enrich\_insight\_spec\_all.py` - 全講義（01～21）の一括処理スクリプト



\### 仕様



\#### 1. Video ID 検索

YouTube Data API v3 の `search().list()` を使用して、タイトルから video\_id を検索します。



\#### 2. キャッシング機構

\- メモリ内キャッシュ（辞書）

\- API クォータ節約（月 1000 万リクエスト制限）

\- 同じタイトルの連続検索を 1 回に削減



\#### 3. JSON 更新ロジック

1\. `insight\_spec\_XX.json` を読み込み

2\. `video\_meta.video\_id` が存在（≠ "XX"）で、かつ≠ null なら、スキップ

3\. `video\_meta.title` から API で video\_id を検索

4\. 取得した video\_id を `video\_meta.video\_id` に上書き

5\. JSON ファイルを保存（UTF-8, indent=2）



\### 実装結果



\*\*テスト対象\*\*: `insight\_spec\_01.json`



\*\*結果\*\*:

\- 処理ファイル: 1 (insight\_spec\_01.json)

\- 成功: 1

\- video\_id: `b8u2CQLQBVU`

\- タイトル: "【超重要！】コンテンツ販売必須の基礎知識"



\*\*テスト結果\*\*: 5/5 PASS ✅



\### 出力例



\#### 更新前

```json

{

&#x20; "video\_meta": {

&#x20;   "video\_id": "01",

&#x20;   "title": "Lecture 01"

&#x20; }

}


#### 更新後

Copy{
  "video_meta": {
    "video_id": "b8u2CQLQBVU",
    "title": "Lecture 01"
  }
}



