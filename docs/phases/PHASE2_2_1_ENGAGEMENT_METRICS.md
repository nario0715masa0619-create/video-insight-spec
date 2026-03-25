# Phase 2.2.1: Engagement Metrics 計算

## 概要
Phase 2.2 で取得した YouTube Data API のメトリクス（view_count, like_count, comment_count）から、
派生指標（`engagement_metrics`）を計算し、insight_spec JSON に統合する。

## 計算式

### 1. engagement_rate
```python
if view_count == 0:
    engagement_rate = 0  # ゼロ除算回避
else:
    engagement_rate = (likes + comments) / view_count * 100
```
- 動画への総相互作用率（%）
- 値域: 0 ～ 無制限（通常は 0～20%）
- **view_count が 0 の場合は 0 とする**

### 2. likes_per_1000_views
```python
if view_count == 0:
    likes_per_1000_views = 0  # ゼロ除算回避
else:
    likes_per_1000_views = likes / view_count * 1000
```
- 1000視聴あたりの高評価数
- 値域: 0 ～ 無制限
- **view_count が 0 の場合は 0 とする**

### 3. comments_per_1000_views
```python
if view_count == 0:
    comments_per_1000_views = 0  # ゼロ除算回避
else:
    comments_per_1000_views = comments / view_count * 1000
```
- 1000視聴あたりのコメント数
- 値域: 0 ～ 無制限
- **view_count が 0 の場合は 0 とする**

## 実装場所
- `converter/insights_converter.py`: `calculate_engagement_metrics()` 関数
- `tests/test_insights_converter.py`: テストケース

## 出力例
```json
{
  "engagement_metrics": {
    "engagement_rate": 4.51,
    "likes_per_1000_views": 27.5,
    "comments_per_1000_views": 6.3
  }
}
```

## エッジケース処理
- view_count = 0: 全指標を 0 に設定（ゼロ除算回避）
- like_count または comment_count が負数: 入力検証で拒否（想定外）
- 浮動小数点誤差: 小数第2位まで丸め処理

## 将来の拡張
- Phase 2.3: ベンチマーク分析（同一チャンネル内平均・カテゴリ平均との比較）
- Phase 2.4: トレンド分析（時系列での engagement 変化）
- Phase 2.5: 機械学習による engagement 予測モデル

## タイムスタンプ
実装日: 2026-03-23T15:11:32.428082
