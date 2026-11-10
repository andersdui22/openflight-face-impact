"""Gate 05 regression: the new app namespace must be import-side-effect free."""

from pathlib import Path
import subprocess
import sys


def test_face_impact_root_import_is_independent():
    source_root = Path(__file__).resolve().parents[1] / "src"
    code = (
        "import sys; "
        f"sys.path.insert(0, {str(source_root)!r}); "
        "import face_impact; "
        "forbidden = ('openflight', 'cv2', 'serial', 'picamera2'); "
        "loaded = [name for name in sys.modules "
        "if any(name == item or name.startswith(item + '.') for item in forbidden)]; "
        "assert not loaded, loaded"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
