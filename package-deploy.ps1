param(
    [string]$OutputDir = ".",
    [string]$Prefix = "ai-platform-deploy"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$dateTag = Get-Date -Format "yyyyMMdd"
$packageName = "$Prefix-$dateTag.zip"
$outputRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $projectRoot $OutputDir)
)
$packagePath = Join-Path $outputRoot $packageName
$stagingRoot = Join-Path (
    [System.IO.Path]::GetTempPath()
) ("ai-platform-package-" + [System.Guid]::NewGuid().ToString("N"))
$stagingProject = Join-Path $stagingRoot "ai-platform"

$excludeDirNames = @(
    ".git",
    ".agents",
    ".claude",
    ".codex",
    ".uv-cache",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "storage",
    "YOLOconstructionSiteSeftyDetector-main",
    ".venv",
    "venv"
)

$excludeFileNames = @(
    ".env",
    ".env.local",
    ".DS_Store",
    "Thumbs.db"
)

$excludeExtensions = @(
    ".log",
    ".pyc",
    ".pyo",
    ".pyd",
    ".tsbuildinfo"
)

$excludeNamePatterns = @(
    "ai-platform-deploy-*.zip"
)

function Test-ExcludedPath {
    param(
        [System.IO.FileSystemInfo]$Item
    )

    if ($Item.PSIsContainer -and $excludeDirNames -contains $Item.Name) {
        return $true
    }

    if ($excludeFileNames -contains $Item.Name) {
        return $true
    }

    if ($excludeExtensions -contains $Item.Extension) {
        return $true
    }

    foreach ($pattern in $excludeNamePatterns) {
        if ($Item.Name -like $pattern) {
            return $true
        }
    }

    return $false
}

function Copy-ProjectItem {
    param(
        [string]$SourcePath,
        [string]$TargetPath
    )

    $item = Get-Item -LiteralPath $SourcePath -Force
    if (Test-ExcludedPath -Item $item) {
        return
    }

    if ($item.PSIsContainer) {
        New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
        foreach ($child in Get-ChildItem -LiteralPath $item.FullName -Force) {
            Copy-ProjectItem `
                -SourcePath $child.FullName `
                -TargetPath (Join-Path $TargetPath $child.Name)
        }
        return
    }

    $targetDir = Split-Path -Parent $TargetPath
    if (-not (Test-Path -LiteralPath $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    Copy-Item -LiteralPath $item.FullName -Destination $TargetPath -Force
}

if (-not (Test-Path -LiteralPath $outputRoot)) {
    New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
}

Get-ChildItem `
    -LiteralPath $outputRoot `
    -Filter "$Prefix-*.zip" `
    -File `
    -ErrorAction SilentlyContinue | Remove-Item -Force

New-Item -ItemType Directory -Path $stagingProject -Force | Out-Null

try {
    foreach ($child in Get-ChildItem -LiteralPath $projectRoot -Force) {
        Copy-ProjectItem `
            -SourcePath $child.FullName `
            -TargetPath (Join-Path $stagingProject $child.Name)
    }

    if (Test-Path -LiteralPath $packagePath) {
        Remove-Item -LiteralPath $packagePath -Force
    }

    Compress-Archive `
        -Path (Join-Path $stagingProject "*") `
        -DestinationPath $packagePath `
        -CompressionLevel Optimal

    Write-Host "Package created: $packagePath"
    Write-Host "Next steps:"
    Write-Host "1. Upload $packageName to the server"
    Write-Host "2. Extract it into the target directory"
    Write-Host "3. Copy docker.env.example to .env and update values"
    Write-Host "4. Run: docker compose --env-file .env up -d --build"
}
finally {
    if (Test-Path -LiteralPath $stagingRoot) {
        Remove-Item -LiteralPath $stagingRoot -Recurse -Force
    }
}
