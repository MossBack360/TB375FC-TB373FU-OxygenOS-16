param(
    [string]$RepositoryRoot = (Get-Location).Path,
    [string]$AdbPath = 'C:\Program Files (x86)\MiFlashPro\adb.exe',
    [string]$OutputPath = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not (Test-Path -LiteralPath $AdbPath)) {
    throw "ADB executable not found: $AdbPath"
}

$deviceLines = & $AdbPath devices
if ($LASTEXITCODE -ne 0 -or -not ($deviceLines -match "`tdevice$")) {
    throw 'No authorized ADB device is connected.'
}

$scriptPath = Join-Path $PSScriptRoot 'capture_device_state.sh'
& $AdbPath push $scriptPath /data/local/tmp/fixo_capture_device_state.sh | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to push the device snapshot helper.'
}

$snapshot = & $AdbPath shell su -c 'sh /data/local/tmp/fixo_capture_device_state.sh'
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to capture rooted device state.'
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $RepositoryRoot 'reports\LIVE_DEVICE_STATE.txt'
}
$parent = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $parent | Out-Null
$snapshot | Set-Content -Encoding utf8 -LiteralPath $OutputPath
Write-Output $OutputPath
