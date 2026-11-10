"""Gate 05 regression: the new app namespace must be import-side-effect free."""

import subprocess
import sys


def test_face_impact_root_import_is_independent():
    code = (
        "import sys; import face_impact; "
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
