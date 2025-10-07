#requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Move to repo root
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $repoRoot

Write-Host "[1/5] Ensuring Python and tools..." -ForegroundColor Cyan
# Prefer py launcher if available
$python = "python"
try {
  $pyVersion = (& py -3 -c "import sys;print(sys.version)" 2>$null)
  if ($LASTEXITCODE -eq 0) { $python = "py -3" }
} catch {}

# Create venv (optional but keeps build clean)
if (-not (Test-Path ".venv")) {
  & $python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1

Write-Host "[2/5] Installing dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
  pip install -r requirements.txt
}
pip install pyinstaller

Write-Host "[3/5] Building one-file GUI exe..." -ForegroundColor Cyan
# Entry point: enhanced unified GUI
$entry = "spp_toolkit_enhanced.py"
if (-not (Test-Path $entry)) { throw "Entry file not found: $entry" }

# Clean previous builds
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "SPPToolkit.spec") { Remove-Item -Force "SPPToolkit.spec" }

pyinstaller --noconfirm --clean --onefile --windowed --name SPPToolkit `
  "$entry"

$exePath = Join-Path "dist" "SPPToolkit.exe"
if (-not (Test-Path $exePath)) { throw "Build failed: $exePath not found" }

Write-Host "[4/5] Creating zip artifact..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "artifacts" | Out-Null
$zipPath = Join-Path "artifacts" "SPPToolkit.zip"
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path $exePath -DestinationPath $zipPath -Force

Write-Host "[5/5] Done." -ForegroundColor Green
Write-Host "Executable: $exePath"
Write-Host "Zip:        $zipPath"