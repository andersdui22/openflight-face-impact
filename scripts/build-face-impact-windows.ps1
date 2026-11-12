# Gate 10: Build an unpackaged portable Electron directory (NOT a release).
# Run from repository root on Windows with Node/npm installed.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ui = Join-Path $root 'ui'
Push-Location $ui
try {
  npm ci
  if ($LASTEXITCODE -ne 0) { throw 'npm ci failed' }
  npm run build
  if ($LASTEXITCODE -ne 0) { throw 'npm run build failed' }
} finally { Pop-Location }
$electron = Join-Path $ui 'node_modules/electron/dist'
if (!(Test-Path (Join-Path $electron 'electron.exe'))) {
  # npm installations with restricted lifecycle scripts can skip Electron's
  # postinstall download. Invoke its official install script explicitly.
  Push-Location $ui
  try {
    node node_modules/electron/install.js
    if ($LASTEXITCODE -ne 0) { throw 'Electron runtime installation failed' }
  } finally { Pop-Location }
}
if (!(Test-Path (Join-Path $electron 'electron.exe'))) { throw 'Electron Windows binary missing after install' }
$output = Join-Path $root 'out/OpenFlight-Face-Impact-Windows'
if (Test-Path $output) { Remove-Item $output -Recurse -Force }
New-Item -ItemType Directory -Force -Path $output | Out-Null
Copy-Item (Join-Path $electron '*') $output -Recurse -Force
Rename-Item (Join-Path $output 'electron.exe') 'OpenFlight Face Impact.exe'
$appDir = Join-Path $output 'resources/app'
# A separately built Python backend can be staged for a development-only bundle.
# Never claim hardware validation or silently include an arbitrary executable.
$backendSource = $env:OPENFLIGHT_BACKEND_BUILD_EXE
if ($backendSource) {
  if (!(Test-Path -LiteralPath $backendSource -PathType Leaf)) {
    throw 'OPENFLIGHT_BACKEND_BUILD_EXE must point to an existing backend executable'
  }
  $backendSource = (Resolve-Path -LiteralPath $backendSource).Path
  if ([System.IO.Path]::GetExtension($backendSource).ToLowerInvariant() -ne '.exe') {
    throw 'Backend staging requires an .exe file'
  }
  $backendDir = Join-Path $output 'resources/backend'
  New-Item -ItemType Directory -Force -Path $backendDir | Out-Null
  Copy-Item -LiteralPath $backendSource -Destination (Join-Path $backendDir 'OpenFlightFaceImpactBackend.exe')
  $dependencies = Join-Path (Split-Path -Parent $backendSource) '_internal'
  if (Test-Path -LiteralPath $dependencies -PathType Container) {
    Copy-Item -LiteralPath $dependencies -Destination $backendDir -Recurse
  }
}

New-Item -ItemType Directory -Force -Path (Join-Path $appDir 'electron') | Out-Null
Copy-Item (Join-Path $ui 'electron/main.js') (Join-Path $appDir 'electron/main.js')
Copy-Item (Join-Path $ui 'electron/resolveTargetUrl.js') (Join-Path $appDir 'electron/resolveTargetUrl.js')
Copy-Item (Join-Path $ui 'electron/backendProcess.js') (Join-Path $appDir 'electron/backendProcess.js')
Copy-Item (Join-Path $ui 'electron/desktopPreload.cjs') (Join-Path $appDir 'electron/desktopPreload.cjs')
Copy-Item (Join-Path $ui 'dist') (Join-Path $appDir 'dist') -Recurse
@'
{"name":"openflight-face-impact-portable","version":"0.0.0-gate10","private":true,"type":"module","main":"electron/main.js"}
'@ | Set-Content -Path (Join-Path $appDir 'package.json') -Encoding utf8
@'
Gate 10 development-only Windows portable bundle.
Double-click OpenFlight Face Impact.exe.
The UI runs locally. An optional separately-built backend may be staged via
OPENFLIGHT_BACKEND_BUILD_EXE; no Python backend is included by default.
Keep any backend _internal folder beside its EXE.
This bundle does NOT validate real ELP camera
capture, measurement validation, or an installer. Keep all files in this folder.
Do not distribute as a validated release.
'@ | Set-Content -Path (Join-Path $output 'README.txt') -Encoding utf8
if (!(Test-Path (Join-Path $appDir 'dist/index.html'))) { throw 'Bundled UI missing' }
if (!(Test-Path (Join-Path $appDir 'electron/backendProcess.js'))) { throw 'Bundled backend process module missing' }
Write-Host "Portable EXE staged: $output"
