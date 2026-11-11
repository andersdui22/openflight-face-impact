"""Gate 24 synthetic quality never fabricates physical measurement confidence."""

import pytest

from openflight.camera.synthetic_impact_pipeline import (
    SyntheticImpactResult, SyntheticImpactStatus,
)
from openflight.camera.synthetic_impact_quality import assess_synthetic_impact_quality


def test_accepted_geometry_does_not_claim_physical_validation():
    result = SyntheticImpactResult(
        SyntheticImpactStatus.OK, 12., -4., "toe", "low",
    )
    quality = assess_synthetic_impact_quality(result)
    assert quality.accepted_synthetic_geometry is True
    assert quality.physically_validated is False
    assert quality.position_uncertainty_mm is None
    assert "unverified" in quality.reason


@pytest.mark.parametrize("status", [
    SyntheticImpactStatus.INVALID_GEOMETRY,
    SyntheticImpactStatus.OUTSIDE_FACE,
    SyntheticImpactStatus.NO_TANGENCY,
])
def test_rejection_carries_reason_without_accuracy_claim(status):
    quality = assess_synthetic_impact_quality(
        SyntheticImpactResult(status, rejection_reason="synthetic rejection"),
    )
    assert quality.accepted_synthetic_geometry is False
    assert quality.physically_validated is False
    assert quality.position_uncertainty_mm is None
    assert quality.reason == "synthetic rejection"


def test_invalid_quality_input_rejected():
    with pytest.raises(ValueError, match="synthetic impact result"):
        assess_synthetic_impact_quality(None)
