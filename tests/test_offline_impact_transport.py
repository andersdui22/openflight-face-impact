"""Contract tests for future Python -> React offline synthetic impact messages."""

import json

import pytest

from openflight.camera.offline_impact_evidence import OfflineImpactEvidence
from openflight.camera.offline_impact_transport import serialize_offline_impact_evidence


def test_accepted_synthetic_evidence_serializes_with_capture_identity():
    evidence = OfflineImpactEvidence(
        "shot-42", "session-7", 2, True, 12., 5., "toe", "high",
        "synthetic geometry only",
    )
    payload = json.loads(json.dumps(serialize_offline_impact_evidence(evidence)))
    assert payload == {
        "schema_version": 1, "source": "offline_synthetic_analysis",
        "shot_id": "shot-42", "session_id": "session-7",
        "accepted": True, "reason": "synthetic geometry only",
        "physically_validated": False, "position_uncertainty_mm": None,
        "frame_index": 2, "x_mm": 12., "y_mm": 5.,
        "horizontal_region": "toe", "vertical_region": "high",
    }


def test_rejected_evidence_never_exposes_coordinates():
    evidence = OfflineImpactEvidence(
        "shot-42", "session-7", None, False, None, None, None, None,
        "ambiguous synthetic frame",
    )
    payload = serialize_offline_impact_evidence(evidence)
    assert payload["accepted"] is False
    for key in ("frame_index", "x_mm", "y_mm", "horizontal_region", "vertical_region"):
        assert key not in payload


@pytest.mark.parametrize("coordinate", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_accepted_coordinates_are_rejected(coordinate):
    evidence = OfflineImpactEvidence(
        "shot-42", "session-7", 2, True, coordinate, 5., "toe", "high",
        "synthetic geometry only",
    )
    with pytest.raises(ValueError, match="coordinates or regions invalid"):
        serialize_offline_impact_evidence(evidence)


def test_wrong_evidence_type_is_rejected():
    with pytest.raises(ValueError, match="typed impact evidence"):
        serialize_offline_impact_evidence(None)
