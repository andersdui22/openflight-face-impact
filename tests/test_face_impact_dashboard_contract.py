"""Gate 06: protect the approved six-panel Face Impact dashboard layout."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ui" / "src" / "App.tsx"
DEMO = ROOT / "ui" / "src" / "components" / "SyntheticFaceImpactDemo.tsx"


def test_all_six_dashboard_panels_are_retained():
    source = APP.read_text(encoding="utf-8")
    titles = (
        "Side Impact",
        "Front Impact",
        "Top Impact",
        "Impact Distribution",
        "Camera Preview",
        "Shot Replay",
    )
    for title in titles:
        assert source.count(f"title: '{title}'") == 1, title


def test_face_impact_demo_is_explicitly_synthetic():
    app = APP.read_text(encoding="utf-8")
    demo = DEMO.read_text(encoding="utf-8")
    assert "IMPACT DATA NOT MEASURED" in app
    assert "SyntheticFaceImpactDemo" in app
    assert "Not a camera measurement" in demo
