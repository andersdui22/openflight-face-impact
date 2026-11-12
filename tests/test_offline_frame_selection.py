"""Offline frame selection must reject ambiguity and never invent contact."""

from dataclasses import replace

import pytest

from openflight.camera.capture_ball_synthetic_quality import AssessedSyntheticCaptureImpact
from openflight.camera.offline_frame_selection import (
    OfflineFrameSelection, OfflineSelectionStatus, select_unique_synthetic_frame,
)
from openflight.camera.synthetic_frame_candidates import AssessedFrameCandidate
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactResult, SyntheticImpactStatus
from openflight.camera.synthetic_impact_quality import assess_synthetic_impact_quality


def frame(index, status=SyntheticImpactStatus.INVALID_GEOMETRY):
    if status is SyntheticImpactStatus.OK:
        impact = SyntheticImpactResult(
            status, x_mm=12.0, y_mm=5.0,
            horizontal_region="toe", vertical_region="high",
        )
    else:
        impact = SyntheticImpactResult(status, rejection_reason="not observable")
    return AssessedFrameCandidate(
        index, AssessedSyntheticCaptureImpact(impact, assess_synthetic_impact_quality(impact)),
    )


def test_single_synthetic_acceptance_has_explicit_nonphysical_provenance():
    result = select_unique_synthetic_frame((frame(1), frame(3, SyntheticImpactStatus.OK)))
    assert result.status is OfflineSelectionStatus.UNIQUE_SYNTHETIC
    assert result.frame_index == 3
    assert result.accepted_frame_indices == (3,)
    assert result.physical_contact_confirmed is False
    assert "physical contact unverified" in result.reason


def test_no_accepted_frame_has_no_selected_index():
    result = select_unique_synthetic_frame((frame(2), frame(4)))
    assert result.status is OfflineSelectionStatus.NO_ACCEPTED_FRAME
    assert result.frame_index is None
    assert result.accepted_frame_indices == ()


def test_multiple_accepted_frames_fail_closed_independent_of_order():
    items = (frame(9, SyntheticImpactStatus.OK), frame(1, SyntheticImpactStatus.OK))
    for ordered in (items, items[::-1]):
        result = select_unique_synthetic_frame(ordered)
        assert result.status is OfflineSelectionStatus.AMBIGUOUS
        assert result.frame_index is None
        assert result.accepted_frame_indices == (1, 9)


@pytest.mark.parametrize("items", [(), [], None])
def test_invalid_batch_rejected(items):
    with pytest.raises(ValueError, match="bounded"):
        select_unique_synthetic_frame(items)


@pytest.mark.parametrize("limit", [0, -1, True, 1.2])
def test_invalid_limit_rejected(limit):
    with pytest.raises(ValueError, match="max_frames"):
        select_unique_synthetic_frame((frame(1),), max_frames=limit)


def test_duplicate_and_invalid_identity_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        select_unique_synthetic_frame((frame(1), frame(1)))
    with pytest.raises(ValueError, match="identity"):
        select_unique_synthetic_frame((replace(frame(1), frame_index=True),))


def test_inconsistent_quality_fails_before_selection():
    accepted = frame(2, SyntheticImpactStatus.OK)
    bad_quality = replace(accepted.assessment.quality, accepted_synthetic_geometry=False)
    corrupted = replace(accepted, assessment=replace(accepted.assessment, quality=bad_quality))
    with pytest.raises(ValueError, match="inconsistent"):
        select_unique_synthetic_frame((corrupted,))


def test_physical_contact_claim_is_forbidden():
    with pytest.raises(ValueError, match="physical contact"):
        OfflineFrameSelection(
            OfflineSelectionStatus.UNIQUE_SYNTHETIC, 2, (2,),
            "synthetic only", physical_contact_confirmed=True,
        )


def test_bounded_count():
    with pytest.raises(ValueError, match="bounded"):
        select_unique_synthetic_frame((frame(1), frame(2)), max_frames=1)
