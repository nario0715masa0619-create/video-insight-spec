# ===============================================
# Free-Trial Dashboard Launcher v1.5.7
# Life Design Partners
# ===============================================

Write-Host ""
Write-Host "🚀 Free-Trial Dashboard v1.5.7 起動中（Life Design Partners）..." -ForegroundColor Green
Write-Host ""

# Step 1: プロセス停止
Write-Host "[Step 1] 既存プロセスを停止..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Step 2: キャッシュ削除
Write-Host "[Step 2] Streamlit キャッシュを削除..." -ForegroundColor Cyan
Remove-Item $env:USERPROFILE\.streamlit -Recurse -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Step 3: 環境変数設定
Write-Host "[Step 3] 環境変数を設定..." -ForegroundColor Cyan
$env:VIS_MODE="free_trial"
$env:PYTHONIOENCODING="utf-8"

# Step 4: Streamlit 起動
Write-Host "[Step 4] Streamlit を起動します..." -ForegroundColor Cyan
Write-Host ""
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host "Local URL: http://localhost:8501" -ForegroundColor Yellow
Write-Host "Network URL: http://192.168.0.241:8501" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "ダッシュボードが起動しています..." -ForegroundColor Green
Write-Host "ブラウザで上記URLにアクセスしてください。" -ForegroundColor Green
Write-Host ""

streamlit run streamlit_app/app.py --server.port=8501
