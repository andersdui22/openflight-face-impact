"""Gate 22 software-only orchestration of dual-object motion evidence.

This pipeline reports a descriptive pixel-space trend, not a contact time.
"""

from __future__ import annotations

from dataclasses import dataclass

from .offline_dual_object_sequence import OfflineDualObjectSequence
from .offline_proximity_trend import (
    SyntheticProximityTrend, classify_synthetic_proximity_trend,
)
from .offline_synthetic_proximity import (
    SyntheticProximityEvidence, assess_synthetic_proximity,
)
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineDualObjectMotion:
    """Linked image-space distance evidence and conservative temporal trend."""

    proximity: SyntheticProximityEvidence
    trend: SyntheticProximityTrend
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("synthetic motion cannot confirm physical contact")


def assess_offline_dual_object_motion(
    capture: TriggeredCapture,
    sequence: OfflineDualObjectSequence,
    *,
    max_sensor_gap_ns: int,
    max_host_gap_ns: int,
    minimum_change_px: float = 0.5,
) -> OfflineDualObjectMotion:
    """Compose provenance, timing, proximity and approach/separation checks.

    The returned closest frame, when present, is an image-space observation
    and must not be treated as a physically measured impact frame.
    """
    proximity = assess_synthetic_proximity(
        capture, sequence, max_sensor_gap_ns=max_sensor_gap_ns,
        max_host_gap_ns=max_host_gap_ns,
    )
    trend = classify_synthetic_proximity_trend(
        proximity, minimum_change_px=minimum_change_px,
    )
    return OfflineDualObjectMotion(proximity, trend)
