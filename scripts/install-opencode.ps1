# install-opencode.ps1 - OpenCode + Fireworks + GLM-5.1 for Windows.
#
# Mirror of scripts/install-opencode.sh. Idempotent. Safe to re-run.
# Works from `irm ... | iex` (remote) or `powershell -File scripts\install-opencode.ps1` (local clone).
#
# Targets: PowerShell 5.1+ (pre-installed on Windows 10/11) and PowerShell 7+.
# Prereqs: Windows 10 1809+ (or Windows 11), winget OR scoop OR npm, .NET 4.7+.
#
# One-liner (PowerShell):
#   irm https://raw.githubusercontent.com/DefaultPerson/agent-setup/feat/opencode-support/scripts/install-opencode.ps1 | iex

[CmdletBinding()]
param(
    [string]$Ref = $(if ($env:AGENT_SETUP_REF) { $env:AGENT_SETUP_REF } else { 'feat/opencode-support' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'   # otherwise Invoke-WebRequest is painfully slow on PS 5.1

# TLS 1.2 is required on PS 5.1 to reach GitHub and Fireworks
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
} catch {
    Write-Verbose "TLS 1.2 setup skipped: $_"
}

# --- config -------------------------------------------------------------------

$Repo     = 'DefaultPerson/agent-setup'
$Raw      = "https://raw.githubusercontent.com/$Repo/$Ref"

$ConfigDir   = Join-Path $env:USERPROFILE '.config\opencode'
$CommandsDir = Join-Path $ConfigDir 'commands'

$Commands = @('commit', 'prime', 'push-and-pr', 'publish', 'release', 'research', 'ultrathink')

# --- ui helpers ---------------------------------------------------------------

function Write-Ok   { param($Msg) Write-Host "[OK]  $Msg" -ForegroundColor Green }
function Write-Info { param($Msg) Write-Host "[..]  $Msg" -ForegroundColor DarkGray }
function Write-Warn { param($Msg) Write-Host "[!!]  $Msg" -ForegroundColor Yellow }
function Die        { param($Msg) Write-Host "[ERR] $Msg" -ForegroundColor Red; exit 1 }

# --- 1. install opencode CLI --------------------------------------------------

function Test-Command {
    param($Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

if (Test-Command 'opencode') {
    $ver = (& opencode --version 2>$null) -join ' '
    Write-Ok "opencode already installed ($ver)"
}
else {
    $installed = $false

    if (Test-Command 'winget') {
        Write-Info 'installing opencode via winget (SST.opencode)'
        try {
            & winget install --exact --id SST.opencode `
                --accept-source-agreements --accept-package-agreements `
                --silent | Out-Null
            if ($LASTEXITCODE -eq 0) { $installed = $true }
        } catch { Write-Warn "winget install failed: $_" }
    }

    if (-not $installed -and (Test-Command 'scoop')) {
        Write-Info 'installing opencode via scoop'
        try {
            & scoop install opencode | Out-Null
            if ($LASTEXITCODE -eq 0) { $installed = $true }
        } catch { Write-Warn "scoop install failed: $_" }
    }

    if (-not $installed -and (Test-Command 'npm')) {
        Write-Info 'installing opencode via npm (opencode-ai)'
        try {
            & npm install -g opencode-ai | Out-Null
            if ($LASTEXITCODE -eq 0) { $installed = $true }
        } catch { Write-Warn "npm install failed: $_" }
    }

    if (-not $installed) {
        Die 'could not install opencode: none of winget/scoop/npm worked. Install winget from Microsoft Store (App Installer), then re-run.'
    }

    # winget may not propagate PATH to the current session; refresh from registry
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath    = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machinePath;$userPath"

    if (-not (Test-Command 'opencode')) {
        Die 'opencode installed but not on PATH. Open a NEW PowerShell window and re-run.'
    }
    Write-Ok 'opencode installed'
}

# --- 2. create config dirs ----------------------------------------------------

New-Item -ItemType Directory -Force -Path $CommandsDir | Out-Null
Write-Ok "config dir ready: $ConfigDir"

# --- 3. fetch or copy template files ------------------------------------------

# Detect local clone: if $PSScriptRoot\..\.opencode\opencode.json exists, use it.
$LocalRepo = $null
if ($PSScriptRoot) {
    $candidate = Resolve-Path (Join-Path $PSScriptRoot '..') -ErrorAction SilentlyContinue
    if ($candidate -and (Test-Path (Join-Path $candidate '.opencode\opencode.json'))) {
        $LocalRepo = $candidate.Path
    }
}

function Get-TemplateFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$RemotePath,
        [Parameter(Mandatory)][string]$Destination
    )
    if ($LocalRepo) {
        $src = Join-Path $LocalRepo $RemotePath
        if (-not (Test-Path $src)) { Die "local file missing: $src" }
        Copy-Item -Force -Path $src -Destination $Destination
    }
    else {
        $url = "$Raw/$($RemotePath -replace '\\','/')"
        try {
            Invoke-WebRequest -Uri $url -OutFile $Destination -UseBasicParsing
        } catch {
            Die "failed to fetch $url : $_"
        }
    }
}

if ($LocalRepo) {
    Write-Info "source: local repo ($LocalRepo)"
} else {
    Write-Info "source: $Raw"
}

Get-TemplateFile -RemotePath '.opencode/opencode.json' -Destination (Join-Path $ConfigDir 'opencode.json')
Get-TemplateFile -RemotePath 'AGENTS.md'                -Destination (Join-Path $ConfigDir 'AGENTS.md')
foreach ($cmd in $Commands) {
    Get-TemplateFile -RemotePath ".claude/commands/$cmd.md" -Destination (Join-Path $CommandsDir "$cmd.md")
}
Write-Ok "template files installed (config + AGENTS.md + $($Commands.Count) commands)"

# --- 4. prompt for Fireworks API key ------------------------------------------

function Get-PersistedUserEnv {
    param($Name)
    return [Environment]::GetEnvironmentVariable($Name, 'User')
}

function Save-UserEnvVar {
    param($Name, $Value)
    [Environment]::SetEnvironmentVariable($Name, $Value, 'User')
    Set-Item -Path "Env:$Name" -Value $Value     # also expose in current session
}

$apiKey = $env:FIREWORKS_API_KEY
if (-not $apiKey) { $apiKey = Get-PersistedUserEnv 'FIREWORKS_API_KEY' }

if (-not $apiKey) {
    Write-Host ''
    Write-Host 'Get a Fireworks API key at: https://fireworks.ai/account/api-keys'
    $secure = Read-Host -Prompt 'Enter your FIREWORKS_API_KEY' -AsSecureString
    $bstr   = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if ([string]::IsNullOrWhiteSpace($apiKey)) { Die 'empty FIREWORKS_API_KEY' }

    Save-UserEnvVar 'FIREWORKS_API_KEY' $apiKey
    Write-Ok 'FIREWORKS_API_KEY saved to User environment (persists across sessions)'
} else {
    $env:FIREWORKS_API_KEY = $apiKey
    Write-Info 'FIREWORKS_API_KEY already set'
}

# --- 5. resolve GLM-5.1 slug from live catalog --------------------------------

Write-Info 'resolving GLM-5.1 slug from Fireworks catalog'
$modelsList = $null
try {
    $modelsList = Invoke-RestMethod `
        -Uri 'https://api.fireworks.ai/inference/v1/models' `
        -Headers @{ 'Authorization' = "Bearer $apiKey" } `
        -Method Get
} catch {
    Die "failed to query Fireworks /v1/models: $_"
}

$glmIds = @()
if ($modelsList -and $modelsList.data) {
    $glmIds = $modelsList.data | Where-Object { $_.id -and ($_.id.ToLower() -like '*glm-5*') } | ForEach-Object { $_.id }
}

if (-not $glmIds -or $glmIds.Count -eq 0) {
    Die 'no GLM-5 model visible to this API key (check Fireworks dashboard/tier)'
}

# Prefer 5.1-flavored slugs, then 5.0, then anything
function Get-SlugPriority {
    param($Id)
    $lower = $Id.ToLower()
    if ($lower -match '5p1' -or $lower -match '5-1' -or $lower -match '5\.1') { return 0 }
    if ($lower -match '5p0' -or $lower -match '5-0' -or $lower -match '5\.0') { return 1 }
    return 2
}
$slug = $glmIds | Sort-Object { Get-SlugPriority $_ }, { $_ } | Select-Object -First 1
Write-Ok "resolved model: $slug"

# --- 6. rewrite placeholder in config -----------------------------------------

$configPath = Join-Path $ConfigDir 'opencode.json'
$content = [System.IO.File]::ReadAllText($configPath)
$content = $content.Replace('{{GLM_MODEL_ID}}', $slug)

# Write back as UTF-8 without BOM (OpenCode / Node strict parsers dislike BOM)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($configPath, $content, $utf8NoBom)

# Validate: parses as JSON and no placeholder left
try {
    $null = Get-Content $configPath -Raw | ConvertFrom-Json
} catch {
    Die "rewritten $configPath is not valid JSON: $_"
}
if ((Get-Content $configPath -Raw).Contains('{{GLM_MODEL_ID}}')) {
    Die "placeholder not fully replaced in $configPath"
}
Write-Ok 'config rewritten with live slug'

# --- 7. smoke test chat-completions -------------------------------------------

Write-Info 'smoke-testing Fireworks chat completions'
$payload = @{
    model      = $slug
    max_tokens = 8
    messages   = @(@{ role = 'user'; content = 'ping' })
} | ConvertTo-Json -Depth 5 -Compress

$smoke = $null
try {
    $smoke = Invoke-RestMethod `
        -Uri 'https://api.fireworks.ai/inference/v1/chat/completions' `
        -Method Post `
        -Headers @{ 'Authorization' = "Bearer $apiKey" } `
        -ContentType 'application/json' `
        -Body $payload
} catch {
    Die "Fireworks chat/completions failed: $_"
}

$smokeText = $null
if ($smoke -and $smoke.choices -and $smoke.choices.Count -gt 0) {
    $smokeText = $smoke.choices[0].message.content
}
if ([string]::IsNullOrEmpty($smokeText)) {
    Die 'smoke test returned empty content'
}
$preview = if ($smokeText.Length -gt 40) { $smokeText.Substring(0, 40) } else { $smokeText }
Write-Ok "smoke test passed ($preview)"

# --- done ---------------------------------------------------------------------

Write-Host ''
Write-Host '[OK] OpenCode setup complete.' -ForegroundColor Green
Write-Host "     Config:   $configPath"   -ForegroundColor DarkGray
Write-Host "     Commands: $CommandsDir ($($Commands.Count) files)" -ForegroundColor DarkGray
Write-Host "     Model:    $slug"         -ForegroundColor DarkGray
Write-Host ''
Write-Host 'Next: open a NEW PowerShell window (so FIREWORKS_API_KEY is loaded from User env) and run:'
Write-Host '  opencode'
Write-Host ''
