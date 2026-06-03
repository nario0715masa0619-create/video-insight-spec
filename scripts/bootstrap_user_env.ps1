<#
.SYNOPSIS
    ユーザーホームに video-insight-spec の環境変数正本ファイルを作成します。

.DESCRIPTION
    %USERPROFILE%\.video-insight-spec ディレクトリを作成し、
    リポジトリの .env.example を元に正本となる .env を生成します。
    既に .env が存在する場合は上書きしません。
#>

$TargetDir = Join-Path -Path $env:USERPROFILE -ChildPath ".video-insight-spec"
$TargetEnv = Join-Path -Path $TargetDir -ChildPath ".env"

$RepoDir = Split-Path -Path $PSScriptRoot -Parent
$ExampleEnv = Join-Path -Path $RepoDir -ChildPath ".env.example"

Write-Host "=========================================="
Write-Host " 秘密情報の正本セットアップ"
Write-Host "=========================================="

if (-not (Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
    Write-Host "✅ ディレクトリを作成しました: $TargetDir" -ForegroundColor Green
} else {
    Write-Host "ℹ️ ディレクトリは既に存在します: $TargetDir" -ForegroundColor Cyan
}

if (-not (Test-Path -Path $TargetEnv)) {
    if (Test-Path -Path $ExampleEnv) {
        Copy-Item -Path $ExampleEnv -Destination $TargetEnv
        Write-Host "✅ .env テンプレートを正本としてコピーしました: $TargetEnv" -ForegroundColor Green
        Write-Host "⚠️ メモ帳などで $TargetEnv を開き、必要な API キーを設定してください。" -ForegroundColor Yellow
    } else {
        Write-Host "❌ リポジトリ直下に .env.example が見つかりません: $ExampleEnv" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ℹ️ 正本 .env は既に存在します（上書きスキップ）: $TargetEnv" -ForegroundColor Cyan
}

Write-Host "=========================================="
Write-Host " セットアップ完了"
Write-Host "=========================================="
