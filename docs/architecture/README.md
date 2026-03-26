# Architecture & Design Documents

このディレクトリには、システム全体とコンポーネントの設計ドキュメントが含まれています。

## ファイル一覧

| ファイル | 説明 |
|---------|------|
| **VIEWS_DESIGN.md** | Views セクションの設計。engagement_score の定義、top N ピン抽出、サブスク連携フロー。 |

## 主な設計原則

1. **Progressive Disclosure**: views は要約 + top N、詳細は knowledge_core 参照
2. **Single Responsibility**: 各ファイルが単一の責務を持つ
3. **Extensibility**: 新規ビュー追加や重み付け調整が容易

詳細は [VIEWS_DESIGN.md](VIEWS_DESIGN.md) を参照してください。
