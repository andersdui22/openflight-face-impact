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


@dataclass(frozen=True)
class CalibrationClubBinding:
    calibration_revision: str
    club_model_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.calibration_revision, str) or not self.calibration_revision:
            raise ValueError("explicit calibration revision required")
        if not isinstance(self.club_model_id, str) or not self.club_model_id.strip():
            raise ValueError("explicit club model identity required")


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
