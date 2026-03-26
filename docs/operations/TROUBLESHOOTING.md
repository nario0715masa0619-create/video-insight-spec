# Git Push トラブルシューティング

## 問題: git push が "Failed to connect to github.com port 443" で失敗する

### 症状

- GitHub の Web は正常に開ける
- `ping github.com` がタイムアウトする（ICMP ブロック）
- `ssh -T git@github.com` が port 22 タイムアウト
- DNS は解決できる (`nslookup github.com` は成功)
- エラー: fatal: unable to access 'https://github.com/...': Failed to connect to github.com port 443

### 原因

不明。以下の可能性が考えられます：

1. 一時的なネットワーク遅延
2. Git 内部的なプロキシキャッシュ（設定ファイルには記録なし）
3. ファイアウォール/プロキシの一時的なブロック

### 対処方法

git config --global --unset http.proxy
git config --global --unset https.proxy
git push origin <branch-name>

### 発生日時と詳細

日時: 2026-03-26
ブランチ: feature/phase-3.2-google-genai-migration → main
コミット: eec8850 (feat: Phase 3.2 完了 - google.generativeai → google-genai 移行)
エラー回数: 3 回の失敗後、対処方法で成功

### 確認コマンド

git config --list | Select-String proxy
$env:HTTP_PROXY
$env:HTTPS_PROXY
$env:ALL_PROXY
cat $env:USERPROFILE\.gitconfig

### 予防策

- 定期的に `git config --list` でプロキシ設定を確認
- ネットワーク不安定な環境では `git push` 前に `ping github.com` を実行
- 複数回失敗した場合は、上記の対処方法を実行
