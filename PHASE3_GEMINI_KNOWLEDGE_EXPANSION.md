\# PHASE3\_GEMINI\_KNOWLEDGE\_EXPANSION.md



\## Phase 3: Gemini API による知識点自動拡張



\### 概要



`importance\_score` の高いセンターピン（center\_pin）をベースに、Google Gemini 3 Pro API を使用して関連概念・実務応用例・注意点を自動生成し、`gemini\_expansion` フィールドとして JSON に統合するフェーズです。



\### 実装目標



\- \*\*入力\*\*: `insight\_spec\_XX.json` の `knowledge\_core\[].content` + `visual\_text` 抜粋

\- \*\*処理\*\*: Gemini 3 Pro で構造化プロンプト実行

\- \*\*出力\*\*: `gemini\_expansion` を各 center\_pin に追加

\- \*\*テスト対象\*\*: Brain マーケティング講座 1 本分（TOP 5 center\_pin）



\---



\## 設計仕様



\### 1. 入力データ



\#### ベーステキスト

\- \*\*メイン\*\*: `center\_pin.content`（既にまとめられたセンターピンテキスト）

\- \*\*参考情報\*\*: 関連する `visual\_text` の抜粋（クリーニング済みテキストから関連部分を抽出）



\#### 処理対象の選定

1\. `evidence\_index` テーブルから `importance\_score` でソート（降順）

2\. TOP 5 件を抽出

3\. 各 center\_pin ごとに 1 リクエストを Gemini API に送信



\#### 例



importance\_score 順位 1位: BRAIN\_CENTERPIN\_001 (importance\_score=3.0) 2位: BRAIN\_CENTERPIN\_002 (importance\_score=3.0) 3位: BRAIN\_CENTERPIN\_003 (importance\_score=3.0) 4位: BRAIN\_CENTERPIN\_004 (importance\_score=2.0) 5位: BRAIN\_CENTERPIN\_005 (importance\_score=2.0)





\---



\### 2. 出力フォーマット



\#### JSON スキーマ（1 center\_pin 単位）



```json

{

&#x20; "element\_id": "BRAIN\_CENTERPIN\_001",

&#x20; "type": "FACT",

&#x20; "content": "量産思考",

&#x20; "base\_purity\_score": 90.0,

&#x20; "occurrence\_count": 3,

&#x20; "importance\_score": 3.0,

&#x20; "gemini\_expansion": {

&#x20;   "related\_concepts": \[

&#x20;     "スケーラビリティ設計",

&#x20;     "プロセス標準化",

&#x20;     "リスク分散"

&#x20;   ],

&#x20;   "practical\_applications": \[

&#x20;     "SOP 作成時に、各ステップの反復性を最初から設計する",

&#x20;     "チーム拡大時に、業務マニュアルを整備してレプリケーション可能にする",

&#x20;     "商品開発で、1 つのテンプレートから複数バリエーションを効率生産する"

&#x20;   ],

&#x20;   "cautions": \[

&#x20;     "量産化のみに注力すると、初期品質を見落とす可能性がある",

&#x20;     "すべてを標準化しようとすると、創意工夫の余地が失われる",

&#x20;     "コンテキストが異なる場合は、そのまま流用できないことがある"

&#x20;   ]

&#x20; }

}

フィールド詳細

フィールド	型	説明	例

element\_id	string	センターピン ID	"BRAIN\_CENTERPIN\_001"

type	string	知識の種類（FACT / LOGIC / SOP）	"FACT"

content	string	センターピンのコア概念	"量産思考"

base\_purity\_score	float	元々の信頼度スコア	90.0

occurrence\_count	integer	OCR ログでの出現回数	3

importance\_score	float	重要度スコア（occurrence\_count ベース）	3.0

gemini\_expansion.related\_concepts	string\[]	関連概念 3 件	\["スケーラビリティ", ...]

gemini\_expansion.practical\_applications	string\[]	実務応用例 3 件	\["SOP 作成時に...", ...]

gemini\_expansion.cautions	string\[]	注意点 3 件	\["量産化のみに...", ...]

3\. Gemini API 仕様

モデル情報

モデル: gemini-3-pro-preview

API: Google Generative AI

出力形式: JSON（response\_mime\_type: "application/json"）

リトライロジック: 指数バックオフ（最大 3 回、初期待機時間 1～2 秒）

API 初期化コード

Copyimport google.generativeai as genai

import os

from dotenv import load\_dotenv



load\_dotenv()



API\_KEY = os.getenv("GEMINI\_API\_KEY")

MODEL\_ID = os.getenv("GEMINI\_MODEL\_ID", "gemini-3-pro-preview")



if not API\_KEY:

&#x20;   raise ValueError("GEMINI\_API\_KEY は .env ファイルで設定されている必要があります。")



genai.configure(api\_key=API\_KEY)



gen\_model = genai.GenerativeModel(

&#x20;   model\_name=MODEL\_ID,

&#x20;   generation\_config={"response\_mime\_type": "application/json"}

)

プロンプトテンプレート（1 center\_pin ごと）

あなたは日本語話者向けのビジネス講座の補助教材を設計する専門家です。

以下のコンセプトは、この講座の中核となるセンターピンです。



【コンセプト名】

{center\_pin.content}



【概要テキスト（講義スライドから抽出）】

{visual\_text\_excerpt}



このコンセプトについて、次の3つをそれぞれ 3 点ずつ、日本語で箇条書き形式で出力してください。



1\. related\_concepts: このコンセプトと関連する概念・考え方（1行説明付き）



2\. practical\_applications: 実務・日常での具体的な活用例



3\. cautions: 受講者が誤解しやすい点や、実装時の落とし穴



出力は、次の JSON フォーマットに厳密に従ってください：



{

&#x20; "related\_concepts": \["概念1", "概念2", "概念3"],

&#x20; "practical\_applications": \["応用例1", "応用例2", "応用例3"],

&#x20; "cautions": \["注意点1", "注意点2", "注意点3"]

}



余計な文章は書かず、JSON のみを返してください。

API 呼び出し実装

Copyimport time

import json



def \_call\_gemini\_with\_retry(gen\_model, prompt, max\_retries=3, initial\_wait=1):

&#x20;   """

&#x20;   Gemini API を指数バックオフで再試行する

&#x20;   

&#x20;   Args:

&#x20;       gen\_model: GenerativeModel インスタンス

&#x20;       prompt (str): API に送信するプロンプト

&#x20;       max\_retries (int): 最大再試行回数

&#x20;       initial\_wait (int): 初期待機時間（秒）

&#x20;   

&#x20;   Returns:

&#x20;       response: Gemini からの応答

&#x20;   """

&#x20;   for attempt in range(max\_retries):

&#x20;       try:

&#x20;           print(f"Gemini API call (attempt {attempt + 1}/{max\_retries})...")

&#x20;           start\_time = time.time()

&#x20;           

&#x20;           response = gen\_model.generate\_content(prompt)

&#x20;           

&#x20;           elapsed\_time = time.time() - start\_time

&#x20;           print(f"Gemini API response received in {elapsed\_time:.2f}s")

&#x20;           

&#x20;           return response

&#x20;       

&#x20;       except Exception as e:

&#x20;           elapsed\_time = time.time() - start\_time

&#x20;           error\_type = type(e).\_\_name\_\_

&#x20;           print(f"Attempt {attempt + 1} failed ({error\_type}): {str(e)\[:200]}")

&#x20;           

&#x20;           if attempt < max\_retries - 1:

&#x20;               wait\_time = initial\_wait \* (2 \*\* attempt)  # 指数バックオフ

&#x20;               print(f"Retrying in {wait\_time}s...")

&#x20;               time.sleep(wait\_time)

&#x20;           else:

&#x20;               print(f"All {max\_retries} attempts failed.")

&#x20;               raise



\# 使用例

response = \_call\_gemini\_with\_retry(gen\_model, prompt)

expansion\_data = json.loads(response.text)

Copy

4\. 実装フロー

Step 1: TOP 5 center\_pin を抽出

CopySELECT element\_id, type, content, base\_purity\_score, occurrence\_count, importance\_score

FROM knowledge\_core

WHERE lecture\_id = '01'

ORDER BY importance\_score DESC

LIMIT 5

Step 2: 各 center\_pin について visual\_text 関連部分を取得

CopySELECT visual\_text

FROM evidence\_index

WHERE element\_id IN (top 5 center\_pin IDs)

ORDER BY importance\_score DESC

LIMIT 2-3

Step 3: Gemini API に送信

1 center\_pin = 1 リクエスト

JSON レスポンスを gemini\_expansion に格納

Step 4: insight\_spec\_01.json の knowledge\_core を更新

Copy{

&#x20; "knowledge\_core": \[

&#x20;   {

&#x20;     "element\_id": "BRAIN\_CENTERPIN\_001",

&#x20;     ...

&#x20;     "gemini\_expansion": { ... }

&#x20;   },

&#x20;   ...

&#x20; ]

}

5\. API クォータ管理

Gemini 3 Pro のレートリミット

RPM (Requests Per Minute): 環境・プラン依存

TPM (Tokens Per Minute): 環境・プラン依存

RPD (Requests Per Day): 無制限（通常）

初期実装戦略（「小さく試す」フェーズ）

Brain マーケティング講座 1 本分（TOP 5 center\_pin）をテスト実行

レスポンス品質、生成時間、トークン消費量を検証

必要に応じてバッチ処理や response\_schema を導入

バッチ化の例（将来の最適化）

Copy# 複数 center\_pin を 1 リクエストで処理

request\_payload = {

&#x20; "center\_pins": \[

&#x20;   {"element\_id": "...", "content": "...", "visual\_text": "..."},

&#x20;   {"element\_id": "...", "content": "...", "visual\_text": "..."},

&#x20;   ...

&#x20; ]

}



\# response\_schema で、配列 JSON を返させる

response\_schema = {

&#x20; "type": "array",

&#x20; "items": {

&#x20;   "type": "object",

&#x20;   "properties": {

&#x20;     "element\_id": {"type": "string"},

&#x20;     "gemini\_expansion": {...}

&#x20;   }

&#x20; }

}

6\. 実装ファイル（予定）

converter/gemini\_knowledge\_expander.py



GeminiKnowledgeExpander クラス

expand\_center\_pin(center\_pin, visual\_text) -> Dict

expand\_all\_center\_pins(insight\_spec\_path, top\_n=5) -> Dict

tests/test\_gemini\_knowledge\_expander.py



Gemini API モック

出力 JSON スキーマ検証

エラーハンドリングテスト

expand\_insight\_spec\_with\_gemini.py



スタンドアロンスクリプト

insight\_spec\_01.json に gemini\_expansion を追加

7\. 品質チェック（検証項目）

JSON スキーマ検証

gemini\_expansion の 3 つのフィールド（related\_concepts, practical\_applications, cautions）が存在

各フィールドが 3 件の文字列配列

コンテンツ検証

日本語で記述されていること

1 行 50 文字以上（不自然な短さでないこと）

元の center\_pin.content と関連性があること

API エラーハンドリング

API キーがない → エラーメッセージ出力

レート制限に達した → リトライロジック

JSON パースエラー → ログ記録 + スキップ

8\. 環境変数設定（.env）

CopyGEMINI\_API\_KEY=<実際のキーを設定>

GEMINI\_MODEL\_ID=gemini-3-pro-preview

ARCHIVE\_DIR=D:\\Knowledge\_Base\\Brain\_Marketing\\archive

9\. 次ステップ

.env に GEMINI\_API\_KEY と GEMINI\_MODEL\_ID を追加

GeminiKnowledgeExpander 実装

insight\_spec\_01.json で試験実行

生成結果の品質確認

全講義（01～21）への展開を検討

参考資料

Google Generative AI SDK（Python）

Gemini API リファレンス

JSON Mode

