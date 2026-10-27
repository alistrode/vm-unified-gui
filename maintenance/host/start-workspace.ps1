param([switch]$VerifyOnly)
$ErrorActionPreference='Stop'
$projectUri='http://127.0.0.1:48080/'
try {
    $page=Invoke-WebRequest -Uri $projectUri -UseBasicParsing -TimeoutSec 8
    if($page.StatusCode -ne 200 -or $page.Content -notmatch 'id="display"') { throw 'Project dashboard did not respond correctly.' }
    $containers=Invoke-RestMethod -Uri ($projectUri+'api/status') -TimeoutSec 8
    $names=@($containers | ForEach-Object { $_.Name })
    foreach($name in @('unified-a','unified-b','unified-c')) {
        if($name -notin $names) { throw ('Application container is unavailable: '+$name) }
    }
    $display=Invoke-WebRequest -Uri ($projectUri+'display/') -UseBasicParsing -TimeoutSec 8
    if($display.StatusCode -ne 200) { throw 'Graphical session is unavailable.' }
    if($VerifyOnly) { Write-Output 'PROJECT_CONNECTION_OK'; exit 0 }
    $edge='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    if(-not (Test-Path -LiteralPath $edge)) { $edge='C:\Program Files\Microsoft\Edge\Application\msedge.exe' }
    if(Test-Path -LiteralPath $edge) {
        Start-Process -FilePath $edge -ArgumentList @('--app='+$projectUri,'--start-maximized','--user-data-dir=E:\VM-Unified-GUI\host-ui-profile')
    } else { Start-Process $projectUri }
} catch {
    if($VerifyOnly) { Write-Error $_; exit 1 }
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show('Cannot connect to the existing Linux project. This launcher never starts or modifies the virtual machine.','Unified Workspace',0,48) | Out-Null
    exit 1
}
