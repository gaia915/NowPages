# Planetarium Events Page Generator (PowerShell runner)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Planetarium Event Page Generator" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Checking Python dependencies..." -ForegroundColor Green
python -m pip install -r requirements.txt -q

Write-Host "[2/2] Fetching events and generating pages..." -ForegroundColor Green
python -X utf8 main.py

$htmlPath = Join-Path $scriptDir "dist\index.html"
Write-Host "`n======================================================" -ForegroundColor Cyan
Write-Host "  Done! Opening dist\index.html in browser..." -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Cyan

Start-Process $htmlPath
