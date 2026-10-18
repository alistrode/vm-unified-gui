[CmdletBinding()]
param(
    [string]$VMName = 'Ubuntu-MultiContainer-GUI',
    [string]$ProjectRoot = 'E:\VM-Unified-GUI',
    [int]$WaitSeconds = 240,
    [switch]$NoBrowser,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$url = 'http://127.0.0.1:48080/'

function Get-HostPressure {
    $os = Get-CimInstance Win32_OperatingSystem
    $processors = Get-CimInstance Win32_Processor
    $disk = Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk -Filter "Name='_Total'" -ErrorAction SilentlyContinue
    [pscustomobject]@{
        sampled_at = (Get-Date).ToString('o')
        cpu_percent = [math]::Round(($processors | Measure-Object LoadPercentage -Average).Average, 1)
        memory_percent = [math]::Round(100 * (1 - $os.FreePhysicalMemory / $os.TotalVisibleMemorySize), 1)
        memory_free_mib = [int]($os.FreePhysicalMemory / 1024)
        memory_total_mib = [int]($os.TotalVisibleMemorySize / 1024)
        disk_busy_percent = $disk.PercentDiskTime
        disk_bytes_per_second = $disk.DiskBytesPersec
        disk_queue = $disk.CurrentDiskQueueLength
    }
}
function Show-Pressure {
    $p = Get-HostPressure
    Write-Host ('Hardware: CPU {0}% | memory {1}% ({2} MiB free) | disk busy {3}% | disk queue {4}' -f $p.cpu_percent,$p.memory_percent,$p.memory_free_mib,$p.disk_busy_percent,$p.disk_queue)
    return $p
}
function Invoke-VBox([string[]]$Arguments) {
    $result = & $script:VBox @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw ('VirtualBox failed: ' + ($result -join "`n")) }
    return $result
}
function Get-VMState {
    $lines = Invoke-VBox @('showvminfo', $VMName, '--machinereadable')
    $state = @{}
    foreach ($line in $lines) {
        if ($line -match '^([^=]+)=(.*)$') { $state[$matches[1]] = $matches[2].Trim('"') }
    }
    return $state
}
function Test-Workbench {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        return $response.StatusCode -eq 200
    } catch { return $false }
}

$install = (Get-ItemProperty 'HKLM:\SOFTWARE\Oracle\VirtualBox' -ErrorAction SilentlyContinue).InstallDir
$script:VBox = if ($install) { Join-Path $install 'VBoxManage.exe' } else { $null }
if (!$script:VBox -or !(Test-Path -LiteralPath $script:VBox)) {
    $command = Get-Command VBoxManage.exe -ErrorAction SilentlyContinue
    if ($command) { $script:VBox = $command.Source }
}
if (!$script:VBox -or !(Test-Path -LiteralPath $script:VBox)) { throw 'VirtualBox was not found. This launcher uses the existing installation.' }
$state = Get-VMState
$pressure = Show-Pressure
Write-Host ('VM: {0} | state {1} | {2} MiB | {3} CPU' -f $VMName,$state.VMState,$state.memory,$state.cpus)
if ($CheckOnly) {
    [pscustomobject]@{ vm=$VMName; state=$state.VMState; http_ready=(Test-Workbench); pressure=$pressure } | ConvertTo-Json -Depth 4
    exit 0
}
if ($state.VMState -in @('poweroff','aborted')) {
    $reserve = [math]::Max(2048, [int]($pressure.memory_total_mib * 0.2))
    $need = [int]$state.memory + $reserve
    if ($pressure.memory_free_mib -lt $need) {
        throw ('Available memory is {0} MiB; this VM needs {1} MiB plus a {2} MiB host reserve. Close unused applications before starting.' -f $pressure.memory_free_mib,$state.memory,$reserve)
    }
    $deadline = (Get-Date).AddSeconds(120)
    while ($pressure.cpu_percent -gt 85 -or $pressure.disk_queue -gt 4) {
        if ((Get-Date) -gt $deadline) { throw 'Host load remains high; the VM has not been started.' }
        Write-Host 'Waiting for host load to fall before starting the VM...'
        Start-Sleep -Seconds 5
        $pressure = Show-Pressure
    }
    Write-Host 'Starting existing VM in headless mode...'
    Invoke-VBox @('startvm', $VMName, '--type', 'headless') | Write-Host
} elseif ($state.VMState -eq 'saved') {
    Invoke-VBox @('startvm', $VMName, '--type', 'headless') | Write-Host
} elseif ($state.VMState -eq 'paused') {
    Invoke-VBox @('controlvm', $VMName, 'resume') | Write-Host
} elseif ($state.VMState -ne 'running') { throw ('Unexpected VM state: ' + $state.VMState) }

$deadline = (Get-Date).AddSeconds($WaitSeconds)
$nextPressure = Get-Date
while (!(Test-Workbench)) {
    if ((Get-Date) -gt $deadline) {
        $state = Get-VMState
        throw ('Workbench did not become ready at {0}; VM state: {1}. Existing VM and application data have been preserved.' -f $url,$state.VMState)
    }
    if ((Get-Date) -ge $nextPressure) { $null = Show-Pressure; $nextPressure = (Get-Date).AddSeconds(15) }
    Start-Sleep -Seconds 2
}
Write-Host ('Workbench is ready: ' + $url)
$null = Show-Pressure
if (!$NoBrowser) { Start-Process $url }
