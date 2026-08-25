param(
    [string]$OutputPath = ""
)

$ErrorActionPreference = "SilentlyContinue"

function Get-CommandText {
    param([string]$Command, [string[]]$CommandArgs)
    $cmd = Get-Command $Command -ErrorAction SilentlyContinue
    if (-not $cmd) { return "" }
    $job = $null
    try {
        $job = Start-Job -ScriptBlock {
            param($JobCommand, $JobArgs)
            & $JobCommand @JobArgs 2>$null
        } -ArgumentList $Command, (, $CommandArgs)
        if (Wait-Job $job -Timeout 5) {
            return (Receive-Job $job) -join "`n"
        }
        Stop-Job $job | Out-Null
        return ""
    } catch {
        return ""
    } finally {
        if ($job) {
            Remove-Job $job -Force -ErrorAction SilentlyContinue | Out-Null
        }
    }
}

$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$gpus = Get-CimInstance Win32_VideoController
$drives = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3"
$nvidia = Get-CommandText "nvidia-smi" @(
    "--query-gpu=name,memory.total,memory.free,driver_version",
    "--format=csv,noheader"
)
$conda = Get-CommandText "conda" @("--version")
$python = Get-CommandText "python" @("--version")

$ramGb = if ($os.TotalVisibleMemorySize) {
    [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
} else {
    ""
}

$diskLines = @()
foreach ($drive in $drives) {
    $freeGb = [math]::Round($drive.FreeSpace / 1GB, 2)
    $sizeGb = [math]::Round($drive.Size / 1GB, 2)
    $diskLines += "- $($drive.DeviceID) free ${freeGb}GB / total ${sizeGb}GB"
}

$gpuLines = @()
foreach ($gpu in $gpus) {
    $gpuLines += "- $($gpu.Name)"
}
if ($nvidia) {
    $gpuLines += ""
    $gpuLines += "nvidia-smi:"
    $gpuLines += ($nvidia -split "`n" | ForEach-Object { "- $_" })
}

$content = @"
# Hardware Profile

## Machine

- OS: $($os.Caption) $($os.Version)
- CPU: $($cpu.Name)
- RAM: ${ramGb}GB
- GPU:
$($gpuLines -join "`n")
- Disk free:
$($diskLines -join "`n")
- Conda: $conda
- Python: $python

## Experiment Budget

- Maximum runtime per run:
- Maximum total runtime:
- Maximum number of runs:
- Maximum dataset size:
- Maximum model size:

## Feasibility Notes

- Expected bottleneck:
- Scaling strategy:
- Risks:
- Assumptions:
"@

if ($OutputPath) {
    $content | Out-File -FilePath $OutputPath -Encoding utf8
} else {
    $content
}
