"""Gate 22 trend evidence does not claim physical contact."""

import pytest

from openflight.camera.offline_proximity_trend import classify_synthetic_proximity_trend
from openflight.camera.offline_synthetic_proximity import (
    SyntheticProximityEvidence, SyntheticProximitySample,
)


def evidence(distances, closest):
    return SyntheticProximityEvidence(
        tuple(SyntheticProximitySample(i, i * 100, i * 1000, distance)
              for i, distance in enumerate(distances)),
        closest, "synthetic observation",
    )


def test_interior_strict_minimum_is_descriptive_only():
    trend = classify_synthetic_proximity_trend(evidence([15., 8., 2., 9., 16.], 2))
    assert trend.closest_frame_index == 2
    assert trend.has_observed_approach_and_separation is True
    assert trend.physical_contact_confirmed is False


def test_monotonic_approach_cannot_establish_an_event():
    trend = classify_synthetic_proximity_trend(evidence([15., 8., 2.], 2))
    assert trend.closest_frame_index is None
    assert "boundary" in trend.reason


def test_equal_or_noisy_distances_do_not_pass():
    assert not classify_synthetic_proximity_trend(
        evidence([15., 8., 8.2, 10.], 1),
    ).has_observed_approach_and_separation
    assert not classify_synthetic_proximity_trend(
        evidence([15., 8., 8.], None),
    ).has_observed_approach_and_separation


@pytest.mark.parametrize("minimum", [0, -1, float("nan"), float("inf"), True])
def test_invalid_noise_tolerance_rejected(minimum):
    with pytest.raises(ValueError, match="pixel change"):
        classify_synthetic_proximity_trend(evidence([10., 2., 10.], 1),
                                          minimum_change_px=minimum)
