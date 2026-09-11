param(
    [string]$AdbPath = 'C:\Program Files (x86)\MiFlashPro\adb.exe',
    [int]$TestSeconds = 25
)

$ErrorActionPreference = 'Stop'

function Adb([string[]]$Arguments) {
    ((& $AdbPath @Arguments 2>&1) | Out-String).Trim()
}

$originalAttention = Adb @('shell', 'settings', 'get', 'secure', 'adaptive_sleep')
$originalTimeout = Adb @('shell', 'settings', 'get', 'system', 'screen_off_timeout')

try {
    Adb @('shell', 'settings', 'put', 'secure', 'adaptive_sleep', '1') | Out-Null
    Adb @('shell', 'settings', 'put', 'system', 'screen_off_timeout', '10000') | Out-Null
    Adb @('logcat', '-b', 'all', '-c') | Out-Null
    Write-Output 'Look at the screen without touching it. Starting in 5 seconds...'
    Start-Sleep -Seconds 5
    Adb @('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP') | Out-Null
    Adb @('shell', 'input', 'keyevent', 'KEYCODE_HOME') | Out-Null
    Start-Sleep -Seconds $TestSeconds

    Write-Output '===== POWER ====='
    $power = Adb @('shell', 'dumpsys', 'power')
    $power -split "`r?`n" | Select-String -Pattern 'mWakefulness=|mIsSettingEnabled=|mAttentionServiceSupported=|mRequested=|Display Power:'
    Write-Output '===== ATTENTION LOG ====='
    $log = Adb @('logcat', '-b', 'all', '-d', '-v', 'threadtime')
    $log -split "`r?`n" | Select-String -Pattern 'AiAiAttention|AttentionManagerService|AttentionDetector'
} finally {
    if ($originalAttention -eq 'null') {
        Adb @('shell', 'settings', 'delete', 'secure', 'adaptive_sleep') | Out-Null
    } else {
        Adb @('shell', 'settings', 'put', 'secure', 'adaptive_sleep', $originalAttention) | Out-Null
    }
    Adb @('shell', 'settings', 'put', 'system', 'screen_off_timeout', $originalTimeout) | Out-Null
    Write-Output "Restored adaptive_sleep=$originalAttention, screen_off_timeout=$originalTimeout"
}
