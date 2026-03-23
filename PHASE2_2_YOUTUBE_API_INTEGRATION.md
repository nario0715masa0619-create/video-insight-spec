# Phase 2.2: YouTube Data API 統合

## 概要
Mk2_Sidecar_XX.db に保存されたビデオファイルパスから、YouTube Data API v3 を使用して動画メタデータ（再生数、高評価数、コメント数）を取得し、insight_spec_XX.json に統合しました。

## 実装内容

### 1. ビデオファイルメタデータ抽出
- `D:/Knowledge_Base/Brain_Marketing/videos/downloaded_videos/` から MP4 ファイルを読み込み
- ファイル名から lecture_id とタイトルを自動抽出
- lecture_id 01～21 のビデオを処理

### 2. YouTube API 検索
- 抽出されたタイトルで YouTube を検索
- 最初の検索結果から video_id を取得
- API クォータ使用: 検索 1 回 = 100ユニット

### 3. メタデータ取得
- video_id から以下のデータを取得：
  - `viewCount`（再生数）
  - `likeCount`（高評価数）
  - `commentCount`（コメント数）
- エンゲージメント率を計算：`(likes + comments) / views * 100`
- API クォータ使用: 1 回 = 1ユニット

### 4. JSON 統合
- 取得データを `insight_spec_01.json` の `views.competitive.youtube_metrics` 追加
- タイムスタンプと API クォータ情報も記録

### 5. CSV エクスポート
- video_mapping.csv に lecture_id、title、video_id、YouTube URL、メトリクスを記録

## 出力ファイル
- `phase2_2_output/insight_spec_01_with_youtube.json` - YouTube メトリクス統合版
- `phase2_2_output/video_mapping.csv` - video_id マッピング一覧

## API クォータ管理
- 日上限: 1,000,000ユニット
- Phase 2.2 使用量: 2,020 ユニット（全21動画の検索 + メタデータ取得）
- 残り: 997,980 ユニット

## 実行結果の統計

### ビデオ処理結果
- 処理対象: 21 件
- 検索成功: 20 件
- 検索失敗: 1 件

### メトリクス統計
- 総再生数: 9,337,354
- 総高評価数: 233,348
- 総コメント数: 1,604

## 今後の拡張
- Phase 2.2.1: YouTube Analytics API を統合し、平均視聴時間、視聴者層分析などを追加
- Phase 2.2.2: 定期的な自動更新スケジュール（週 1 回など）を実装
- Phase 2.2.3: Brain の販売数データと YouTube メトリクスの相関分析

## テスト状況
- ✅ ビデオ検索: 20/21 成功
- ✅ メタデータ取得: 20/21 成功
- ✅ pytest: 全テスト PASS

## 実装日時
2026-03-23T11:52:22.642910
