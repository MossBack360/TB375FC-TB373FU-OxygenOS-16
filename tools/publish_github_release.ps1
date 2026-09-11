param(
    [Parameter(Mandatory = $true)]
    [string]$Owner,

    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [Parameter(Mandatory = $true)]
    [string]$Tag,

    [Parameter(Mandatory = $true)]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [string]$BodyFile,

    [Parameter(Mandatory = $true)]
    [string[]]$Assets
)

$ErrorActionPreference = 'Stop'

function Get-GitHubToken {
    if ($env:GITHUB_TOKEN) {
        return $env:GITHUB_TOKEN
    }

    $query = "protocol=https`nhost=github.com`n`n"
    $result = $query | git credential fill
    foreach ($line in $result) {
        if ($line.StartsWith('password=')) {
            return $line.Substring('password='.Length)
        }
    }

    throw 'No GitHub token found in GITHUB_TOKEN or git credential manager.'
}

function Invoke-GitHubJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Method,

        [Parameter(Mandatory = $true)]
        [string]$Uri,

        [object]$Body = $null
    )

    $args = @{
        Method = $Method
        Uri = $Uri
        Headers = $script:Headers
        TimeoutSec = 60
    }

    if ($null -ne $Body) {
        $args.ContentType = 'application/json; charset=utf-8'
        $args.Body = ($Body | ConvertTo-Json -Depth 8)
    }

    Invoke-RestMethod @args
}

$token = Get-GitHubToken
Write-Host 'Authenticated'
$script:Headers = @{
    Authorization = "Bearer $token"
    Accept = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2022-11-28'
    'User-Agent' = 'fixO-release-uploader'
}

$body = Get-Content -Raw -LiteralPath $BodyFile
$apiBase = "https://api.github.com/repos/$Owner/$Repo"

try {
    Write-Host "Checking release $Tag"
    $release = Invoke-GitHubJson -Method Get -Uri "$apiBase/releases/tags/$Tag"
    Write-Host "Using existing release $Tag"
} catch {
    Write-Host "Creating release $Tag"
    $release = Invoke-GitHubJson -Method Post -Uri "$apiBase/releases" -Body @{
        tag_name = $Tag
        name = $Name
        body = $body
        draft = $false
        prerelease = $false
    }
    Write-Host "Created release $Tag"
}

foreach ($assetPath in $Assets) {
    $item = Get-Item -LiteralPath $assetPath
    $assetName = $item.Name
    Write-Host "Preparing $assetName"

    foreach ($asset in @($release.assets)) {
        if ($asset.name -eq $assetName) {
            Invoke-GitHubJson -Method Delete -Uri $asset.url | Out-Null
            Write-Host "Replaced existing asset $assetName"
        }
    }

    $contentType = if ($item.Extension -eq '.zip') { 'application/zip' } else { 'text/plain; charset=utf-8' }
    $uploadUri = "https://uploads.github.com/repos/$Owner/$Repo/releases/$($release.id)/assets?name=$([uri]::EscapeDataString($assetName))"
    Invoke-RestMethod -Method Post -Uri $uploadUri -Headers $script:Headers -ContentType $contentType -InFile $item.FullName -TimeoutSec 600 | Out-Null
    Write-Host "Uploaded $assetName"
}

Write-Host $release.html_url
