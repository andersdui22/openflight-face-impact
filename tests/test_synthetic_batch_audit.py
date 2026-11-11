"""Gate 24 aggregate offline audit regression matrix."""

from dataclasses import replace

import pytest

from openflight.camera.synthetic_batch_audit import audit_synthetic_candidate_batch
from openflight.camera.synthetic_frame_candidates import AssessedFrameCandidate
from openflight.camera.capture_ball_synthetic_quality import AssessedSyntheticCaptureImpact
from openflight.camera.synthetic_impact_pipeline import (
    SyntheticImpactResult, SyntheticImpactStatus,
)
from openflight.camera.synthetic_impact_quality import (
    SyntheticImpactQuality, assess_synthetic_impact_quality,
)


def item(index, status):
    impact = (
        SyntheticImpactResult(status, 1., 2., "toe", "high")
        if status is SyntheticImpactStatus.OK
        else SyntheticImpactResult(status, rejection_reason="explicit rejection")
    )
    return AssessedFrameCandidate(
        index, AssessedSyntheticCaptureImpact(
            impact, assess_synthetic_impact_quality(impact),
        ),
    )


def test_aggregate_counts_all_four_statuses_without_physical_claim():
    statuses = tuple(SyntheticImpactStatus)
    report = audit_synthetic_candidate_batch(tuple(
        item(index, status) for index, status in enumerate(statuses)
    ))
    assert report.total == 4
    assert report.accepted_synthetic == 1
    assert report.rejected_invalid_geometry == 1
    assert report.rejected_no_tangency == 1
    assert report.rejected_outside_face == 1
    assert report.all_rejections_fail_closed is True
    assert report.physical_contact_established is False
    assert report.physical_accuracy_established is False


def test_rejects_contradictory_accepted_quality():
    accepted = item(2, SyntheticImpactStatus.OK)
    bad = replace(accepted, assessment=replace(
        accepted.assessment,
        quality=replace(accepted.assessment.quality, accepted_synthetic_geometry=False),
    ))
    with pytest.raises(ValueError, match="contradicts"):
        audit_synthetic_candidate_batch((bad,))


def test_rejects_fake_physical_accuracy():
    rejected = item(2, SyntheticImpactStatus.NO_TANGENCY)
    bad = replace(rejected, assessment=replace(
        rejected.assessment,
        quality=replace(rejected.assessment.quality, position_uncertainty_mm=0.1),
    ))
    with pytest.raises(ValueError, match="physical validation"):
        audit_synthetic_candidate_batch((bad,))


def test_rejects_quality_reason_mismatch():
    rejected = item(2, SyntheticImpactStatus.OUTSIDE_FACE)
    bad = replace(rejected, assessment=replace(
        rejected.assessment,
        quality=replace(rejected.assessment.quality, reason="different"),
    ))
    with pytest.raises(ValueError, match="preserve reason"):
        audit_synthetic_candidate_batch((bad,))


@pytest.mark.parametrize("invalid", [(), [], None])
def test_rejects_empty_or_wrong_batch(invalid):
    with pytest.raises(ValueError, match="nonempty tuple"):
        audit_synthetic_candidate_batch(invalid)


def test_rejects_duplicate_frame_indices():
    accepted = item(2, SyntheticImpactStatus.OK)
    with pytest.raises(ValueError, match="distinct"):
        audit_synthetic_candidate_batch((accepted, accepted))


def test_rejects_wrong_batch_item_type():
    with pytest.raises(ValueError, match="frame assessments"):
        audit_synthetic_candidate_batch((object(),))
