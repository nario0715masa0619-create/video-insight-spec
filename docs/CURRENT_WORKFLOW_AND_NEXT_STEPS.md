# 「3. 運用の手作業感」– 現在のあなたの作業フロー

## 問題: 実装完了後、「では毎月何をするのか」が不明確

---

## 現在の状況（Phase 7 完了時点）

### ファイル構成
\\\
config/
  └─ scoring_rules.json (v2.2, 39 mappings)

scripts/
  ├─ quality_scoring_engine.py
  ├─ apply_scoring_to_insights.py
  ├─ gemini_clustering.py
  ├─ embedding_mapper.py
  ├─ generate_statistics.py
  └─ generate_executive_report.py

results/
  ├─ summary.json (最新スコア)
  └─ insight_spec_*_scored.json (各ファイルのスコア詳細)

data/
  ├─ final_statistics_report.json
  └─ executive_report.json
\\\

---

## 現在あなたが手動でしている 3 つのこと

### 1️⃣ Unmapped テーマの発見

**現在の方法**
\\\powershell
# results/*.json を開いて、手動で「unmapped」を探す
Get-Content results/insight_spec_01_scored.json | Select-String "unmapped"

# または
 = Get-Content results/insight_spec_02_scored.json | ConvertFrom-Json
 = .score_details.normalization_log | 
  Where-Object { .source -eq "unmapped" }
\\\

**問題点**
- ❌ 毎回 6 つのファイル全て手動でチェック
- ❌ 新しいテーマが出現したかどうか、前月との比較が面倒
- ❌ 「新規テーマが X 個出た」という記録がない

**あなたが実際にやること**
\\\
毎月初日（例）
  ↓
「さて、先月新しいテーマが出たか確認するか」
  ↓
results/*.json を 6 個開く
  ↓
各ファイルの normalization_log を眺める
  ↓
「あ、コンテンツ制作がまだ unmapped だ」← 前月からの変化が判らない
  ↓
data/unmapped_themes.json に手動で記入
  ↓
data/unmapped_themes.json を Gemini に渡す
  ↓
（待ってから）Gemini の結果を見て、config を手動更新
\\\

---

### 2️⃣ Mapping 修正（JSON 手動編集）

**現在の方法**
\\\powershell
# config/scoring_rules.json を手動で開く（テキストエディタ）
code config/scoring_rules.json

# 例: 「広告運用」を カスタマーサクセス → マーケティング に修正
# {
#   "raw_theme": "広告運用",
#   "canonical": "マーケティング",  ← これを手動で変更
#   "cluster": "digital_marketing",
#   "confidence": 0.85
# }

# 保存して PowerShell で確認
 = Get-Content config/scoring_rules.json | ConvertFrom-Json
.theme_normalization.cluster_mapping | 
  Where-Object { .raw_theme -eq "広告運用" }
\\\

**問題点**
- ❌ JSON のシンタックスエラーのリスク（括弧の不一致など）
- ❌ 修正履歴が Git commit に埋もれる（どの mapping をいつ変えたのか追跡困難）
- ❌ 複数の修正が同時に発生したときの衝突管理が不明確

**あなたが実際にやること**
\\\
「OK、Gemini の結果をもらった」
  ↓
config/scoring_rules.json をエディタで開く
  ↓
cluster_mapping セクションを探す
  ↓
新しいマッピングを 1 つずつ JSON に追加
  ↓
括弧・コンマのチェック（エラーが出ないか）
  ↓
PowerShell で JSON parse して正当性確認
  ↓
git add → git commit
  ↓
apply_scoring_to_insights.py を再実行
\\\

---

### 3️⃣ 定期監視（スクリプト実行 → ファイル確認）

**現在の方法**
\\\powershell
# 毎月、手動で以下を実行

# Step 1: スコアリング再実行
python scripts/apply_scoring_to_insights.py

# Step 2: 統計生成
python scripts/generate_statistics.py

# Step 3: レポート生成
python scripts/generate_executive_report.py

# Step 4: 手動で結果を確認
 = Get-Content data/final_statistics_report.json | ConvertFrom-Json
Write-Host "Avg semantic_purity: "
Write-Host "Unmapped: "

 = Get-Content data/executive_report.json | ConvertFrom-Json
Write-Host "Status: "
Write-Host "Quality Score: "
\\\

**問題点**
- ❌ 毎月同じコマンドを 3 つ実行（自動化されていない）
- ❌ 結果がスクリーンに出るだけで記録されない
- ❌ 「先月と比べて semantic_purity は上がったのか下がったのか」が判らない（比較データがない）
- ❌ drift（低下）を検知できない

**あなたが実際にやること**
\\\
毎月 1 日の朝
  ↓
PowerShell を開く
  ↓
3 つのスクリプトを順番に実行
  ↓
結果ファイルを開いて、数値をスプレッドシートに手動入力
  ↓
「今月は semantic_purity 0.61 で前月と同じか」
  ↓
ビジネスユーザーに Slack/Email で連絡
  ↓
（もし数値が低かったら）「何が原因か」を手動で調査
\\\

---

## 「自動化されていない」ことの具体的な影響

### シナリオ 1: 新規テーマが出現した場合

**現在（手動）**
\\\
2026-05-15
  新しい insight_spec ファイルが入ってくる
    ↓
  「あ、新規テーマあるのかな」
    ↓
  apply_scoring_to_insights.py を走す
    ↓
  results/ を確認
    ↓
  「あ、"SEO 動画制作" が unmapped だ」
    ↓
  data/unmapped_themes.json に手動で追加
    ↓
  「Gemini で classify するか」
    ↓
  Gemini API を手動でコール
    ↓
  結果を確認
    ↓
  config/scoring_rules.json を手動編集
    ↓
  git add → git commit
    ↓
  再度 apply_scoring_to_insights.py
    ↓
  2026-05-16（翌日に完了）
\\\

**自動化後**
\\\
2026-05-15
  新しい insight_spec ファイルが入ってくる
    ↓
  [自動] cron job が夜間に実行
    ↓
  [自動] auto_detect_new_unmapped.py が新規テーマを検出
    ↓
  [自動] Slack alert: "新規 unmapped テーマ 1 件: SEO 動画制作"
    ↓
  [自動] data/new_unmapped.json に記録
    ↓
  2026-05-16 朝、あなたが確認
    ↓
  「あ、新規テーマ 1 個出たんだ」
    ↓
  Gemini clustering を手動トリガー（または自動）
    ↓
  config 更新
    ↓
  [自動] 再スコアリング＆レポート生成
\\\

---

## 「3. 運用の手作業感」の正体

### あなたが毎月すべきこと（理想形）

\\\
毎月 1 日 09:00
  ↓
「先月の summary を確認しよう」
  ↓
Dashboard を開く（Streamlit）
  ↓
「あ、semantic_purity 0.62（+0.01 from 先月）」
  ↓
「unmapped テーマ 0（stable）」
  ↓
「新規テーマなし」
  ↓
→ 何もしない、完了
\\\

vs

\\\
毎月 1 日 09:00
  ↓
「先月の summary を確認しよう」
  ↓
PowerShell で 3 つのスクリプトを実行
  ↓
JSON ファイルを 5 個開く
  ↓
数値をメモして比較
  ↓
「あ、semantic_purity が 0.61 → 0.58 に下がった」
  ↓
「何が原因だ？」
  ↓
各 insight_spec を手動で確認
  ↓
「insight_spec_02 の 1 つのテーマが unmapped になった」
  ↓
data/unmapped_themes.json に追加
  ↓
Gemini を手動でコール
  ↓
...（以下延々と手作業）
\\\

---

## 「自動化」の内訳

### 現在あなたが「毎月手動でしている」タスク

| # | タスク | 所要時間 | 自動化で削減 |
|---|---|---|---|
| 1 | unmapped テーマの検出 | 15 分 | ✅ 5 分（Slack alert だけ確認） |
| 2 | Gemini clustering（手動コール） | 10 分 | ✅ 5 分（自動実行 + 確認） |
| 3 | config/scoring_rules.json 手動編集 | 20 分 | ✅ 10 分（API で自動更新） |
| 4 | apply_scoring_to_insights.py 実行 | 5 分 | ✅ 0 分（自動実行） |
| 5 | 統計・レポート生成（手動実行） | 10 分 | ✅ 0 分（自動実行） |
| 6 | 結果ファイルを開いて確認 | 20 分 | ✅ 5 分（Dashboard で確認） |
| 7 | ビジネスユーザーへの報告 | 15 分 | ✅ 5 分（自動配信） |
| **合計** | | **95 分** | **30 分（68% 削減）** |

---

## では「次のステップ」で実装すべき機能（優先度順）

### Phase 3-1: 自動 Drift Detection ⭐⭐⭐ 最優先

**何をするのか**

\\\python
# scripts/monitor_semantic_purity.py

def monthly_check():
    \"\"\"
    毎月 1 日 09:00 に cron で自動実行
    \"\"\"
    
    # Step 1: 前月の semantic_purity を取得
    previous_avg = load_from_history('2026-04-01', 'avg_semantic_purity')  # 0.61
    
    # Step 2: 今月の semantic_purity を取得
    current_stats = run_generate_statistics()  # avg = ?
    current_avg = current_stats['summary']['avg_semantic_purity']
    
    # Step 3: 比較
    if current_avg < previous_avg - 0.05:  # 5% 低下
        # Alert
        send_slack_alert(f"⚠️ semantic_purity が {previous_avg} → {current_avg} に低下しました")
    
    elif current_avg > previous_avg + 0.02:  # 2% 向上
        send_slack_alert(f"✅ semantic_purity が {previous_avg} → {current_avg} に向上しました")
    
    else:
        send_slack_alert(f"📊 semantic_purity {current_avg}（前月比 {current_avg - previous_avg:+.2f}）")
\\\

**あなたが するコト**
- コマンドを手動で 3 つ実行 → **1 つの Slack message を見るだけ**

**期待効果**
- semantic_purity の低下を **即座に検知**
- 「先月と今月どっちが良い？」が自動判定される
- 異常を見逃さない

---

### Phase 3-2: 自動 Unmapped Detection ⭐⭐⭐ 最優先

**何をするのか**

\\\python
# scripts/auto_detect_new_unmapped.py

def daily_check():
    \"\"\"
    毎日（または新規ファイル投入時に）自動実行
    \"\"\"
    
    # Step 1: 今月のすべての insight_spec を load
    current_insights = load_all_insights()
    
    # Step 2: 前月の mapping と比較
    previous_mapping = load_config_version('v2.2')
    
    # Step 3: 新規 unmapped テーマを検出
    new_unmapped = []
    for insight in current_insights:
        for theme in extract_themes(insight):
            if theme not in previous_mapping['cluster_mapping']:
                new_unmapped.append(theme)
    
    # Step 4: 新規テーマがあれば alert
    if new_unmapped:
        send_slack_alert(f"🆕 新規 unmapped テーマ {len(new_unmapped)} 件: {new_unmapped}")
        # data/new_unmapped_themes.json に自動保存
\\\

**あなたが するコト**
- 「新規テーマ 3 個出た」という Slack message を見る
- 必要に応じて Gemini clustering をトリガー

**期待効果**
- 新規テーマの発見が **自動化**
- 「先月はあったのに今月ないテーマ」も自動追跡
- data/unmapped_themes.json に自動更新

---

### Phase 3-3: 自動 Monthly Report ⭐⭐⭐ 最優先

**何をするのか**

\\\python
# scripts/generate_monthly_report.py

def generate_monthly_summary():
    \"\"\"
    毎月 1 日に cron で自動実行 → 最終成果物を Email で送信
    \"\"\"
    
    report = {
        'month': '2026-05',
        'summary': {
            'avg_semantic_purity': 0.62,
            'change_from_prev_month': '+0.01',
            'new_unmapped_detected': 2,
            'new_mappings_added': 3
        },
        'key_insights': [
            'insight_spec_02 が 0.53 → 0.55 に改善',
            '新規テーマ「SEO 動画」が出現、Gemini で classify 予定',
            '全ファイル unmapped = 0 を維持'
        ],
        'recommended_actions': [
            'insight_spec_05 (0.44) の詳細レビュー',
            '新規 unmapped 2 個を Phase 2 clustering で処理'
        ]
    }
    
    # HTML 形式で Email送信
    send_email_report(
        to='business_team@company.com',
        subject=f'[Quality Scoring] Monthly Summary - {report["month"]}',
        html=render_html(report)
    )
\\\

**あなたが するコト**
- Email で「先月の summary」が自動配信される
- ビジネスユーザーに報告済み
- 手作業ゼロ

**期待効果**
- ビジネスユーザーへの報告が **全自動**
- Executive team が dashboard を開くだけで状況が判る

---

### Phase 3-4: Web Dashboard（オプション）⭐⭐ 二次優先

**何をするのか**

\\\
Web ブラウザで以下が見られる

📊 Summary
  - Avg Semantic Purity: 0.61 (↑ +0.01 from prev month)
  - Quality Score: 0.71
  - Unmapped Rate: 0%
  - Config Version: v2.2

📈 File-wise Scores
  - insight_spec_01: 0.65 ✅ Good
  - insight_spec_02: 0.55 ⚠️ Mixed
  - insight_spec_03: 0.55 ⚠️ Mixed
  - insight_spec_04: 0.75 ✅ Good
  - insight_spec_05: 0.44 ⚠️ Poor
  - insight_spec_mirirepi: 0.76 ✅ Good

📊 Canonical Distribution
  - Pie chart: マーケティング 68%, 分析 13%, ...

📅 Trend Analysis
  - 過去 6 ヶ月の semantic_purity 推移グラフ
  - Unmapped テーマ数の推移

⚙️ Config Status
  - v2.2 details
  - 最新 changelog
\\\

**あなたが するコト**
- Dashboard URL を開いて確認
- スクリプト実行なし、JSON ファイル見なし

**期待効果**
- 視覚的に状況把握が容易
- ビジネスユーザーも自助で確認可能

---

## まとめ: 「次のステップで実装すべき」の正体

### 現在（Phase 7 完了時）

\\\
毎月: 
  ❌ 3 つのスクリプトを手動実行
  ❌ 5 個の JSON ファイルを手動確認
  ❌ 新規テーマを手動検出
  ❌ Gemini を手動コール
  ❌ config を手動編集
  ❌ ビジネスユーザーへ手動報告
  → 所要時間: 約 2 時間/月
\\\

### Phase 3 導入後（目標形）

\\\
毎月 1 日朝:
  ✅ Slack notification で「先月の summary」が自動配信
  ✅ 新規テーマは「自動検出 + alert」
  ✅ drift（低下）は「自動検知 + alert」
  ✅ Dashboard で「ビジネスユーザーが自分で確認」
  → あなたの所要時間: 約 15 分/月（alert を確認 + 必要に応じて対応）
\\\

### あなたが「毎月すべきこと」（Phase 3 導入後）

\\\
毎月 1 日 09:00
  1. Slack 通知を確認 ← ✅ 自動
  2. 「今月は semantic_purity 0.62（+0.01）です」と読む
  3. 新規 unmapped テーマがあれば
     → Gemini clustering をトリガー（手動、5 分）
     → config を API で自動更新（自動）
     → 再スコアリング（自動）
  4. ビジネスユーザーに「先月の summary」を報告
     → Email で自動配信済み（確認するだけ）
\\\

---

## 実装の優先度

### 🔴 Phase 3-1, 2: 自動 Drift Detection + Unmapped Detection
- **理由**: 現在最も時間がかかっている（60 分/月削減）
- **期待 ROI**: 実装 2 週間 vs 月 1 時間削減 → 12 ヶ月で元が取れる
- **実装**: scripts/ に 2 つのスクリプト追加 + cron job 設定

### 🟡 Phase 3-3: Monthly Report
- **理由**: ビジネスユーザーへの報告が自動化（15 分削減）
- **期待 ROI**: 実装 1 週間 vs 月 15 分削減 + ビジネス価値（定期レポート）
- **実装**: scripts/ に 1 つのスクリプト追加 + Email 設定

### 🟡 Phase 3-4: Dashboard
- **理由**: ビジネスユーザーの自助分析（質問対応削減）
- **期待 ROI**: 実装 2 週間 vs「質問が減る」という定性的効果
- **実装**: scripts/dashboard.py (Streamlit) + 定期デプロイ

---

**つまり、あなたが「次のステップで何をすればいいのか」は：**

1. **今は何もしない**
2. **Phase 3 を実装するまで** → 毎月 2 時間は手作業が続く
3. **Phase 3-1, 2 が完成したら** → 毎月 15 分で済む
4. **Phase 3-3 が完成したら** → ほぼ自動、alert 確認のみ

### ?? ���o�b�N���O: load_executive_report() �̃o���f�[�V�����E�t�H�[���o�b�N����
- **�D��x**: Medium (�^�p���萫����E�}�[�W�u���b�J�[�ł͂Ȃ�)
- **�w�i**: PR #27 �ɂāA\executive_report.json\ �ւ̋��ˑ���p�~���A�s�ݎ�/JSON�j�����ɂ� \insight_spec_*.json\ ���玩���ōďW�v������S�݌v�i�t�H�[���o�b�N�j�𓱓����܂����B
- **���**: ���݂̃t�H�[���o�b�N�̃g���K�[�� \FileNotFoundError\ �� \JSONDecodeError\ �Ɍ��肳��Ă��܂��B���̂��߁AJSON �Ƃ��Ă͐����� \{}\ ��A\lectures\ �����݂��Ȃ��E�\�����s���Ȃ܂܂̃t�@�C�����c�����Ă���ꍇ�A�ďW�v�ɉ�炸��f�[�^���̋����ɂȂ�܂��B
- **���҂�����P**: �t�@�C���̑��݁EJSON �̍\���`�F�b�N�����łȂ��A\lectures\ �L�[�̑��݂ƌ^�̑Ó����idict �ł��邩�A���g����łȂ����j���o���f�[�V�������������ŁA�s���S�ȏꍇ�� \insight_spec_*.json\ �ւ̃t�H�[���o�b�N�𔭓����������B
- **�󂯓������**:
  1. \executive_report.json\ �����݂��Ȃ��Ă��]���ǂ��� \insight_spec\ �W�v�։��B
  2. \executive_report.json\ �� \{}\ �̏ꍇ�ł� fallback ����B
  3. \executive_report.json\ �� \lectures\ �������Ȃ��ꍇ�ł� fallback ����B
  4. \lectures\ �̌^�� dict �łȂ��ꍇ�ł� fallback ����B
  5. Warning �͏o�邪�_�b�V���{�[�h�͒�~���Ȃ��B
  6. �����̐��� JSON ���͎��̋����͉󂳂Ȃ��B
- **��������**: 
  - \data_loader.py\ �� \load_executive_report()\ ���Ń��[�h���� data �ɑ΂��āA\if not data.get('lectures') or not isinstance(data['lectures'], dict):\ ���̔����ǉ����ANG�Ȃ� \uild_executive_report_from_specs()\ �֗����B


## ダッシュボード デモ確認完了メモ

**確認対象**: Streamlit ダッシュボード (main ブランチ反映後)

**確認結果**:
- チャンネル全体KPI（総再生数・総いいね・総コメント）が表示される
- 個別動画分析でも、各動画の再生数・いいね・コメントが表示される
- quality_score / anking_score は「未算出」と表示される
- AIサマリーが正常に表示される（GPTによる動的生成）

**判定**: デモ実施可能

**備考**:
- quality_score / anking_score が「未算出」表示となるのは、現行データに該当項目が存在しないため仕様どおりです。
- 軽微バックログとして、load_executive_report() の不完全JSONに対するフォールバック強化（バリデーション強化）タスクが別途残っています。

**関連PR**:
- PR #27: executive_report.json への強依存廃止と insight_spec_*.json 直接集計への移行
- PR #29: エンゲージメント指標の取得パス補正 (iews.competitive.metrics.*)
