"""Gate 18: provenance-aware clubface geometry, without assumed dimensions.

Models are metadata, not measured physical shapes. Curvature is not inferred
from a club category; actual dimensions require an admitted evidence source.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class ClubFamily(str, Enum):
    DRIVER = "driver"
    WOOD = "wood"
    IRON = "iron"
    WEDGE = "wedge"


class FaceSurface(str, Enum):
    UNKNOWN = "unknown"
    PLANAR = "planar"
    CURVED = "curved"


@dataclass(frozen=True)
class ClubFaceModel:
    """Club identity and optional independently sourced face geometry in mm."""

    family: ClubFamily
    model_id: str
    surface: FaceSurface = FaceSurface.UNKNOWN
    width_mm: float | None = None
    height_mm: float | None = None
    bulge_radius_mm: float | None = None
    roll_radius_mm: float | None = None
    evidence_source: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.family, ClubFamily):
            raise ValueError("a supported club family is required")
        if not isinstance(self.surface, FaceSurface):
            raise ValueError("a supported face surface type is required")
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("a nonempty model identity is required")
        dimensions = (
            self.width_mm, self.height_mm,
            self.bulge_radius_mm, self.roll_radius_mm,
        )
        if any(
            value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            )
            for value in dimensions
        ):
            raise ValueError("known clubface dimensions must be finite positive millimeters")
        if self.surface is not FaceSurface.CURVED and any(
            value is not None for value in
            (self.bulge_radius_mm, self.roll_radius_mm)
        ):
            raise ValueError("bulge and roll require an explicitly curved face")
        if self.surface is FaceSurface.PLANAR and (
            self.bulge_radius_mm is not None or self.roll_radius_mm is not None
        ):
            raise ValueError("planar faces cannot have bulge or roll radii")
        if any(value is not None for value in dimensions):
            if not isinstance(self.evidence_source, str) or not self.evidence_source.strip():
                raise ValueError("measured dimensions require explicit evidence provenance")
        elif self.evidence_source is not None and (
            not isinstance(self.evidence_source, str) or not self.evidence_source.strip()
        ):
            raise ValueError("evidence provenance must be a nonempty string")

    @property
    def geometry_known(self) -> bool:
        """True only when dimensions and surface classification are supplied."""
        return (
            self.surface is not FaceSurface.UNKNOWN
            and self.width_mm is not None
            and self.height_mm is not None
            and self.evidence_source is not None
        )
