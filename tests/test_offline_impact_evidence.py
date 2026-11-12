"""Offline synthetic impact export preserves provenance and fails closed."""

from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.capture_ball_synthetic_quality import AssessedSyntheticCaptureImpact
from openflight.camera.offline_impact_evidence import (
    OfflineImpactEvidence, export_offline_impact_evidence,
)
from openflight.camera.offline_temporal_evidence import assess_offline_temporal_evidence
from openflight.camera.synthetic_frame_candidates import AssessedFrameCandidate
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactResult, SyntheticImpactStatus
from openflight.camera.synthetic_impact_quality import assess_synthetic_impact_quality
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture():
    image = np.zeros((12, 12), dtype=np.uint8)
    return TriggeredCapture(
        (CameraFrame(image.copy(), 100, 1000, 100, 1.),
         CameraFrame(image.copy(), 200, 2000, 100, 1.)),
        1, 1500, shot_id="shot", session_id="session",
    )


def candidate(index, ok=True):
    if ok:
        result = SyntheticImpactResult(
            SyntheticImpactStatus.OK, x_mm=12., y_mm=5.,
            horizontal_region="toe", vertical_region="high",
        )
    else:
        result = SyntheticImpactResult(
            SyntheticImpactStatus.NO_TANGENCY, rejection_reason="no tangency",
        )
    return AssessedFrameCandidate(
        index, AssessedSyntheticCaptureImpact(
            result, assess_synthetic_impact_quality(result),
        ),
    )


def temporal(cap, frames, max_sensor_gap_ns=100):
    return assess_offline_temporal_evidence(
        cap, frames, max_sensor_gap_ns=max_sensor_gap_ns,
        max_host_gap_ns=1000,
    )


def test_unique_accepted_candidate_exports_synthetic_only_coordinates():
    cap = capture()
    frames = (candidate(0, False), candidate(1))
    result = export_offline_impact_evidence(cap, frames, temporal(cap, frames))
    assert result.shot_id == "shot" and result.session_id == "session"
    assert result.frame_index == 1
    assert (result.x_mm, result.y_mm) == (12., 5.)
    assert result.physically_validated is False
    assert result.position_uncertainty_mm is None


def test_ambiguous_candidates_hide_coordinates():
    cap = capture()
    frames = (candidate(0), candidate(1))
    result = export_offline_impact_evidence(cap, frames, temporal(cap, frames))
    assert result.accepted_for_offline_analysis is False
    assert result.frame_index is None
    assert result.x_mm is None and result.y_mm is None


def test_bad_timing_hides_coordinates_even_with_unique_geometry():
    cap = capture()
    frames = (candidate(1),)
    result = export_offline_impact_evidence(
        cap, frames, temporal(cap, frames, max_sensor_gap_ns=99),
    )
    assert result.accepted_for_offline_analysis is False
    assert result.x_mm is None
    assert "sensor clock gap" in result.reason


def test_mismatched_temporal_selection_rejected():
    cap = capture()
    frames = (candidate(0),)
    other = (candidate(1),)
    with pytest.raises(ValueError, match="does not match"):
        export_offline_impact_evidence(cap, frames, temporal(cap, other))


def test_physical_claim_and_rejected_coordinates_forbidden():
    cap = capture()
    frames = (candidate(1),)
    result = export_offline_impact_evidence(cap, frames, temporal(cap, frames))
    with pytest.raises(ValueError, match="physical accuracy"):
        replace(result, physically_validated=True)
    with pytest.raises(ValueError, match="cannot expose"):
        replace(result, accepted_for_offline_analysis=False)


def test_export_requires_typed_temporal_evidence():
    with pytest.raises(ValueError, match="temporal evidence"):
        export_offline_impact_evidence(capture(), (candidate(1),), None)


def test_empty_candidate_batch_rejected():
    with pytest.raises(ValueError, match="nonempty"):
        export_offline_impact_evidence(capture(), (), None if False else temporal(
            capture(), (candidate(1),),
        ))
