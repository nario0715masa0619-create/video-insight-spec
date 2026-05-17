# Sample Archive (最小実行用サンプルデータ)

このフォルダは、`video-insight-spec` の最小実行確認（smoke test）を目的としたダミーデータを収録しています。

## 目的と制約
- **目的**: リポジトリを clone してすぐに `competitor_analytics_generator.py` を実行し、レポート生成プロセス（Phase 4.2/4.3）が動作するか確認するため。
- **制約**: ここに含まれる `insight_spec_*.json` は、フォーマットを模倣した**本番データではないダミーデータ**です。実データでは `knowledge_core` や `video_meta` により多くの情報が含まれます。

## 実データとの違い（簡略化されている点）
- `center_pins` の数が極端に少ない（通常は数十個）。
- `views.competitive.snapshot_history` の履歴が意図的に 2 件のみ設定されています（growth_view の算出には最低 2 件の履歴が必要なため）。

## 実行方法
以下のコマンドで、このサンプルデータを使ったレポート生成をテストできます。

```bash
# sample_archive を入力ディレクトリとして指定
python competitor_analytics_generator.py --lecture-ids "01,02" --archive-dir "sample_archive"
```

※ Windows 環境で出力が文字化けする場合は、UTF-8 モードを有効にして実行してください。
```powershell
$env:PYTHONUTF8=1; python competitor_analytics_generator.py --lecture-ids "01,02" --archive-dir "sample_archive"
```

## サンプルデータの追加方法
新しいテストデータを追加する場合は、以下の命名規則でこのフォルダに JSON ファイルを作成し、実行時の `--lecture-ids` に追加してください。

- **ファイル命名規則**: `insight_spec_{lecture_id}.json` (例: `insight_spec_03.json`)
- **JSONの必須構造**: `docs/specs/JSON_SPEC.md` に準拠していること。特に growth_view を通す場合は `snapshot_history` に最低 2 つのレコードが必要です。
