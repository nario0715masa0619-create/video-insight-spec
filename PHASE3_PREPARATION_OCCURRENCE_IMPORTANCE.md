\# PHASE3\_PREPARATION\_OCCURRENCE\_IMPORTANCE.md



\## Phase 3 準備: occurrence\_count \& importance\_score



\### 概要

Phase 3（Gemini API による知識点自動拡張）に向けた準備フェーズです。OCR テキストの出現回数をベースに、重要度スコアを計算し、Gemini API への入力時に優先順位付けに使用します。



\### スキーマ変更



`evidence\_index` テーブルに以下のカラムを追加：



| カラム名 | 型 | デフォルト | 説明 |

|---------|-----|---------|------|

| `occurrence\_count` | INTEGER | 0 | クリーニング済みテキストが OCR ログ内で出現した回数 |

| `importance\_score` | REAL | 0.0 | 重要度スコア（暫定: occurrence\_count と同値） |



\### 実装仕様



\#### 1. occurrence\_count 集計

1\. `evidence\_index` から全ての `visual\_text` (NOT NULL, != '') を取得

2\. クリーニング済みテキストごとに出現回数をカウント（Counter）

3\. 各レコードの `occurrence\_count` に該当カウント数を格納



\#### 2. importance\_score 計算



暫定ルール（Phase 3 実装時に改善予定）:



importance\_score = occurrence\_count



つまり：

\- 出現 1 回 → importance\_score = 1.0

\- 出現 5 回 → importance\_score = 5.0

\- 出現 10 回 → importance\_score = 10.0



\#### 3. Phase 3 での活用予定

Gemini API に複数のセンターピンテキストを送信する際：

1\. `importance\_score` でソート（降順）

2\. 重要度の高いテキストから優先的にプロンプトに含める

3\. トークン数制限がある場合、低スコアテキストは除外



\### 実装ファイル

\- `add\_importance\_schema.py` - スキーマ追加スクリプト

\- `calculate\_occurrence\_and\_importance.py` - 出現回数集計・スコア計算スクリプト



\### 実行手順



```bash

\# Step 1: スキーマ更新

python add\_importance\_schema.py



\# Step 2: occurrence\_count \& importance\_score 集計

python calculate\_occurrence\_and\_importance.py



\# Step 3: テスト実行

pytest tests/ -v



統計情報例

総レコード数（occurrence > 0）: 10

平均 occurrence\_count: 2.1

最大 occurrence\_count: 5



次フェーズ（Phase 3）への継承

importance\_score を利用して、Gemini API へのプロンプト構築時に優先順位付けを実施

低スコアテキストの除外またはグループ化

知識点自動拡張の精度向上



