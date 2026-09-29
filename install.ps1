<#
.SYNOPSIS
    把本仓库安装为 WorkBuddy 用户级技能（Windows PowerShell 版）。

.DESCRIPTION
    将 SKILL.md、references、assets、scripts、examples 复制到
    %USERPROFILE%\.workbuddy-ai\skills\jobready-career-assistant\。
    仓库管理文件（README、LICENSE、CI 配置等）不会被复制。

.PARAMETER Force
    目标目录已存在时直接覆盖，不再询问。

.PARAMETER Dir
    自定义技能根目录，默认为 %USERPROFILE%\.workbuddy-ai\skills

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install.ps1 -Force
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [string]$Dir
)

$ErrorActionPreference = 'Stop'

$SkillName = 'jobready-career-assistant'
$SrcDir    = Split-Path -Parent $MyInvocation.MyCommand.Path

if ([string]::IsNullOrWhiteSpace($Dir)) {
    $DestRoot = Join-Path $env:USERPROFILE '.workbuddy-ai\skills'
} else {
    $DestRoot = $Dir
}

$DestDir = Join-Path $DestRoot $SkillName
$Items   = @('SKILL.md', 'references', 'assets', 'scripts', 'examples')

Write-Host "源目录：  $SrcDir"
Write-Host "目标目录：$DestDir"
Write-Host ""

if (-not (Test-Path (Join-Path $SrcDir 'SKILL.md'))) {
    Write-Error "源目录下未找到 SKILL.md，请确认在仓库根目录执行本脚本。"
    exit 1
}

if (Test-Path $DestDir) {
    if (-not $Force) {
        $reply = Read-Host '目标目录已存在，是否覆盖？[y/N]'
        if ($reply -notmatch '^(y|yes)$') {
            Write-Host '已取消，未做任何修改。'
            exit 0
        }
    }
    Write-Host '正在移除旧版本……'
    Remove-Item -Recurse -Force $DestDir
}

New-Item -ItemType Directory -Path $DestDir -Force | Out-Null

foreach ($item in $Items) {
    $source = Join-Path $SrcDir $item
    if (Test-Path $source) {
        Copy-Item -Recurse -Force $source -Destination $DestDir
        Write-Host "  已安装 $item"
    } else {
        Write-Host "  跳过（不存在）$item"
    }
}

Write-Host ""
Write-Host "安装完成：$DestDir"

$python = $null
foreach ($candidate in @('python', 'py', 'python3')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}

if ($python) {
    Write-Host ""
    & $python (Join-Path $DestDir 'scripts\validate_skill.py') $DestDir
}

Write-Host ""
Write-Host "若技能未立即生效，请重启 WorkBuddy 客户端。"
