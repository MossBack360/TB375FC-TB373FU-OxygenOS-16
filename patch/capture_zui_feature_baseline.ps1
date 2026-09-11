param(
    [string]$RepositoryRoot = 'C:\Users\GY\Documents\GitHub\fixO',
    [string]$AdbPath = 'C:\Program Files (x86)\MiFlashPro\adb.exe',
    [string]$Label = 'zui',
    [switch]$NoRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Invoke-AdbText([string[]]$CommandArgs) {
    ((& $AdbPath @CommandArgs 2>&1) | Out-String).TrimEnd()
}

function Add-Section([Text.StringBuilder]$Builder, [string]$Title, [string]$Body) {
    [void]$Builder.AppendLine("===== $Title =====")
    [void]$Builder.AppendLine($Body)
    [void]$Builder.AppendLine()
}

if (-not (Test-Path -LiteralPath $AdbPath)) {
    throw "ADB executable not found: $AdbPath"
}

$devices = Invoke-AdbText @('devices', '-l')
if ($devices -notmatch '\sdevice\b') {
    throw "No authorized ADB device is connected.`n$devices"
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outputDir = Join-Path $RepositoryRoot "out\$Label-feature-baseline-$stamp"
$packageDir = Join-Path $outputDir 'packages'
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null

$report = [Text.StringBuilder]::new()
Add-Section $report 'HOST' "captured_at=$((Get-Date).ToString('o'))`nlabel=$Label`nrepository=$RepositoryRoot"
Add-Section $report 'ADB' $devices
Add-Section $report 'BUILD' (Invoke-AdbText @('shell', 'getprop', 'ro.build.fingerprint'))

$allProperties = Invoke-AdbText @('shell', 'getprop')
$propertyPattern = 'aon|attention|aiunit|adaptive|zram|swap|memory|ram|product|device|fingerprint|build\.version'
$relevantProperties = ($allProperties -split "`r?`n" | Select-String -Pattern $propertyPattern -CaseSensitive:$false | ForEach-Object Line) -join "`n"
Add-Section $report 'RELEVANT PROPERTIES' $relevantProperties

foreach ($namespace in 'secure', 'system', 'global') {
    $settings = Invoke-AdbText @('shell', 'settings', 'list', $namespace)
    $filtered = ($settings -split "`r?`n" | Select-String -Pattern 'attention|adaptive_sleep|screen|aon|zram|swap|memory|ram' -CaseSensitive:$false | ForEach-Object Line) -join "`n"
    Add-Section $report "SETTINGS $($namespace.ToUpperInvariant())" $filtered
}

$attentionComponent = Invoke-AdbText @('shell', 'cmd', 'attention', 'getAttentionServiceComponent')
Add-Section $report 'ATTENTION COMPONENT' $attentionComponent
Add-Section $report 'ATTENTION BEFORE TEST' (Invoke-AdbText @('shell', 'dumpsys', 'attention'))
Add-Section $report 'FEATURES' (Invoke-AdbText @('shell', 'pm', 'list', 'features'))
Add-Section $report 'OVERLAYS' (Invoke-AdbText @('shell', 'cmd', 'overlay', 'list'))

[void](Invoke-AdbText @('logcat', '-b', 'all', '-c'))
$attentionDispatch = Invoke-AdbText @('shell', 'cmd', 'attention', 'call', 'checkAttention')
Start-Sleep -Seconds 3
$attentionResult = Invoke-AdbText @('shell', 'cmd', 'attention', 'getLastTestCallbackCode')
$attentionAfter = Invoke-AdbText @('shell', 'dumpsys', 'attention')
$attentionLog = Invoke-AdbText @('logcat', '-b', 'all', '-d', '-v', 'threadtime')
Add-Section $report 'ATTENTION TEST' "dispatch=$attentionDispatch`ncallback_code=$attentionResult"
Add-Section $report 'ATTENTION AFTER TEST' $attentionAfter
$attentionLog | Set-Content -Encoding utf8 -LiteralPath (Join-Path $outputDir 'attention-logcat.txt')

$rootProbe = if ($NoRoot) { 'skipped by -NoRoot' } else { Invoke-AdbText @('shell', 'su', '-c', 'id') }
$rooted = -not $NoRoot -and $rootProbe -match 'uid=0'
Add-Section $report 'ROOT' "available=$rooted`n$rootProbe"

$memoryCommands = @(
    'cat /proc/swaps',
    'cat /sys/block/zram0/disksize',
    'cat /sys/block/zram0/backing_dev',
    'cat /sys/block/zram0/mm_stat',
    'cat /sys/block/zram0/bd_stat',
    'df -h /data'
)
foreach ($command in $memoryCommands) {
    $commandArgs = if ($rooted) { @('shell', 'su', '-c', $command) } else { @('shell', 'sh', '-c', $command) }
    Add-Section $report "MEMORY: $command" (Invoke-AdbText $commandArgs)
}

$hashLines = [Collections.Generic.List[string]]::new()
$inventoryCommand = 'find /system /system_ext /product /my_product /vendor -type f 2>/dev/null'
$allFeatureFiles = if ($NoRoot) {
    ''
} elseif ($rooted) {
    Invoke-AdbText @('shell', 'su', '-c', $inventoryCommand)
} else {
    Invoke-AdbText @('shell', 'sh', '-c', $inventoryCommand)
}
$featureFiles = @($allFeatureFiles -split "`r?`n" | Select-String -Pattern 'aon|attention|aiunit|zram|nandswap|swap' -CaseSensitive:$false | ForEach-Object Line)
Add-Section $report 'FEATURE FILE INVENTORY' ($featureFiles -join "`n")

$featureDir = Join-Path $outputDir 'feature-files'
foreach ($remotePath in ($featureFiles | Where-Object { $_ -match '\.(apk|xml|rc|prop|json|conf|txt)$' })) {
    $relativePath = $remotePath.TrimStart('/').Replace('/', '\')
    $localPath = Join-Path $featureDir $relativePath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $localPath) | Out-Null
    & $AdbPath pull $remotePath $localPath | Out-Null
    if (Test-Path -LiteralPath $localPath) {
        $hash = (Get-FileHash -LiteralPath $localPath -Algorithm SHA256).Hash.ToLowerInvariant()
        $snapshotPath = $localPath.Substring($outputDir.Length).TrimStart('\')
        $hashLines.Add("$hash  $snapshotPath")
    }
}

$packageNames = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
[void]$packageNames.Add('android')
[void]$packageNames.Add('com.android.settings')
[void]$packageNames.Add('com.android.systemui')
if ($attentionComponent -match '^([^/]+)/') {
    [void]$packageNames.Add($Matches[1])
}
$packageList = Invoke-AdbText @('shell', 'pm', 'list', 'packages')
$relevantPackages = @($packageList -split "`r?`n" | Select-String -Pattern 'attention|aon|aiunit|memory|zram' -CaseSensitive:$false | ForEach-Object Line)
Add-Section $report 'RELEVANT PACKAGES' ($relevantPackages -join "`n")
foreach ($packageLine in $relevantPackages) {
    if ($packageLine -match '^package:(.+)$') {
        $candidatePackage = $Matches[1]
        if ($candidatePackage -match 'attention|aon|aiunit') {
            [void]$packageNames.Add($candidatePackage)
        }
    }
}

foreach ($packageName in $packageNames) {
    Add-Section $report "PACKAGE $packageName" (Invoke-AdbText @('shell', 'dumpsys', 'package', $packageName))
    $paths = Invoke-AdbText @('shell', 'pm', 'path', $packageName)
    Add-Section $report "PACKAGE PATHS $packageName" $paths
    $destination = Join-Path $packageDir $packageName
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    $packagePaths = $paths -split "`r?`n" | Where-Object { $_ -match '^package:/' } | ForEach-Object { $_ -replace '^package:', '' }
    foreach ($remotePath in $packagePaths) {
        $localPath = Join-Path $destination (Split-Path $remotePath -Leaf)
        & $AdbPath pull $remotePath $localPath | Out-Null
        if (Test-Path -LiteralPath $localPath) {
            $hash = (Get-FileHash -LiteralPath $localPath -Algorithm SHA256).Hash.ToLowerInvariant()
            $relativePath = $localPath.Substring($outputDir.Length).TrimStart('\')
            $hashLines.Add("$hash  $relativePath")
        }
    }
}

$hashLines | Set-Content -Encoding ascii -LiteralPath (Join-Path $outputDir 'SHA256SUMS.txt')
$report.ToString() | Set-Content -Encoding utf8 -LiteralPath (Join-Path $outputDir 'baseline.txt')
Write-Output $outputDir
