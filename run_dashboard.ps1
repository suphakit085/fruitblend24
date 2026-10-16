$ErrorActionPreference = 'Stop'
$dashboardPython = Join-Path $PSScriptRoot '.venv-dashboard\Scripts\python.exe'
$dashboardFolder = Join-Path $PSScriptRoot 'dashboard'
if (-not (Test-Path -LiteralPath $dashboardPython)) {
    throw 'ไม่พบ environment กรุณาติดตั้งตาม dashboard/README.md'
}
Push-Location $dashboardFolder
try {
    & $dashboardPython -m streamlit run app.py
} finally {
    Pop-Location
}
