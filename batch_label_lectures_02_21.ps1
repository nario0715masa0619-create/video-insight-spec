# -*- coding: utf-8 -*-
# Phase 3: Batch Labeling for Lectures 02-21
# Purpose: Run expand_insight_spec_with_gemini.py for all lectures, with logging

param(
    [string]$LogDir = "logs",
    [string]$ArchiveDir = "D:\Knowledge_Base\Brain_Marketing\archive",
    [int]$TopN = 5,
    [int]$StartLecture = 2,
    [int]$EndLecture = 21
)

# ====== Setup ======
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $LogDir "phase3_batch_lecture_${StartLecture}_${EndLecture}_${timestamp}.log"
$resultsFile = Join-Path $LogDir "phase3_batch_results_${timestamp}.json"

# Create logs directory if not exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

# Initialize logging
$logContent = @()
$results = @{
    started_at = (Get-Date -Format "o")
    lectures = @()
    summary = @{
        total = 0
        success = 0
        failed = 0
        skipped = 0
    }
}

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")][string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logLine = "[$timestamp] [$Level] $Message"
    Write-Host $logLine
    $logContent += $logLine
}

function Test-InputFile {
    param([string]$LectureId)
    $inputFile = Join-Path $ArchiveDir "insight_spec_${LectureId}.json"
    if (-not (Test-Path $inputFile)) {
        Write-Log "入力ファイルなし: $inputFile" "WARN"
        return $false
    }
    return $true
}

# ====== Main Execution ======
Write-Log "========================================" "INFO"
Write-Log "Phase 3 Batch Labeling: Lecture $StartLecture - $EndLecture" "INFO"
Write-Log "Archive Dir: $ArchiveDir" "INFO"
Write-Log "Top N: $TopN" "INFO"
Write-Log "========================================" "INFO"

for ($i = $StartLecture; $i -le $EndLecture; $i++) {
    $lectureId = "{0:d2}" -f $i
    $inputFile = Join-Path $ArchiveDir "insight_spec_${lectureId}.json"
    $outputFile = Join-Path $ArchiveDir "insight_spec_${lectureId}_labeled.json"
    
    $lectureResult = @{
        lecture_id = $lectureId
        input_file = $inputFile
        output_file = $outputFile
        status = "unknown"
        error = $null
        duration_seconds = 0
        start_time = (Get-Date)
    }
    
    # Check input file exists
    if (-not (Test-InputFile $lectureId)) {
        Write-Log "Lecture ${lectureId}: スキップ（入力ファイルなし）" "WARN"
        $lectureResult.status = "skipped"
        $results.summary.skipped++
        $results.lectures += $lectureResult
        continue
    }
    
    # Execute labeling
    Write-Log "Lecture ${lectureId}: ラベル付与開始..." "INFO"
    try {
        $startTime = Get-Date
        & python expand_insight_spec_with_gemini.py `
            --lecture-id $lectureId `
            --top-n $TopN `
            --output $outputFile 2>&1 | ForEach-Object {
                Write-Log "  $_" "INFO"
                $logContent += "  $_"
            }
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        # Verify output file exists
        if (Test-Path $outputFile) {
            Write-Log "Lecture ${lectureId}: ✅ 完了 (${duration}秒)" "SUCCESS"
            $lectureResult.status = "success"
            $lectureResult.duration_seconds = [int]$duration
            $results.summary.success++
        } else {
            Write-Log "Lecture ${lectureId}: ❌ 失敗 (出力ファイルが生成されない)" "ERROR"
            $lectureResult.status = "failed"
            $lectureResult.error = "出力ファイルが生成されない"
            $results.summary.failed++
        }
    }
    catch {
        Write-Log "Lecture ${lectureId}: ❌ エラー: $_" "ERROR"
        $lectureResult.status = "failed"
        $lectureResult.error = $_.Exception.Message
        $results.summary.failed++
    }
    finally {
        $lectureResult.end_time = (Get-Date)
        $results.lectures += $lectureResult
        $results.summary.total++
    }
}

# ====== Summary ======
Write-Log "========================================" "INFO"
Write-Log "実行完了サマリー:" "INFO"
Write-Log "  総実行数: $($results.summary.total)" "INFO"
Write-Log "  成功: $($results.summary.success)" "INFO"
Write-Log "  失敗: $($results.summary.failed)" "INFO"
Write-Log "  スキップ: $($results.summary.skipped)" "INFO"
Write-Log "========================================" "INFO"

# ====== Save Logs ======
$logContent | Out-File -FilePath $logFile -Encoding UTF8
Write-Log "ログファイル保存: $logFile" "SUCCESS"

# Save results as JSON
$results.completed_at = (Get-Date -Format "o")
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsFile -Encoding UTF8
Write-Log "結果ファイル保存: $resultsFile" "SUCCESS"

# Final status
if ($results.summary.failed -eq 0) {
    Write-Log "✅ すべてのラベル付与が完了しました" "SUCCESS"
    exit 0
} else {
    Write-Log "⚠️  $($results.summary.failed) 件の失敗があります。ログを確認してください。" "WARN"
    exit 1
}
