param(
  [Parameter(Mandatory)] [string] $EvidenceDirectory,
  [switch] $WithBackend
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$exe = Resolve-Path (Join-Path $root 'out/OpenFlight-Face-Impact-Windows/OpenFlight Face Impact.exe')
New-Item -ItemType Directory -Force -Path $EvidenceDirectory | Out-Null
$env:OPENFLIGHT_GATE11_SMOKE = '1'
$env:OPENFLIGHT_GATE11_EXPECT_BACKEND = if ($WithBackend) { '1' } else { '0' }
$env:OPENFLIGHT_PROFILES_PATH = Join-Path $EvidenceDirectory 'smoke-profiles.json'
# Exercise resource discovery. An inherited override could mask a missing bundle.
Remove-Item Env:OPENFLIGHT_BACKEND_EXECUTABLE -ErrorAction SilentlyContinue

function Wait-BackendPortReleased {
  $deadline = [DateTime]::UtcNow.AddSeconds(10)
  while (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue) {
    if ([DateTime]::UtcNow -ge $deadline) { throw 'Port 8080 still has a listener' }
    Start-Sleep -Milliseconds 200
  }
}

Wait-BackendPortReleased
$launches = if ($WithBackend) { 2 } else { 1 }
for ($launch = 1; $launch -le $launches; $launch++) {
  $env:OPENFLIGHT_GATE11_SCREENSHOT = Join-Path $EvidenceDirectory "dashboard-$launch.png"
  $env:OPENFLIGHT_GATE11_RESULT = Join-Path $EvidenceDirectory "result-$launch.json"
  $env:OPENFLIGHT_GATE11_EXPECT_SAVED_SESSION = if ($launch -eq 2) { '1' } else { '0' }
  $process = Start-Process -FilePath $exe -PassThru
  try {
    if (!$process.WaitForExit(90000)) { throw 'Packaged Electron smoke timed out' }
    if ($process.ExitCode -ne 0) { throw "Packaged Electron exited with $($process.ExitCode)" }
    $result = Get-Content -LiteralPath $env:OPENFLIGHT_GATE11_RESULT -Raw | ConvertFrom-Json
    if (!$result.ok) { throw "Packaged Electron smoke failed: $($result.error)" }
    if ($result.panels -ne 6 -or $result.backend_ready -ne $WithBackend.IsPresent -or
        $result.restored_session -ne ($launch -eq 2)) {
      throw 'Unexpected dashboard or backend state'
    }
    if (!(Test-Path -LiteralPath $env:OPENFLIGHT_GATE11_SCREENSHOT)) { throw 'Missing dashboard screenshot' }
    Wait-BackendPortReleased
    Write-Host "Packaged Electron launch ${launch}: six panels, mock backend ready=$($result.backend_ready), $($result.camera), restored session=$($result.restored_session), port 8080 released."
  } finally {
    if (!$process.HasExited) { taskkill.exe /PID $process.Id /T /F }
    $process.Dispose()
  }
}
