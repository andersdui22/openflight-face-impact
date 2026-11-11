"""Fail-closed UI serialization of synthetic image-space motion."""

from dataclasses import replace
import json

import pytest

from openflight.camera.offline_dual_object_motion import OfflineDualObjectMotion
from openflight.camera.offline_dual_object_sequence import OfflineDualObjectSequence
from openflight.camera.offline_motion_ui_payload import export_synthetic_motion_ui_payload
from openflight.camera.offline_proximity_trend import SyntheticProximityTrend
from openflight.camera.offline_synthetic_proximity import (
    SyntheticProximityEvidence, SyntheticProximitySample,
)


def fixture():
    sequence = OfflineDualObjectSequence((), ((2, "occluded"),), "fingerprint")
    proximity = SyntheticProximityEvidence(
        (SyntheticProximitySample(1, 100, 1000, 4.0),), None,
        "incomplete image sequence",
    )
    motion = OfflineDualObjectMotion(
        proximity, SyntheticProximityTrend(None, False, "no trend"),
    )
    return sequence, motion


def test_payload_is_json_compatible_and_never_exposes_impact():
    sequence, motion = fixture()
    motion = replace(motion, proximity=replace(motion.proximity, samples=()))
    payload = export_synthetic_motion_ui_payload(sequence, motion)
    assert json.loads(json.dumps(payload)) == payload
    assert payload["impact_frame_index"] is None
    assert payload["impact_x_mm"] is None
    assert payload["impact_y_mm"] is None
    assert payload["physical_contact_confirmed"] is False
    assert payload["rejected_frames"] == [{"frame_index": 2, "reason": "occluded"}]


def test_mismatched_motion_sample_is_rejected():
    sequence, motion = fixture()
    with pytest.raises(ValueError, match="do not match"):
        export_synthetic_motion_ui_payload(sequence, motion)


def test_missing_trend_sample_is_rejected():
    sequence, motion = fixture()
    motion = replace(
        motion,
        proximity=replace(motion.proximity, samples=()),
        trend=SyntheticProximityTrend(1, True, "synthetic"),
    )
    with pytest.raises(ValueError, match="missing frame"):
        export_synthetic_motion_ui_payload(sequence, motion)
