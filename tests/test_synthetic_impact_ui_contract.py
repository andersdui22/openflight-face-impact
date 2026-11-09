"""Gate 20: verify UI JSON fixtures against the actual Python geometry pipeline."""

import json
from pathlib import Path

import numpy as np

from openflight.camera.synthetic_face_frame import SyntheticFaceFrame
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_impact_pipeline import calculate_synthetic_face_impact
from openflight.camera.synthetic_mesh_pose import SyntheticPoseCandidate


def test_ui_fixture_contract_matches_python_pipeline():
    path = Path(__file__).resolve().parents[1] / "ui/src/data/syntheticFaceImpactCases.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["source"] == "synthetic_python_pipeline_fixture"
    polygon = SyntheticFacePolygon(np.asarray(payload["polygon_face_mm"], dtype=float))
    frame = SyntheticFaceFrame(
        np.zeros(3), np.array([1., 0., 0.]),
        np.array([0., 1., 0.]), np.array([0., 0., 1.])
    )
    pose = SyntheticPoseCandidate(np.eye(3), np.zeros(3))
    assert len(payload["cases"]) >= 4
    for case in payload["cases"]:
        actual = calculate_synthetic_face_impact(
            np.asarray(case["ball_center_world_mm"], dtype=float),
            case["ball_radius_mm"], frame, pose, polygon
        )
        expected = case["result"]
        assert actual.status.value == expected["status"], case["id"]
        if actual.status.value == "ok":
            assert actual.x_mm == expected["x_mm"]
            assert actual.y_mm == expected["y_mm"]
            assert actual.horizontal_region == expected["horizontal_region"]
            assert actual.vertical_region == expected["vertical_region"]
            assert actual.rejection_reason is None
        else:
            assert actual.x_mm is None and actual.y_mm is None
            assert actual.rejection_reason == expected["rejection_reason"]
            assert "x_mm" not in expected and "y_mm" not in expected
