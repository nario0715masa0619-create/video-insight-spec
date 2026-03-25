# -*- coding: utf-8 -*-
# Pipeline Output Validation Script

param(
    [string]$ArchiveDir = "D:\AI_Data\video-insight-spec\archive",
    [int]$MinCenterPins = 3,
    [int]$MinContentChars = 50
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pipeline Output Validation Started" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$results = @()

# 講座 01～05 を検証
foreach ($lectureId in @("01", "02", "03", "04", "05")) {
    Write-Host "`n【Lecture $lectureId】" -ForegroundColor Yellow
    
    $coreJson = Join-Path $ArchiveDir "Mk2_Core_${lectureId}.json"
    $insightJson = Join-Path $ArchiveDir "insight_spec_${lectureId}.json"
    $ocrFile = Join-Path $ArchiveDir "Mk2_OCR_${lectureId}.txt"
    
    $validation = @{
        lecture_id = $lectureId
        files_exist = $true
        core_pins_count = 0
        insight_pins_count = 0
        avg_content_length = 0
        has_labels = $false
        issues = @()
    }
    
    # ファイル存在確認
    if (-not (Test-Path $coreJson)) {
        $validation.files_exist = $false
        $validation.issues += "Mk2_Core_${lectureId}.json が見つかりません"
        Write-Host "  ❌ Mk2_Core: NOT FOUND" -ForegroundColor Red
    } else {
        Write-Host "  ✅ Mk2_Core: OK" -ForegroundColor Green
    }
    
    if (-not (Test-Path $insightJson)) {
        $validation.files_exist = $false
        $validation.issues += "insight_spec_${lectureId}.json が見つかりません"
        Write-Host "  ❌ insight_spec: NOT FOUND" -ForegroundColor Red
    } else {
        Write-Host "  ✅ insight_spec: OK" -ForegroundColor Green
    }
    
    if (-not (Test-Path $ocrFile)) {
        $validation.issues += "Mk2_OCR_${lectureId}.txt が見つかりません"
        Write-Host "  ⚠️  OCR file: NOT FOUND" -ForegroundColor Yellow
    } else {
        $ocrSize = (Get-Item $ocrFile).Length
        Write-Host "  ℹ️  OCR file: $ocrSize bytes" -ForegroundColor Cyan
    }
    
    # Mk2_Core 検証
    if (Test-Path $coreJson) {
        try {
            $coreData = Get-Content $coreJson -Raw | ConvertFrom-Json
            $corePins = $coreData.knowledge_core.center_pins
            $validation.core_pins_count = $corePins.Count
            
            if ($corePins.Count -lt $MinCenterPins) {
                $validation.issues += "center_pins が少なすぎます（$($corePins.Count) 個）"
                Write-Host "  ⚠️  Center Pins (Core): $($corePins.Count) 個 (最小: $MinCenterPins 個)" -ForegroundColor Yellow
            } else {
                Write-Host "  ✅ Center Pins (Core): $($corePins.Count) 個" -ForegroundColor Green
            }
            
            # Content 長を確認
            $contentLengths = $corePins | ForEach-Object { $_.content.Length }
            if ($contentLengths.Count -gt 0) {
                $avgLen = [math]::Round(($contentLengths | Measure-Object -Average).Average, 0)
                $minLen = ($contentLengths | Measure-Object -Minimum).Minimum
                $validation.avg_content_length = $avgLen
                
                if ($minLen -lt $MinContentChars) {
                    $validation.issues += "content が短すぎるピンがあります（最小: $minLen 文字）"
                    Write-Host "  ⚠️  Content length (avg): $avgLen 文字, (min): $minLen 文字" -ForegroundColor Yellow
                } else {
                    Write-Host "  ✅ Content length (avg): $avgLen 文字, (min): $minLen 文字" -ForegroundColor Green
                }
            }
        }
        catch {
            $validation.issues += "Mk2_Core JSON パース失敗: $_"
            Write-Host "  ❌ JSON parse error: $_" -ForegroundColor Red
        }
    }
    
    # insight_spec 検証
    if (Test-Path $insightJson) {
        try {
            $insightData = Get-Content $insightJson -Raw | ConvertFrom-Json
            $insightPins = $insightData.knowledge_core.center_pins
            $validation.insight_pins_count = $insightPins.Count
            
            # ラベルの有無を確認
            $hasLabels = $false
            if ($insightPins.Count -gt 0 -and $null -ne $insightPins[0].labels) {
                $hasLabels = $true
                $validation.has_labels = $true
                Write-Host "  ✅ Labels: あり（business_theme, funnel_stage, difficulty）" -ForegroundColor Green
            } else {
                $validation.issues += "ラベルが付与されていません"
                Write-Host "  ❌ Labels: なし" -ForegroundColor Red
            }
            
            Write-Host "  ℹ️  Center Pins (insight_spec): $($insightPins.Count) 個" -ForegroundColor Cyan
        }
        catch {
            $validation.issues += "insight_spec JSON パース失敗: $_"
            Write-Host "  ❌ JSON parse error: $_" -ForegroundColor Red
        }
    }
    
    # サマリー
    if ($validation.issues.Count -eq 0) {
        Write-Host "  ✅ 検証成功：問題なし" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  検証失敗：$($validation.issues.Count) 件の問題" -ForegroundColor Yellow
        $validation.issues | ForEach-Object { Write-Host "     - $_" -ForegroundColor Yellow }
    }
    
    $results += $validation
}

# 結果サマリー（テーブル表示を修正）
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$successCount = ($results | Where-Object { $_.issues.Count -eq 0 }).Count
Write-Host "`n✅ 検証成功: $successCount/5 講座" -ForegroundColor Green

Write-Host "`nDetailed Results:" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Cyan

foreach ($r in $results) {
    $lectureId = $r.lecture_id
    $corePins = $r.core_pins_count
    $insightPins = $r.insight_pins_count
    $avgContent = $r.avg_content_length
    $hasLabels = if ($r.has_labels) { "✅" } else { "❌" }
    $issues = $r.issues.Count
    
    Write-Host "Lecture $lectureId | Core: $corePins | Insight: $insightPins | Avg: $avgContent chars | Labels: $hasLabels | Issues: $issues" -ForegroundColor Cyan
}

Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Cyan

# JSON で結果を保存
$resultsFile = "results/validation_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
New-Item -ItemType Directory -Path (Split-Path $resultsFile) -Force | Out-Null
$results | ConvertTo-Json -Depth 5 | Out-File -FilePath $resultsFile -Encoding UTF8
Write-Host "`n📁 結果ファイル: $resultsFile" -ForegroundColor Cyan
