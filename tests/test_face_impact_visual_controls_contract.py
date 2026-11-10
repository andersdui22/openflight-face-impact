"""Gate 07: all planned UI-only controls are discoverable and honest."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLS = ROOT / "ui" / "src" / "components" / "FaceImpactControls.tsx"
APP = ROOT / "ui" / "src" / "App.tsx"


def test_visual_controls_are_integrated():
    app = APP.read_text(encoding="utf-8")
    assert "import { FaceImpactControls }" in app
    assert "<FaceImpactControls />" in app


def test_planned_ui_sections_are_present():
    source = CONTROLS.read_text(encoding="utf-8")
    for section in ("Camera setup", "Calibration", "Capture", "Replay"):
        assert section in source
    for label in (
        "Camera model",
        "Handedness",
        "Camera position",
        "CONNECT CAMERA",
        "START CALIBRATION",
        "START CAPTURE",
        "STOP CAPTURE",
        "FRAME STEP",
        "EXPORT",
    ):
        assert label in source


def test_unimplemented_physical_operations_are_disabled():
    source = CONTROLS.read_text(encoding="utf-8")
    assert source.count("disabled title=") >= 8
    assert "No camera measurements are active." in source
    assert "Settings are local to this view and are not saved." in source
