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
$closeModes = if ($WithBackend) { @('internal', 'window', 'backend-loss', 'window') } else { @('internal') }
for ($launch = 1; $launch -le $closeModes.Count; $launch++) {
  $env:OPENFLIGHT_GATE11_SCREENSHOT = Join-Path $EvidenceDirectory "dashboard-$launch.png"
  $env:OPENFLIGHT_GATE11_RESULT = Join-Path $EvidenceDirectory "result-$launch.json"
  $closeMode = $closeModes[$launch - 1]
  $env:OPENFLIGHT_GATE11_CLOSE_MODE = $closeMode
  $env:OPENFLIGHT_GATE11_EXPECT_SAVED_SESSION = if ($launch -gt 1) { '1' } else { '0' }
  $env:OPENFLIGHT_GATE11_EXPECT_REJECTED_SHOT = if ($launch -eq 4) { '1' } else { '0' }
  $process = Start-Process -FilePath $exe -PassThru
  try {
    if (!$process.WaitForExit(90000)) { throw 'Packaged Electron smoke timed out' }
    if ($process.ExitCode -ne 0) { throw "Packaged Electron exited with $($process.ExitCode)" }
    $result = Get-Content -LiteralPath $env:OPENFLIGHT_GATE11_RESULT -Raw | ConvertFrom-Json
    if (!$result.ok) { throw "Packaged Electron smoke failed: $($result.error)" }
    if ($result.panels -ne 6 -or $result.backend_ready -ne $WithBackend.IsPresent -or
        $result.restored_session -ne ($launch -gt 1) -or $result.exported_session -ne ($launch -gt 1) -or
        $result.restored_rejection -ne ($launch -eq 4) -or $result.close_mode -ne $closeMode -or
        $result.reconnected -ne ($WithBackend -and $launch -eq 1)) {
      throw 'Unexpected dashboard or backend state'
    }
    if (!(Test-Path -LiteralPath $env:OPENFLIGHT_GATE11_SCREENSHOT)) { throw 'Missing dashboard screenshot' }
    if ($WithBackend) {
      $expectedShutdown = if ($closeMode -eq 'backend-loss') { 'already-exited' } else { 'graceful' }
      if ($result.backend_shutdown -ne $expectedShutdown) {
        throw "Backend shutdown for ${closeMode}: expected $expectedShutdown, got $($result.backend_shutdown)"
      }
      if (Get-Process -Id $result.backend_pid -ErrorAction SilentlyContinue) { throw 'Owned backend process still running' }
    }
    Wait-BackendPortReleased
    Write-Host "Packaged Electron launch ${launch}: six panels, mock backend ready=$($result.backend_ready), $($result.camera), restored session=$($result.restored_session), exported session=$($result.exported_session), reconnected=$($result.reconnected), close=$closeMode, backend shutdown=$($result.backend_shutdown), port 8080 released."
  } finally {
    if (!$process.HasExited) { taskkill.exe /PID $process.Id /T /F }
    $process.Dispose()
  }
}
