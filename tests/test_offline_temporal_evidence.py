"""Gate 22/24 synthetic timing and candidate selection composition."""

from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.capture_ball_synthetic_quality import AssessedSyntheticCaptureImpact
from openflight.camera.offline_temporal_evidence import (
    OfflineTemporalEvidence, assess_offline_temporal_evidence,
)
from openflight.camera.offline_frame_selection import OfflineSelectionStatus
from openflight.camera.synthetic_frame_candidates import AssessedFrameCandidate
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactResult, SyntheticImpactStatus
from openflight.camera.synthetic_impact_quality import assess_synthetic_impact_quality
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture():
    image = np.zeros((12, 12), dtype=np.uint8)
    return TriggeredCapture(
        (CameraFrame(image.copy(), 100, 1000, 100, 1.),
         CameraFrame(image.copy(), 200, 2000, 100, 1.),
         CameraFrame(image.copy(), 300, 3000, 100, 1.)),
        1, 1500, shot_id="shot", session_id="session",
    )


def candidate(index, accepted=True):
    if accepted:
        impact = SyntheticImpactResult(
            SyntheticImpactStatus.OK, x_mm=1., y_mm=1.,
            horizontal_region="center", vertical_region="middle",
        )
    else:
        impact = SyntheticImpactResult(
            SyntheticImpactStatus.INVALID_GEOMETRY, rejection_reason="not observable",
        )
    return AssessedFrameCandidate(
        index, AssessedSyntheticCaptureImpact(
            impact, assess_synthetic_impact_quality(impact),
        ),
    )


def assess(cap, candidates):
    return assess_offline_temporal_evidence(
        cap, candidates, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )


def test_unique_synthetic_candidate_and_valid_timing_accept_offline_only():
    result = assess(capture(), (candidate(0, False), candidate(2)))
    assert result.accepted_for_offline_analysis is True
    assert result.selection.frame_index == 2
    assert result.physical_contact_confirmed is False


def test_timing_failure_blocks_unique_geometry():
    result = assess(capture(), (candidate(1),))
    assert result.accepted_for_offline_analysis is True
    bad = assess_offline_temporal_evidence(
        capture(), (candidate(1),),
        max_sensor_gap_ns=99, max_host_gap_ns=1000,
    )
    assert bad.spacing.accepted is False
    assert bad.accepted_for_offline_analysis is False
    assert bad.selection.frame_index == 1


def test_multiple_geometry_frames_remain_ambiguous():
    result = assess(capture(), (candidate(1), candidate(2)))
    assert result.selection.status is OfflineSelectionStatus.AMBIGUOUS
    assert result.accepted_for_offline_analysis is False
    assert result.selection.frame_index is None


def test_out_of_capture_frame_rejected():
    with pytest.raises(ValueError, match="exceeds capture"):
        assess(capture(), (candidate(3),))


def test_contradictory_acceptance_cannot_be_fabricated():
    result = assess(capture(), (candidate(1),))
    with pytest.raises(ValueError, match="contradicts"):
        replace(result, accepted_for_offline_analysis=False)
    with pytest.raises(ValueError, match="physical contact"):
        replace(result, physical_contact_confirmed=True)
