# Free-Trial Dashboard v1.5.7 起動ガイド
## Life Design Partners

このダッシュボードはフリートライアル検証版です。
本体標準版ではなく、営業デモ・試用目的で使用してください。

## 起動方法

### 方法 1：バッチファイル（Windows推奨）
```
launch_free_trial_LifeDesignPartners.bat
```
ダブルクリックで起動します。

### 方法 2：PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\launch_free_trial_LifeDesignPartners.ps1
```

### 方法 3：手動起動
```powershell
cd D:\AI_スクリプト成果物\video-insight-spec-dev
$env:VIS_MODE="free_trial"
$env:PYTHONIOENCODING="utf-8"
streamlit run streamlit_app/app.py --server.port=8501
```

## アクセスURL
| タイプ | URL |
| --- | --- |
| ローカルアクセス | http://localhost:8501 |
| ネットワークアクセス | http://192.168.0.241:8501 |

## 主な機能

### 【黄金の組み合わせ】
* 2段階診断レポート（Executive Summary + 詳細分析）
* 「なぜ伸びなかったのか」の原因診断
* 「今後、何をすべきか」の優先アクション
* 実績データに基づく具体的な提案

### 【競争優位性分析】
* テーマ多様性、コンテンツ多様性の数値表示
* エンゲージメント効率、初心者向け適性の評価
* 市場でのポジショニング診断

### 【品質診断】
* コンテンツ品質スコア（0.00-1.00）
* ファネルステージ別の品質分析
* 学習ニーズ仮説の提示

### 【改善提案】
* 実行可能な具体的施策リスト
* 優先順位付きのアクションプラン

## デモデータ
* **案件：** trial_lifedesign_20260609
* **YouTube 動画：** YiqGX6Ytjc0
* **タイトル：** 「若者よ、ワークライフバランスに騙されるな！」
* **公開日：** 2026-05-28
* **再生数：** 207
* **高評価：** 10
* **コメント：** 2
* **エンゲージメント率：** 5.8%

## バージョン情報
* **バージョン：** v1.5.7
* **ステータス：** フリートライアル限定版
* **対象：** Life Design Partners
* **リリース日：** 2026-06-11

## 既知の制限事項（v1.5.7）
* フリートライアルモード（`VIS_MODE=free_trial`）のみ動作
* 本体標準版への昇格は保留中
* 複数案件の同時処理未対応

## 次版（v2.0）で改善予定
* 競争優位性分析の計算根拠を明記
* エンゲージメント効率の説明を改善
* コンテンツ形式多様性の具体表示
* 評価トーンを前向きに修正
* 提案文の具体性を向上

## トラブルシューティング

### Streamlit が起動しない場合
```powershell
Remove-Item $env:USERPROFILE\.streamlit -Recurse -Force
```

### ポート 8501 がすでに使用中
```powershell
streamlit run streamlit_app/app.py --server.port=8502
```

### 日本語が文字化けする場合
```powershell
$env:PYTHONIOENCODING="utf-8"
```

---
**対象企業：** Life Design Partners
**案件ID：** trial_lifedesign_20260609
**ステータス：** フリートライアル限定版（本体昇格は保留）
