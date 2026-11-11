"""Gate 19: offline calibration and club binding lifecycle validation.

This function only reads persisted files. It cannot verify a physical camera,
discover a club, estimate pose, or authorize impact measurements.
"""

from __future__ import annotations

from pathlib import Path

from .calibration_club_binding import require_calibration_club_binding
from .calibration_club_binding_store import load_calibration_club_binding
from .calibration_store import load_calibration_profile
from .club_face_model import ClubFaceModel


def validate_stored_calibration_club(
    profile_path: str | Path,
    binding_path: str | Path,
    *,
    club_model: ClubFaceModel,
    camera_mode_id: str | None,
    image_size: tuple[int, int] | None,
) -> dict:
    """Fail closed on missing, stale or incompatible stored offline evidence."""
    result = {
        "state": "evidence_invalid",
        "profile_loaded": False,
        "binding_loaded": False,
        "mode_compatible": False,
        "revision_compatible": False,
        "club_geometry_compatible": False,
        "physical_validation": False,
    }
    try:
        profile = load_calibration_profile(profile_path)
        result["profile_loaded"] = True
        binding = load_calibration_club_binding(binding_path)
        result["binding_loaded"] = True
    except (OSError, ValueError, TypeError, KeyError):
        return result
    if camera_mode_id is None or image_size is None:
        result["state"] = "mode_unknown"
        return result
    try:
        profile.require_mode(camera_mode_id, image_size)
    except ValueError:
        result["state"] = "mode_incompatible"
        return result
    result["mode_compatible"] = True
    try:
        require_calibration_club_binding(
            binding, profile=profile, club_model=club_model
        )
    except ValueError:
        result["state"] = "binding_incompatible"
        return result
    result["revision_compatible"] = True
    result["club_geometry_compatible"] = True
    result["state"] = "offline_evidence_compatible"
    return result
