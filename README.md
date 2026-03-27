# video-insight-spec

YouTube 動画の洞察・競合分析システム。動画視聴データを構造化し、経営判断に直結したレポートを自動生成・配信する SaaS サービスの基盤。

## クイックスタート

**必要なもの:**
- Python 3.8+
- YouTube API キー

**セットアップ:**
1. リポジトリをクローン
2. 依存関係をインストール
3. .env に YOUTUBE_API_KEY を設定
4. competitor_analytics_generator.py を実行

## フェーズの進捗

| フェーズ | タイトル | 状態 | 日付 | 成果物 |
|---------|---------|------|------|--------|
| 4.2 | データ仕様設計 | ✅ 完了 | 2026-03-26 | portfolio_view, growth_view, theme_view |
| 4.3 | HTML/Text フォーマッタ | ✅ 完了 | 2026-03-27 | html_formatter.py, text_formatter.py, Report Generator |
| 5.1 | 経営者向けサマリー | ✅ 完了 | 2026-03-27 | 1ページレポート |
| 5.2 | サブスク仕様 | ✅ 完了 | 2026-03-27 | サービスモデル、料金、SLA |
| 5.3 | 外部向け資料 | ✅ 完了 | 2026-03-27 | LP outline、note 草案、Finance brief |
| 6 | PoC・営業支援 | 🔄 進行中 | - | PoC 用 LP、サンプルレポート、営業テンプレ |
| 7 | プロダクト拡張 | 📋 計画中 | - | ダッシュボード、REST API、Slack 統合 |

## 主な機能

### フェーズ 4: データ生成・レポート自動化
- **3層 JSON 構造**: video_meta / knowledge_core / views
- **自動レポート生成**: Executive Summary（1ページ）+ Full Report（複数ページ）
- **デュアル出力**: HTML（ブラウザ向け）+ テキスト（マークダウン互換）
- **JST タイムスタンプ統一**: すべてのレポートに JST 日時を記載

### フェーズ 5: 商品化・営業資料
- **Executive Summary（1ページ）**: 3分で読める経営判断資料
- **サブスク モデル**: 月額 10 万円（基本プラン）+ 初期 30 万円～
- **ターゲット**: 講座 5～20 本クラスの EdTech スタートアップ
- **営業資料**: LP 構成メモ、note 記事草案、VC・銀行向けピッチ資料

### フェーズ 6: PoC・営業支援（進行中）
- **PoC 用 LP**: サンプルレポート掲載、試算機能
- **サンプルレポート**: 実例 1～3 セット（HTML + テキスト）
- **営業テンプレ**: 提案書、メールテンプレ、見積自動化ツール
- **導入支援**: オンボーディングドキュメント、チェックリスト

### フェーズ 7: プロダクト拡張（将来）
- **Web ダッシュボード**: リアルタイム・日次更新の可視化
- **REST API**: JSON レポートデータを API 化（認証・レート制限付き）
- **Slack 統合**: 月次自動通知・成長テーマのアラート

## ドキュメント

### 仕様書
- [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) - プロジェクト概要・アーキテクチャ
- [JSON_SPEC.md](docs/specs/JSON_SPEC.md) - 3層 JSON スキーマ
- [VIEWS_DESIGN.md](docs/specs/VIEWS_DESIGN.md) - View 定義

### フェーズドキュメント
- [PHASE4_2_DESIGN.md](docs/phases/PHASE4_2_DESIGN.md) - データ構造・View 設計
- [PHASE4_3_DESIGN.md](docs/phases/PHASE4_3_DESIGN.md) - HTML/Text フォーマッタ設計
- [PHASE4_3_PLAN.md](docs/phases/PHASE4_3_PLAN.md) - 実装計画
- [PHASE5_1_DESIGN.md](docs/phases/PHASE5_1_DESIGN.md) - Executive Summary 仕様
- [PHASE5_2_PLAN.md](docs/phases/PHASE5_2_PLAN.md) - サブスク仕様
- [PHASE5_3_LP_OUTLINE.md](docs/phases/PHASE5_3_LP_OUTLINE.md) - LP 構成メモ
- [PHASE5_3_NOTE_DRAFT.md](docs/phases/PHASE5_3_NOTE_DRAFT.md) - note 記事草案
- [PHASE5_3_FINANCE_BRIEF.md](docs/phases/PHASE5_3_FINANCE_BRIEF.md) - 金融機関向け説明書

## コマンド

python competitor_analytics_generator.py --lecture-ids "01,02,03,04,05"

## ディレクトリ構造

video-insight-spec/
├── docs/
│   ├── phases/
│   │   ├── PHASE4_2_DESIGN.md
│   │   ├── PHASE4_3_DESIGN.md
│   │   ├── PHASE4_3_PLAN.md
│   │   ├── PHASE5_1_DESIGN.md
│   │   ├── PHASE5_2_PLAN.md
│   │   ├── PHASE5_3_LP_OUTLINE.md
│   │   ├── PHASE5_3_NOTE_DRAFT.md
│   │   └── PHASE5_3_FINANCE_BRIEF.md
│   └── specs/
│       ├── JSON_SPEC.md
│       └── VIEWS_DESIGN.md
├── converter/
│   ├── text_formatter.py
│   ├── html_formatter.py
│   ├── report_generator.py
│   └── executive_summary_formatter.py
├── reports/
│   ├── competitor_analytics/
│   ├── html/
│   ├── text/
│   └── executive_summary/
├── competitor_analytics_generator.py
├── README.md
└── .env（トラック対象外）

## 出力例

### Executive Summary
- ファイル: reports/executive_summary/executive_summary_YYYYMMDD.html
- 内容: ヘッダー + 全体サマリ（3指標）+ Top 3 講座 + Top 3 テーマ + アクション提案
- サイズ: 1ページ（A4 印刷対応）

### Full Report（HTML）
- ファイル: reports/html/competitor_analytics_YYYYMMDD.html
- 内容: Portfolio View + Growth View + Theme View + Representative Insights
- 特徴: レスポンシブ CSS、セマンティック HTML、印刷対応

### Full Report（テキスト）
- ファイル: reports/text/competitor_analytics_YYYYMMDD.txt
- 内容: HTML と同じ構成、マークダウン互換
- 用途: メール添付、CMS 連携

## ビジネスモデル

### ターゲット市場
- 中堅 EdTech スタートアップ（講座 5～20 本）
- 年間売上 1～10 億円規模
- 課題: データドリブン改善を進めたいが、分析人材が限定的

### 料金体系
- 基本プラン: 月額 10 万円
- 初期導入費: 30～50 万円
- プレミアムプラン（将来）: 月額 20 万円（週次報告 + コンサルティング）
- エンタープライズ（将来）: 要相談（50+ 講座対応）

### Year 3 予測（シナリオ B）
- 年間売上（ARR）: 4,500 万円
- 顧客数: 30 社
- EBITDA: 1,900～2,400 万円（利益率 42～53%）
- 回収期間: 3～4 年

## セキュリティ

- YOUTUBE_API_KEY は .env で管理（Git に commit しない）
- データ暗号化: すべての顧客視聴ログを保存時に暗号化
- SOC 2 / ISO 27001 対応: Year 1 内に取得予定
- バックアップ・災害対応: 稼働保証 99.9% SLA を目指す

## ロードマップ

### フェーズ 6（進行中）
- PoC 用ランディングページ完成
- サンプルレポート 1 セット（実例ベース）
- 営業テンプレ & 自動化ツール投入

### フェーズ 7（プロダクト拡張）
- Web ダッシュボード（リアルタイム可視化）
- REST API（データ公開 + 認証）
- Slack 統合（自動通知）

### フェーズ 8 以降（将来）
- AI による自動提案生成
- PDF 出力機能
- 国際展開（東南アジア）
- モバイル アプリ（iOS / Android）

---

最終更新: 2026-03-27
ブランチ: main（Phase 5.3 マージ済み）
次のフェーズ: Phase 6 - PoC・営業支援