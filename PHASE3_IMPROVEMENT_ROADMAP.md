\# Phase 3 改善ロードマップ



\*\*作成日\*\*: 2026-03-24  

\*\*評価元\*\*: Perplexity AI  

\*\*対象\*\*: GeminiKnowledgeLabeler（Phase 3 実装）



\---



\## 現状評価



\### 強み

\- シンプルでわかりやすい実装

\- リトライロジック（指数バックオフ）が適切

\- JSON モード（response\_mime\_type）を活用

\- テストカバレッジが充実（15/15 PASS）

\- 実試験で正常に動作確認済み（insight\_spec\_01.json ラベル付与成功）



\### 課題

\- 責務が一つのクラスに集中（API・プロンプト・I/O・バリデーション）

\- モデル固定（Gemini のみ）→ Claude/OpenAI への切り替えが困難

\- ラベルスキーマがハードコード → 変更時にソース修正必須

\- エラーハンドリングが簡潔すぎる → スキップされたレコードが追跡困難

\- 複数言語対応が考慮されていない



\---



\## Phase 3.1 改善（短期・優先度高）



\### 1. アーキテクチャ分離（責務分離）

\*\*課題\*\*: GeminiKnowledgeLabeler が以下を同時に処理している

\- API クライアント初期化

\- プロンプト生成

\- モデル呼び出し（リトライ）

\- JSON パース＆スキーマ検証

\- insight\_spec 読み書き

\- TOP N 抽出



\*\*改善案\*\*:



新しいクラス設計： ├── CenterPinLabelingService │ └── label\_center\_pin(center\_pin) → labels dict を返す純粋サービス ├── InsightSpecRepository │ ├── load(path) → insight\_spec dict │ └── save(insight\_spec, path) → bool ├── CenterPinSelector │ └── select\_top\_n(center\_pins, top\_n) → List\[CenterPin] └── GeminiKnowledgeLabeler（統合） └── label\_insight\_spec\_file(input\_path, output\_path, top\_n)





\*\*見積もり\*\*: 4～5 時間  

\*\*優先度\*\*: ⭐⭐⭐ (高)  

\*\*メリット\*\*: モデル切り替え・入出力仕様変更が局所的に対応可能



\---



\### 2. Pydantic によるスキーマバリデーション

\*\*課題\*\*: 自前の `\_validate\_labels()` メソッドが型変換・制約を全部手で書いている



\*\*改善案\*\*:

```python

from pydantic import BaseModel, conlist

from typing import Literal



class Labels(BaseModel):

&#x20;   business\_theme: conlist(str, min\_items=1, max\_items=3)

&#x20;   funnel\_stage: str

&#x20;   difficulty: Literal\["beginner", "intermediate", "advanced"]



&#x20;   class Config:

&#x20;       frozen = True



\# 使用時

try:

&#x20;   labels = Labels(\*\*response\_json\["labels"])

except ValidationError as e:

&#x20;   logger.error(f"Validation failed: {e.json()}")

見積もり: 2～3 時間

優先度: ⭐⭐⭐ (高)

メリット: 型安全性向上、エラーメッセージが明確化



3\. エラートレーサビリティ向上

課題: バリデーション失敗時に「静かにスキップ」される → どの center\_pin が失敗したかが追跡困難



改善案:



Copy# 方案 A: エラー情報を center\_pin に埋め込む

center\_pin\["labels\_error"] = {

&#x20;   "type": "validation\_error",

&#x20;   "message": "business\_theme must have 1-3 items"

}



\# 方案 B: 別ファイルに失敗ログを記録

error\_log = {

&#x20;   "element\_id": "BRAIN\_CENTERPIN\_001",

&#x20;   "error\_type": "json\_decode\_error",

&#x20;   "error\_message": "...",

&#x20;   "timestamp": "2026-03-24T19:11:31Z"

}

\# append to error\_log.jsonl



\# 方案 C: 返り値に status フィールドを持たせる

center\_pin\["labels"] = {

&#x20;   "status": "error",

&#x20;   "error": "validation\_failed",

&#x20;   "message": "..."

}

見積もり: 1～2 時間

優先度: ⭐⭐⭐ (高)

メリット: 後処理で「どの center\_pin が未ラベルか」を簡単に追跡可能



4\. 破壊的変更の明示化

課題: label\_insight\_spec() が入力の dict をインプレース変更している → 呼び出し側が意図せず上書きされる可能性



改善案:



Copydef label\_insight\_spec(self, insight\_spec: Dict, top\_n: int = 5, copy: bool = True) -> Dict:

&#x20;   """

&#x20;   center\_pins にラベルを付与する

&#x20;   

&#x20;   Args:

&#x20;       insight\_spec: 入力 JSON

&#x20;       top\_n: 対象件数

&#x20;       copy: True の場合、新しい dict を返す（元の dict は変更しない）

&#x20;   

&#x20;   Returns:

&#x20;       ラベル付与済みの JSON dict

&#x20;   

&#x20;   Warning:

&#x20;       copy=False の場合、このメソッドは insight\_spec をインプレースで変更します

&#x20;   """

&#x20;   result = copy.deepcopy(insight\_spec) if copy else insight\_spec

&#x20;   # ... 処理

&#x20;   return result

見積もり: 30 分～1 時間

優先度: ⭐⭐ (中)

メリット: ドキュメント化により、バグを未然防止



Phase 3.2 改善（中期・拡張性）

5\. LLM クライアント層の抽象化

課題: Gemini に固定されている → Claude/OpenAI への切り替えが困難



改善案:



Copyfrom typing import Protocol



class LLMClientProtocol(Protocol):

&#x20;   """LLM クライアントのインターフェース"""

&#x20;   def generate\_json(self, prompt: str, schema: Optional\[dict] = None) -> dict:

&#x20;       ...



class GeminiClient(LLMClientProtocol):

&#x20;   def \_\_init\_\_(self, api\_key: str, model\_id: str = "gemini-3-pro-preview"):

&#x20;       ...

&#x20;   

&#x20;   def generate\_json(self, prompt: str, schema: Optional\[dict] = None) -> dict:

&#x20;       # Gemini 固有の実装



class ClaudeClient(LLMClientProtocol):

&#x20;   # 将来: Claude 用の実装



class CenterPinLabelingService:

&#x20;   def \_\_init\_\_(self, llm\_client: LLMClientProtocol):

&#x20;       self.llm = llm\_client

&#x20;   

&#x20;   def label\_center\_pin(self, center\_pin: dict) -> dict:

&#x20;       # llm\_client に依存 → モデル切り替え可能

見積もり: 3～4 時間

優先度: ⭐⭐⭐ (高・将来の差し替え需要が高い)

メリット: Claude/OpenAI への乗り換え時に変更最小化



6\. Label Schema の外出し（JSON ファイル化）

課題: ラベル軸（business\_theme / funnel\_stage / difficulty）がプロンプト内にハードコード



改善案:



Copy// config/label\_schema.json

{

&#x20; "language": "ja",

&#x20; "axes": \[

&#x20;   {

&#x20;     "name": "business\_theme",

&#x20;     "type": "multi\_choice",

&#x20;     "min\_items": 1,

&#x20;     "max\_items": 3,

&#x20;     "choices": \[

&#x20;       "マーケティング",

&#x20;       "セールス",

&#x20;       "プロダクト",

&#x20;       "組織",

&#x20;       "マインドセット",

&#x20;       "オペレーション",

&#x20;       "財務"

&#x20;     ]

&#x20;   },

&#x20;   {

&#x20;     "name": "funnel\_stage",

&#x20;     "type": "single\_choice",

&#x20;     "choices": \[

&#x20;       "認知",

&#x20;       "興味・関心",

&#x20;       "教育",

&#x20;       "比較検討",

&#x20;       "クロージング",

&#x20;       "継続・LTV"

&#x20;     ]

&#x20;   },

&#x20;   {

&#x20;     "name": "difficulty",

&#x20;     "type": "single\_choice",

&#x20;     "choices": \["beginner", "intermediate", "advanced"]

&#x20;   }

&#x20; ]

}

Copy

Copyfrom pydantic import BaseModel

from typing import List, Literal



class LabelAxis(BaseModel):

&#x20;   name: str

&#x20;   type: Literal\["single\_choice", "multi\_choice", "free\_text"]

&#x20;   min\_items: Optional\[int] = None

&#x20;   max\_items: Optional\[int] = None

&#x20;   choices: Optional\[List\[str]] = None



class LabelSchema(BaseModel):

&#x20;   language: str

&#x20;   axes: List\[LabelAxis]



\# 使用時

schema = LabelSchema.parse\_file("config/label\_schema.json")

labeler = CenterPinLabelingService(llm\_client, label\_schema=schema)

見積もり: 2～3 時間

優先度: ⭐⭐⭐ (高・顧客ごとのカスタマイズ需要)

メリット:



ラベル軸を JSON で管理 → ソース修正不要

複数顧客対応が容易

A/B テスト（異なるスキーマ）が実施可能

7\. 複数言語対応

課題: プロンプトが日本語専用 → 英語チャンネルに対応できない



改善案:



Copyclass CenterPinLabelingService:

&#x20;   def \_\_init\_\_(

&#x20;       self,

&#x20;       llm\_client: LLMClientProtocol,

&#x20;       label\_schema: LabelSchema,

&#x20;       language: str = "ja"  # "en", "zh" 対応予定

&#x20;   ):

&#x20;       self.language = language

&#x20;       self.schema = label\_schema



&#x20;   def \_build\_labeling\_prompt(self, center\_pin: dict) -> str:

&#x20;       if self.language == "ja":

&#x20;           system\_prompt = "あなたは、日本語話者向けビジネス講座の内容を分類するアナリストです。"

&#x20;       elif self.language == "en":

&#x20;           system\_prompt = "You are an analyst classifying content for English-speaking business courses."

&#x20;       # ... スキーマから動的に選択肢を生成

見積もり: 2～3 時間

優先度: ⭐⭐ (中・将来の需要次第)

メリット: グローバル対応が可能



8\. バッチ処理による API コスト最適化

課題: 現状は 1 center\_pin ごとに 1 API 呼び出し → 5 件なら 5 回呼び出し



改善案:



Copy# 5〜10 件まとめて処理

def label\_center\_pins\_batch(

&#x20;   self,

&#x20;   center\_pins: List\[dict],

&#x20;   batch\_size: int = 5

) -> List\[dict]:

&#x20;   """

&#x20;   複数 center\_pins をバッチ処理

&#x20;   

&#x20;   Args:

&#x20;       center\_pins: center\_pins リスト

&#x20;       batch\_size: 1 リクエストあたりの件数

&#x20;   

&#x20;   Returns:

&#x20;       ラベル付与済み center\_pins

&#x20;   """

&#x20;   batches = \[center\_pins\[i:i+batch\_size] for i in range(0, len(center\_pins), batch\_size)]

&#x20;   results = \[]

&#x20;   

&#x20;   for batch in batches:

&#x20;       batch\_prompt = self.\_build\_batch\_prompt(batch)

&#x20;       response\_json = self.llm.generate\_json(batch\_prompt)

&#x20;       # response: { "labels": \[{"element\_id": "...", "labels": {...}}, ...] }

&#x20;       results.extend(response\_json\["labels"])

&#x20;   

&#x20;   return results

見積もり: 3～4 時間

優先度: ⭐⭐ (中・API コスト削減の需要次第)

メリット: API 呼び出し 80% 削減、コスト節約



9\. キャッシング機構の追加

課題: 同じ element\_id に対して再度ラベル付けするのは無駄



改善案:



Copyclass LabelCache:

&#x20;   def \_\_init\_\_(self, cache\_path: str = "cache/label\_cache.json"):

&#x20;       self.cache\_path = cache\_path

&#x20;       self.cache = self.\_load\_cache()

&#x20;   

&#x20;   def get(self, element\_id: str) -> Optional\[dict]:

&#x20;       return self.cache.get(element\_id)

&#x20;   

&#x20;   def set(self, element\_id: str, labels: dict):

&#x20;       self.cache\[element\_id] = labels

&#x20;       self.\_save\_cache()

&#x20;   

&#x20;   def \_load\_cache(self) -> dict:

&#x20;       if Path(self.cache\_path).exists():

&#x20;           return json.loads(Path(self.cache\_path).read\_text())

&#x20;       return {}

&#x20;   

&#x20;   def \_save\_cache(self):

&#x20;       Path(self.cache\_path).parent.mkdir(parents=True, exist\_ok=True)

&#x20;       Path(self.cache\_path).write\_text(json.dumps(self.cache, ensure\_ascii=False, indent=2))



\# 使用時

cache = LabelCache()

if cached\_labels := cache.get(center\_pin\["element\_id"]):

&#x20;   center\_pin\["labels"] = cached\_labels

else:

&#x20;   labels = self.label\_center\_pin(center\_pin)

&#x20;   cache.set(center\_pin\["element\_id"], labels)

見積もり: 1～2 時間

優先度: ⭐⭐ (中・再実行時の効率化)

メリット: 再実行時のコスト/時間が大幅削減



テスト拡充計画（Phase 3.3）

現状テスト

✅ 15/15 PASS（Unit テスト）

❌ 統合テスト（実際の insight\_spec JSON との連携）

❌ エッジケーステスト（大規模データセット、API エラー）

追加すべきテスト

単体テスト

\_validate\_labels() の全パターン（正常系・異常系）

\_call\_gemini\_with\_retry() のリトライ動作

複数言語プロンプト生成

Schema バリデーション（Pydantic）

統合テスト

実際の insight\_spec JSON（小規模）での end-to-end テスト

キャッシュの動作確認

バッチ処理の動作確認

パフォーマンステスト

100 件の center\_pins を処理した場合の時間測定

メモリ使用量の確認

API レート制限への対応

見積もり: 5～7 時間

優先度: ⭐⭐⭐ (高・品質保証のため)



実装優先順序（推奨）

即座（次回対応）

✅ Phase 3.1-1: アーキテクチャ分離

✅ Phase 3.1-2: Pydantic バリデーション

✅ Phase 3.1-3: エラートレーサビリティ

短期（1～2 週間後）

✅ Phase 3.2-5: LLM クライアント抽象化

✅ Phase 3.2-6: Label Schema の外出し

✅ テスト拡充

中期（1 ヶ月後）

🔄 Phase 3.2-7: 複数言語対応

🔄 Phase 3.2-8: バッチ処理

🔄 Phase 3.2-9: キャッシング

関連ドキュメント

PHASE3\_GEMINI\_KNOWLEDGE\_EXPANSION.md - Phase 3 設計仕様書

converter/gemini\_knowledge\_expander.py - 現実装

tests/test\_gemini\_knowledge\_labeler.py - 現テスト

メモ

Perplexity 評価日: 2026-03-24

実試験実行結果: ✅ insight\_spec\_01.json ラベル付与成功（TOP 5 件）

次回レビュー予定日: TBD

