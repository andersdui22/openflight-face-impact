"""Gate 24: explicit synthetic impact acceptance and uncertainty boundaries.

A successful synthetic geometry calculation is not a physically calibrated
measurement. This module does not infer or fabricate millimetre uncertainty.
"""

from __future__ import annotations

from dataclasses import dataclass

from .synthetic_impact_pipeline import SyntheticImpactResult, SyntheticImpactStatus


@dataclass(frozen=True)
class SyntheticImpactQuality:
    """Fail-closed quality summary for a synthetic-only impact result."""

    accepted_synthetic_geometry: bool
    physically_validated: bool
    position_uncertainty_mm: float | None
    reason: str


def assess_synthetic_impact_quality(result: SyntheticImpactResult) -> SyntheticImpactQuality:
    """Report geometry acceptance without claiming physical impact accuracy."""
    if not isinstance(result, SyntheticImpactResult):
        raise ValueError("quality assessment requires a synthetic impact result")
    if result.status is SyntheticImpactStatus.OK:
        return SyntheticImpactQuality(
            accepted_synthetic_geometry=True,
            physically_validated=False,
            position_uncertainty_mm=None,
            reason="synthetic geometry accepted; physical accuracy unverified",
        )
    return SyntheticImpactQuality(
        accepted_synthetic_geometry=False,
        physically_validated=False,
        position_uncertainty_mm=None,
        reason=result.rejection_reason,
    )
