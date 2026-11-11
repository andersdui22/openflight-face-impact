"""Gate 19: explicit offline binding of a club model to calibration evidence.

This binding records identity, not accuracy. No automatic camera, club or
pose inference occurs. A consumer must supply an independently persisted
revision and the exact expected club model identifier.
"""

from __future__ import annotations

from dataclasses import dataclass

from .calibration_profile import CameraCalibrationProfile
from .calibration_revision import require_calibration_revision
from .club_face_model import ClubFaceModel
from .club_geometry_revision import club_geometry_revision


@dataclass(frozen=True)
class CalibrationClubBinding:
    calibration_revision: str
    club_model_id: str
    club_geometry_revision: str | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.calibration_revision, str)
            or len(self.calibration_revision) != 64
            or any(char not in "0123456789abcdef" for char in self.calibration_revision)
        ):
            raise ValueError("explicit SHA-256 calibration revision required")
        if not isinstance(self.club_model_id, str) or not self.club_model_id.strip():
            raise ValueError("explicit club model identity required")
        if self.club_geometry_revision is not None and (
            not isinstance(self.club_geometry_revision, str)
            or len(self.club_geometry_revision) != 64
            or any(char not in "0123456789abcdef" for char in self.club_geometry_revision)
        ):
            raise ValueError("club geometry revision must be a SHA-256 hex digest")


def require_calibration_club_binding(
    binding: CalibrationClubBinding,
    *,
    profile: CameraCalibrationProfile,
    club_model: ClubFaceModel,
) -> None:
    """Reject stale optics or substituted/unknown club models."""
    if not isinstance(binding, CalibrationClubBinding):
        raise ValueError("explicit calibration-to-club binding required")
    require_calibration_revision(
        profile, expected_revision=binding.calibration_revision
    )
    if not isinstance(club_model, ClubFaceModel) or not club_model.geometry_known:
        raise ValueError("evidenced club geometry required")
    if binding.club_model_id != club_model.model_id:
        raise ValueError("club model identity incompatible with calibration binding")
    if binding.club_geometry_revision is None:
        raise ValueError("explicit club geometry revision required")
    if binding.club_geometry_revision != club_geometry_revision(club_model):
        raise ValueError("club geometry revision is stale or incompatible")
