"""Gate 22: conservative classification of image-space proximity trends.

A unique smallest pixel separation is not necessarily an impact event:
the closest sample may occur at a sequence boundary or be part of an
unresolved approach. No physical contact time is inferred here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .offline_synthetic_proximity import SyntheticProximityEvidence


@dataclass(frozen=True)
class SyntheticProximityTrend:
    """Bounded temporal pattern with explicit non-physical interpretation."""

    closest_frame_index: int | None
    has_observed_approach_and_separation: bool
    reason: str
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("pixel trend cannot confirm physical contact")


def classify_synthetic_proximity_trend(
    evidence: SyntheticProximityEvidence,
    *,
    minimum_change_px: float = 0.5,
) -> SyntheticProximityTrend:
    """Require an interior strict minimum and observations on both sides.

    A trend is a descriptive image-space observation, not a claim of
    physical impact or a measurement of impact-time accuracy.
    """
    if not isinstance(evidence, SyntheticProximityEvidence):
        raise ValueError("typed proximity evidence required")
    if (not isinstance(minimum_change_px, (int, float))
            or isinstance(minimum_change_px, bool)
            or not math.isfinite(minimum_change_px)
            or minimum_change_px <= 0):
        raise ValueError("minimum pixel change must be finite and positive")
    samples = evidence.samples
    if evidence.closest_frame_index is None or len(samples) < 3:
        return SyntheticProximityTrend(None, False, "no unambiguous interior minimum")
    indices = [sample.frame_index for sample in samples]
    if len(indices) != len(set(indices)):
        raise ValueError("duplicate proximity sample frame indices")
    positions = [i for i, sample in enumerate(samples)
                 if sample.frame_index == evidence.closest_frame_index]
    if len(positions) != 1:
        raise ValueError("closest frame is missing or duplicated")
    position = positions[0]
    if position == 0 or position == len(samples) - 1:
        return SyntheticProximityTrend(
            None, False, "closest observed frame lies at sequence boundary",
        )
    distances = [sample.separation_px for sample in samples]
    if any(not math.isfinite(distance) or distance < 0 for distance in distances):
        raise ValueError("invalid proximity separation")
    # Require strictly decreasing distances up to the closest frame and
    # strictly increasing distances afterwards, beyond a noise tolerance.
    approach = all(
        distances[i] - distances[i + 1] >= minimum_change_px
        for i in range(position)
    )
    separation = all(
        distances[i + 1] - distances[i] >= minimum_change_px
        for i in range(position, len(distances) - 1)
    )
    if not approach or not separation:
        return SyntheticProximityTrend(
            None, False, "no clear approach-and-separation pixel trend",
        )
    return SyntheticProximityTrend(
        evidence.closest_frame_index, True,
        "observed image-space approach and separation; contact unverified",
    )
