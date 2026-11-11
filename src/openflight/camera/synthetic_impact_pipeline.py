"""One entry point for the synthetic Face Impact geometry pipeline.

Inputs are known synthetic geometry, not observations from a camera.
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .synthetic_face_frame import SyntheticFaceFrame
from .synthetic_face_polygon import (
    SyntheticFacePolygon,
    synthetic_polygon_face_contact,
)
from .synthetic_mesh_pose import SyntheticPoseCandidate


class SyntheticImpactStatus(str, Enum):
    """Explicit success or rejection categories for synthetic calculations."""

    OK = "ok"
    OUTSIDE_FACE = "outside_face"
    NO_TANGENCY = "no_tangency"
    INVALID_GEOMETRY = "invalid_geometry"


@dataclass(frozen=True)
class SyntheticImpactResult:
    """A valid impact or an explicit rejection, never both."""

    status: SyntheticImpactStatus
    x_mm: float | None = None
    y_mm: float | None = None
    horizontal_region: str | None = None
    vertical_region: str | None = None
    rejection_reason: str | None = None

    def __post_init__(self) -> None:
        """Reject contradictory accepted/rejected synthetic impact records."""
        if not isinstance(self.status, SyntheticImpactStatus):
            raise ValueError("invalid synthetic impact status")
        coordinates = (self.x_mm, self.y_mm)
        regions = (self.horizontal_region, self.vertical_region)
        if self.status is SyntheticImpactStatus.OK:
            if (
                any(not isinstance(value, (int, float, np.integer, np.floating))
                    or isinstance(value, (bool, np.bool_))
                    or not np.isfinite(value) for value in coordinates)
                or any(not isinstance(value, str) or not value for value in regions)
                or self.rejection_reason is not None
            ):
                raise ValueError("accepted synthetic impact requires finite coordinates and regions")
        elif (
            any(value is not None for value in (*coordinates, *regions))
            or not isinstance(self.rejection_reason, str)
            or not self.rejection_reason.strip()
        ):
            raise ValueError("rejected synthetic impact cannot expose coordinates")


def calculate_synthetic_face_impact(
    ball_center_world_mm: np.ndarray,
    ball_radius_mm: float,
    frame: SyntheticFaceFrame,
    pose: SyntheticPoseCandidate,
    polygon: SyntheticFacePolygon,
    *,
    tolerance_mm: float = 1e-6,
) -> SyntheticImpactResult:
    """Compose existing sphere tangency and polygon footprint checks.

    Rejections are classified from the existing validated geometry functions.
    No guessed or partial impact coordinates are returned on rejection.
    """
    try:
        contact = synthetic_polygon_face_contact(
            ball_center_world_mm, ball_radius_mm, frame, pose,
            polygon, tolerance_mm=tolerance_mm,
        )
    except (ValueError, TypeError, OverflowError) as exc:
        message = str(exc)
        if "outside polygonal face" in message:
            status = SyntheticImpactStatus.OUTSIDE_FACE
        elif "no unique synthetic sphere-plane tangency" in message:
            status = SyntheticImpactStatus.NO_TANGENCY
        else:
            status = SyntheticImpactStatus.INVALID_GEOMETRY
        return SyntheticImpactResult(
            status=status, rejection_reason=message
        )
    return SyntheticImpactResult(
        status=SyntheticImpactStatus.OK,
        x_mm=contact.heel_to_toe_mm,
        y_mm=contact.bottom_to_top_mm,
        horizontal_region=contact.horizontal_region,
        vertical_region=contact.vertical_region,
    )
