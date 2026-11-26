# Development-only Windows Python backend build. Not a validated release.
# Run from repository root on Windows with Python 3.12 and pip available.
param([switch] $UsbFixture)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venv = Join-Path $root '.venv-face-impact-backend-build'
$python = Join-Path $venv 'Scripts/python.exe'
$dist = if ($UsbFixture) { Join-Path $root 'out/face-impact-usb-fixture' } else { Join-Path $root 'out/face-impact-backend' }
$entry = if ($UsbFixture) { 'tests/face_impact_usb_fixture_server.py' } else { 'scripts/face-impact-backend-entry.py' }
$work = Join-Path $root 'out/face-impact-backend-build'
if (!(Test-Path $python)) {
  py -3.12 -m venv $venv
  if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 virtual environment creation failed' }
}
& $python -m pip install pip==26.3
if ($LASTEXITCODE -ne 0) { throw 'pip bootstrap failed' }
# The inherited OpenFlight project includes optional and legacy hardware drivers.
# Install from source with explicit dependencies for this mock-only backend.
& $python -m pip install --only-binary=:all: -r (Join-Path $root 'scripts/face-impact-windows-backend-requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Python backend dependency installation failed' }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Pinned backend dependency check failed' }
$env:PYTHONPATH = Join-Path $root 'src'
New-Item -ItemType Directory -Force -Path $work | Out-Null
$sourceSha = git -C $root rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot identify backend source revision' }
$sourceFile = Join-Path $venv 'face-impact-source-sha.txt'
Set-Content -LiteralPath $sourceFile -Value $sourceSha -Encoding ascii
$nativeBuild = Join-Path $work 'media-foundation'
& cmake -S (Join-Path $root 'native/windows') -B $nativeBuild -A x64
if ($LASTEXITCODE -ne 0) { throw 'Media Foundation bridge configuration failed' }
& cmake --build $nativeBuild --config Release
if ($LASTEXITCODE -ne 0) { throw 'Media Foundation bridge build failed' }
$nativeDll = Join-Path $nativeBuild 'Release/face_impact_mf.dll'
if (!(Test-Path -LiteralPath $nativeDll -PathType Leaf)) { throw 'Missing Media Foundation bridge' }
# A one-directory backend runs directly as the process owned by Electron.
& $python -m PyInstaller --noconfirm --clean --onedir --name OpenFlightFaceImpactBackend --paths (Join-Path $root 'src') --add-binary "$nativeDll;." --add-data "$sourceFile;." --hidden-import engineio.async_drivers.threading --distpath $dist --workpath $work --specpath $work (Join-Path $root $entry)
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller backend build failed' }
$exe = Join-Path $dist 'OpenFlightFaceImpactBackend/OpenFlightFaceImpactBackend.exe'
if (!(Test-Path $exe -PathType Leaf)) { throw 'Missing backend EXE' }
if (!(Test-Path (Join-Path (Split-Path -Parent $exe) '_internal') -PathType Container)) {
  throw 'Missing frozen backend dependencies'
}
Write-Host "Backend EXE staged: $exe"
Write-Host 'This build has NOT passed a runtime smoke or ELP camera validation.'
Write-Host 'To include it in the portable UI build, set OPENFLIGHT_BACKEND_BUILD_EXE to this absolute path.'
