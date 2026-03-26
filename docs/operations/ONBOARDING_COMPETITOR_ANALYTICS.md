# Onboarding Guide: Competitor Analytics

## 1. クライアントにやってもらうこと

競合分析機能を利用するにあたり、クライアント側で用意してもらう情報は次のとおりです。

1. 自社チャンネル／プレイリストの URL
2. 競合チャンネル／プレイリストの URL（1〜数本）
3. それぞれの役割（role）：
   - `"self"`（自社）
   - `"competitor"`（競合）

---

## 2. 設定ファイル形式（targets.yml）

運用では、以下のような YAML ファイルでターゲットを指定します。

```yaml
targets:
  - role: self
    name: "自社メインチャンネル"
    url: "https://www.youtube.com/playlist?list=PL-SELF-XXXX"
  - role: competitor
    name: "競合A マーケティング大学"
    url: "https://www.youtube.com/playlist?list=PL-COMP-A"
  - role: competitor
    name: "競合B 起業チャンネル"
    url: "https://www.youtube.com/playlist?list=PL-COMP-B"
```

- `role`: `"self"` or `"competitor"`
- `name`: レポート上で表示する名称
- `url`: YouTube チャンネル or プレイリストの URL

---

## 3. 実行フロー（概要）

1. `targets.yml` を用意（クライアントと相談のうえ作成）
2. パイプライン起動スクリプトに `--targets config/targets.yml` を渡して実行
3. システム側で：
   - 各 URL から動画一覧を取得
   - transcription / OCR / insight_spec 生成
   - Gemini によるラベル付与
   - views / snapshot_history の生成
   - Phase 4.2 の比較ビュー（portfolio_view / growth_view / theme_view）を出力

---

## 4. 期待されるアウトプット（クライアント視点）

- 自社講座の構造とパフォーマンスの整理（すでに持っているダッシュボードを補完）
- 競合講座の構造を **自社と同じ軸で** 可視化したレポート
- 自社 vs 競合のポジショニング：
  - どのテーマ・ファネル段階で優位か
  - どこに新規講座やプロモーションの余地があるか
- 週次での伸び率比較（view_count / engagement_rate）

---

## 5. 今後の拡張余地メモ

- role の拡張：
  - `"benchmark"`（業界ベンチマーク用チャンネル）
- ターゲット単位のメタ情報：
  - カテゴリ（例：BtoB / BtoC）
  - 市場（例：JP / US）
- GUI からの URL 登録（将来的な管理画面想定）