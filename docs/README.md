# ドキュメント

video-insight-spec プロジェクトの完全なドキュメント。フェーズ4～7に対応。

## ディレクトリ構成

### 📋 [specs](specs/) - スキーマと仕様
- **JSON_SPEC.md**: 完全な JSON スキーマ定義（v3.0）
- **WORKFLOW_IMPLEMENTATION_MAP.md**: データフローと実装マップ
- **VIEWS_DESIGN.md**: ビュー設計思想と実装詳細

### 🏗️ [phases](phases/) - フェーズドキュメント

#### フェーズ4：データ生成・レポート自動化
- PHASE4_2_DESIGN.md - データ仕様設計（Portfolio/Growth/Theme View）
- PHASE4_3_DESIGN.md - HTML/Text フォーマッタ設計
- PHASE4_3_PLAN.md - 実装計画

#### フェーズ5：商品化・営業資料
- PHASE5_1_DESIGN.md - Executive Summary 仕様
- PHASE5_2_PLAN.md - サブスクリプション仕様
- PHASE5_3_LP_OUTLINE.md - LP構成メモ
- PHASE5_3_NOTE_DRAFT.md - note記事草案
- PHASE5_3_FINANCE_BRIEF.md - 金融機関向け説明書

#### フェーズ6：PoC・営業支援（進行中）
- PHASE6_PLAN.md - PoC・営業支援計画（予定）

#### フェーズ7以降：プロダクト拡張（将来）
- PHASE7_PLAN.md - ダッシュボード・API・Slack統合（予定）

### 🔧 [operations](operations/) - 運用と保守
- **TROUBLESHOOTING.md**: トラブルシューティングガイド

### 💻 [implementation](implementation/) - 実装ガイド
- コード設計ガイド、API統合、テスト戦略（準備中）

## クイックリンク

### 初心者向け
1. [README.md](../README.md) - プロジェクト概要・クイックスタート
2. [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - プロジェクト全体像
3. [specs/JSON_SPEC.md](specs/JSON_SPEC.md) - データ構造理解

### 開発者向け
1. [specs/WORKFLOW_IMPLEMENTATION_MAP.md](specs/WORKFLOW_IMPLEMENTATION_MAP.md) - 実装マップ
2. [phases/PHASE4_3_DESIGN.md](phases/PHASE4_3_DESIGN.md) - レポート生成ロジック
3. [operations/TROUBLESHOOTING.md](operations/TROUBLESHOOTING.md) - デバッグガイド

### 営業・ビジネス向け
1. [phases/PHASE5_3_LP_OUTLINE.md](phases/PHASE5_3_LP_OUTLINE.md) - LP構成・営業ポイント
2. [phases/PHASE5_3_NOTE_DRAFT.md](phases/PHASE5_3_NOTE_DRAFT.md) - ビジネスモデル解説
3. [phases/PHASE5_3_FINANCE_BRIEF.md](phases/PHASE5_3_FINANCE_BRIEF.md) - 財務・資金計画

### 運用者向け
1. [operations/TROUBLESHOOTING.md](operations/TROUBLESHOOTING.md) - トラブルシューティング
2. [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - システムアーキテクチャ
3. [specs/JSON_SPEC.md](specs/JSON_SPEC.md) - データ仕様

## フェーズの進捗

| フェーズ | タイトル | 状態 | 最終更新 |
|---------|---------|------|---------|
| 4.2 | データ仕様設計 | ✅ 完了 | 2026-03-26 |
| 4.3 | HTML/Text フォーマッタ | ✅ 完了 | 2026-03-27 |
| 5.1 | 経営者向けサマリー | ✅ 完了 | 2026-03-27 |
| 5.2 | サブスク仕様 | ✅ 完了 | 2026-03-27 |
| 5.3 | 外部向け資料 | ✅ 完了 | 2026-03-27 |
| 6 | PoC・営業支援 | 🔄 進行中 | - |
| 7 | プロダクト拡張 | 📋 計画中 | - |

## 主要成果物

### フェーズ4～5完了
- 3層JSON構造：video_meta / knowledge_core / views
- レポート生成エンジン：Executive Summary + Full Report（HTML/Text）
- サブスク仕様：月額10万円、初期30～50万円
- 営業資料：LP、note、金融機関向け説明書
- Year 3目標：ARR 4,500万円、30社顧客、42～53%利益率

### フェーズ6（進行中）
- PoC用ランディングページ
- サンプルレポートセット（3例）
- 営業テンプレ・自動化ツール
- オンボーディング支援資料

### フェーズ7以降（将来）
- Webダッシュボード
- REST API
- Slack統合
- AI推薦、PDF出力、国際展開

## ドキュメント更新履歴

**フェーズ5.3（2026-03-27）**
- PHASE5_3_LP_OUTLINE.md：LP構成メモ作成
- PHASE5_3_NOTE_DRAFT.md：note記事草案作成
- PHASE5_3_FINANCE_BRIEF.md：金融機関向け説明書作成
- オンラインレビューを必須からオプションに変更

**フェーズ5.2（2026-03-27）**
- サブスクリプション仕様確定
- 料金体系、SLA、契約条件定義

**フェーズ5.1（2026-03-27）**
- Executive Summary フォーマット確定
- 1ページレポート仕様完成

**フェーズ4.3（2026-03-27）**
- HTML/Text フォーマッタ実装完了
- レポート生成エンジン統合完了

**フェーズ4.2（2026-03-26）**
- Portfolio/Growth/Theme View 実装完了
- エンゲージメント計算式確定

---

最終更新：2026-03-27
ブランチ：main（フェーズ5.3 マージ済み）
次のフェーズ：フェーズ6 - PoC・営業支援
