# -*- coding: utf-8 -*-
# YouTube URL → MP4 ダウンロード → Mk2_Core → insight_spec → labeled JSON 生成パイプライン

param(
    [string]$URLFile = "D:\AI_スクリプト成果物\video-insight-spec\targets\marketing_univ_top5.txt",
    [string]$WorkDir = "D:\AI_Data\video-insight-spec",
    [string]$VideosDir = "D:\AI_Data\video-insight-spec\downloaded_videos",
    [string]$ArchiveDir = "D:\AI_Data\video-insight-spec\archive",
    [int]$TopN = 5
)

$ErrorActionPreference = "Continue"

# ========== ログ設定 ==========
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $WorkDir "logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$logFile = Join-Path $logDir "youtube_pipeline_${timestamp}.log"
$resultsFile = Join-Path $logDir "pipeline_results_${timestamp}.json"

function Write-Log {
    param([string]$Message, [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")][string]$Level = "INFO")
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] [$Level] $Message"
    Write-Host $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

Write-Log "========================================" "INFO"
Write-Log "YouTube → Labeled Spec Pipeline Started" "INFO"
Write-Log "========================================" "INFO"
Write-Log "Work Dir: $WorkDir" "INFO"
Write-Log "Videos Dir: $VideosDir" "INFO"
Write-Log "Archive Dir: $ArchiveDir" "INFO"

# ========== URL ファイル読み込み ==========
if (-not (Test-Path $URLFile)) {
    Write-Log "URL ファイルが見つかりません: $URLFile" "ERROR"
    exit 1
}

$urls = @(Get-Content $URLFile | Where-Object { $_.Trim() -ne "" })
Write-Log "✅ $($urls.Count) 個の URL を読み込みました" "INFO"

New-Item -ItemType Directory -Path $VideosDir -Force | Out-Null
New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null

$results = @{
    started_at = (Get-Date -Format "o")
    total_urls = $urls.Count
    work_dir = $WorkDir
    videos_dir = $VideosDir
    archive_dir = $ArchiveDir
    steps = @()
}

# ========== Step 1: yt-dlp でダウンロード ==========
Write-Log "" "INFO"
Write-Log "【Step 1】YouTube → MP4 ダウンロード" "INFO"
Write-Log "================================================" "INFO"

$downloadedFiles = @()
$downloadedCount = 0

foreach ($i in 0..($urls.Count - 1)) {
    $url = $urls[$i]
    $lectureId = "{0:d2}" -f ($i + 1)
    
    Write-Log "[$($i+1)/$($urls.Count)] ダウンロード中: $url" "INFO"
    
    try {
        $outputTemplate = Join-Path $VideosDir "${lectureId}_%(title)s.%(ext)s"
        & python -m yt_dlp -f "best[ext=mp4]" -o $outputTemplate $url 2>&1 | Out-Null
        
        Start-Sleep -Milliseconds 500
        $downloadedFile = Get-ChildItem $VideosDir -Filter "${lectureId}_*.mp4" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if ($downloadedFile) {
            Write-Log "  ✅ ダウンロード成功: $($downloadedFile.Name)" "SUCCESS"
            $downloadedFiles += @{
                lecture_id = $lectureId
                url = $url
                filename = $downloadedFile.Name
                path = $downloadedFile.FullName
            }
            $downloadedCount++
        }
    }
    catch {
        Write-Log "  ❌ エラー: $_" "ERROR"
    }
}

Write-Log "Step 1 完了: $downloadedCount 成功" "INFO"

if ($downloadedFiles.Count -eq 0) {
    Write-Log "ダウンロード失敗。処理を中止します。" "ERROR"
    exit 1
}

$results.steps += @{
    step = 1
    name = "YouTube → MP4 ダウンロード"
    success = $downloadedCount
}


# ========== Step 2: master_batch_refiner.py で Mk2_Core 生成 ==========
Write-Log "" "INFO"
Write-Log "【Step 2】master_batch_refiner.py で Mk2_Core 生成" "INFO"
Write-Log "================================================" "INFO"

$refinerResults = @()
$refinerSuccessCount = 0

foreach ($file in $downloadedFiles) {
    $lectureId = $file.lecture_id
    $filePath = $file.path
    
    Write-Log "[$lectureId] 処理中..." "INFO"
    
    try {
        $startTime = Get-Date
        
        # 環境変数を設定
        $env:ARCHIVE_OUTPUT_DIR = $ArchiveDir
        
        # このリポジトリの master_batch_refiner.py を実行
        $output = & python master_batch_refiner.py $filePath 2>&1
        
        $duration = ((Get-Date) - $startTime).TotalSeconds
        
        $coreJson = Join-Path $ArchiveDir "Mk2_Core_${lectureId}.json"
        $sidecarDb = Join-Path $ArchiveDir "Mk2_Sidecar_${lectureId}.db"
        
        if ((Test-Path $coreJson) -and (Test-Path $sidecarDb)) {
            Write-Log "  ✅ 完了 (${duration}秒)" "SUCCESS"
            $refinerResults += @{ lecture_id = $lectureId; status = "success" }
            $refinerSuccessCount++
        } else {
            Write-Log "  ❌ 失敗: 出力ファイルなし" "ERROR"
            if ($output) {
                Write-Log "  [ERROR] $($output | Select-Object -First 5 | Out-String)" "ERROR"
            }
            $refinerResults += @{ lecture_id = $lectureId; status = "failed" }
        }
    }
    catch {
        Write-Log "  ❌ エラー: $_" "ERROR"
        $refinerResults += @{ lecture_id = $lectureId; status = "error" }
    }
}

Write-Log "Step 2 完了: $refinerSuccessCount 成功" "INFO"
$results.steps += @{
    step = 2
    name = "master_batch_refiner.py"
    success = $refinerSuccessCount
}


# ========== Step 3: convert_to_insight_spec_phase1.py ==========
Write-Log "" "INFO"
Write-Log "【Step 3】convert_to_insight_spec_phase1.py で insight_spec 生成" "INFO"
Write-Log "================================================" "INFO"

$phase1Results = @()
$phase1SuccessCount = 0

foreach ($result in ($refinerResults | Where-Object { $_.status -eq "success" })) {
    $lectureId = $result.lecture_id
    
    Write-Log "[$lectureId] 変換中..." "INFO"
    
    try {
        $startTime = Get-Date
        & python convert_to_insight_spec_phase1.py --lecture-id $lectureId --archive-dir $ArchiveDir 2>&1 | Out-Null
        $duration = ((Get-Date) - $startTime).TotalSeconds
        
        $specJson = Join-Path $ArchiveDir "insight_spec_${lectureId}.json"
        
        if (Test-Path $specJson) {
            Write-Log "  ✅ 完了 (${duration}秒)" "SUCCESS"
            $phase1Results += @{ lecture_id = $lectureId; status = "success" }
            $phase1SuccessCount++
        } else {
            Write-Log "  ❌ 失敗" "ERROR"
            $phase1Results += @{ lecture_id = $lectureId; status = "failed" }
        }
    }
    catch {
        Write-Log "  ❌ エラー: $_" "ERROR"
        $phase1Results += @{ lecture_id = $lectureId; status = "error" }
    }
}

Write-Log "Step 3 完了: $phase1SuccessCount 成功" "INFO"
$results.steps += @{
    step = 3
    name = "convert_to_insight_spec_phase1.py"
    success = $phase1SuccessCount
}

# ========== Step 4: expand_insight_spec_with_gemini.py でラベル付与 ==========
Write-Log "" "INFO"
Write-Log "【Step 4】expand_insight_spec_with_gemini.py でラベル付与" "INFO"
Write-Log "================================================" "INFO"

$phase3Results = @()

foreach ($r in $phase1Results | Where-Object { $_.status -eq "success" }) {
    $lectureId = $r.lecture_id
    
    Write-Log "[$lectureId] ラベル付与中..." "INFO"
    
    try {
        $st = Get-Date
        
        # expand_insight_spec_with_gemini.py を実行
        $output = & python expand_insight_spec_with_gemini.py --lecture-id $lectureId --archive-dir $ArchiveDir  2>&1
        
        $dur = ((Get-Date)-$st).TotalSeconds
        
        # 出力ファイル確認
        $labeledJson = Join-Path $ArchiveDir "insight_spec_${lectureId}.json"
        
        if (Test-Path $labeledJson) {
            Write-Log "  ✅ 完了 (${dur}秒)" "SUCCESS"
            $phase3Results += @{ lecture_id = $lectureId; status = "success"; duration_s = [int]$dur; labeled_json = $labeledJson }
        } else {
            Write-Log "  ❌ 失敗: ファイルが生成されません" "ERROR"
            Write-Log "    出力: $($output | Select-Object -Last 5 | Out-String)" "ERROR"
            $phase3Results += @{ lecture_id = $lectureId; status = "failed"; error = "出力ファイルなし" }
        }
    }
    catch {
        Write-Log "  ❌ エラー: $($_.Exception.Message)" "ERROR"
        $phase3Results += @{ lecture_id = $lectureId; status = "error"; error = $_.Exception.Message }
    }
}

$phase3SuccessCount = ($phase3Results | Where-Object { $_.status -eq "success" }).Count
Write-Log "Step 4 完了: $phase3SuccessCount 成功 / $($phase3Results.Count - $phase3SuccessCount) 失敗" "INFO"

$results.steps += @{ step = 4; name = "expand_insight_spec_with_gemini.py"; results = $phase3Results }


# ========== 完了サマリー ==========
Write-Log "" "INFO"
Write-Log "========================================" "INFO"
Write-Log "パイプライン完了" "INFO"
Write-Log "========================================" "INFO"
Write-Log "Step 1 (ダウンロード): $downloadedCount/$($urls.Count)" "INFO"
Write-Log "Step 2 (Mk2_Core): $refinerSuccessCount/$downloadedCount" "INFO"
Write-Log "Step 3 (insight_spec): $phase1SuccessCount/$refinerSuccessCount" "INFO"
Write-Log "Step 4 (ラベル付与): $phase3SuccessCount/$phase1SuccessCount" "INFO"

$results.completed_at = (Get-Date -Format "o")
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsFile -Encoding UTF8

Write-Log "" "INFO"
Write-Log "ログファイル: $logFile" "SUCCESS"
Write-Log "結果ファイル: $resultsFile" "SUCCESS"
Write-Log "ダウンロード: $VideosDir" "SUCCESS"
Write-Log "アーカイブ: $ArchiveDir" "SUCCESS"

if ($phase3SuccessCount -eq $downloadedCount) {
    Write-Log "✅ すべてのステップが完了しました" "SUCCESS"
    exit 0
} else {
    Write-Log "⚠️ 一部のステップで失敗しています。ログを確認してください。" "WARN"
    exit 1
}


