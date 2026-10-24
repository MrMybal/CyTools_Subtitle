$ErrorActionPreference = 'Stop'
$toolRoot = Split-Path -Parent $PSScriptRoot
$privatePython = Join-Path $toolRoot 'runtime/python/Scripts/python.exe'
if ((Test-Path -LiteralPath (Join-Path $toolRoot 'runtime/portable.json')) -and (Test-Path -LiteralPath $privatePython)) {
    Write-Host 'The portable runtime is already included. Launch CyTools_Subtitle.exe.'
    exit 0
}
if (-not (Test-Path -LiteralPath $privatePython)) {
    & py -3.11 -m venv (Join-Path $toolRoot 'runtime/python')
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 required; install it from python.org.' }
}
& $privatePython -m pip install --keyring-provider disabled --find-links (Join-Path $PSScriptRoot 'packages') --no-deps -r (Join-Path $PSScriptRoot 'requirements-base-windows.txt')
if ($LASTEXITCODE -ne 0) { throw 'Private runtime installation failed.' }
Write-Host 'Ready. Launch CyTools_Subtitle.exe; use Installation for PyTorch and model downloads.'
