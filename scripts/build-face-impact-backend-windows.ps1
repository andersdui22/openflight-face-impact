# Development-only Windows Python backend build. Not a validated release.
# Run from repository root on Windows with Python 3.12 and pip available.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venv = Join-Path $root '.venv-face-impact-backend-build'
$python = Join-Path $venv 'Scripts/python.exe'
$dist = Join-Path $root 'out/face-impact-backend'
$work = Join-Path $root 'out/face-impact-backend-build'
if (!(Test-Path $python)) {
  py -3.12 -m venv $venv
  if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 virtual environment creation failed' }
}
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip bootstrap failed' }
# The inherited OpenFlight project includes optional and legacy hardware drivers.
# Install from source with explicit dependencies for this mock-only backend.
& $python -m pip install pyinstaller flask flask-cors flask-socketio numpy scipy pyserial
if ($LASTEXITCODE -ne 0) { throw 'Python backend dependency installation failed' }
$env:PYTHONPATH = Join-Path $root 'src'
& $python -m PyInstaller --noconfirm --clean --onefile --name OpenFlightFaceImpactBackend --paths (Join-Path $root 'src') --distpath $dist --workpath $work --specpath $work (Join-Path $root 'scripts/face-impact-backend-entry.py')
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller backend build failed' }
$exe = Join-Path $dist 'OpenFlightFaceImpactBackend.exe'
if (!(Test-Path $exe -PathType Leaf)) { throw 'Missing backend EXE' }
Write-Host "Backend EXE staged: $exe"
Write-Host 'This build has NOT passed a runtime smoke or ELP camera validation.'
Write-Host 'To include it in the portable UI build, set OPENFLIGHT_BACKEND_BUILD_EXE to this absolute path.'
