"""Gate 19: read-only revision status for the existing USB status API.

A stored binding provides independent revision evidence, but this helper
does not establish camera mode or validate a live club model.
"""

from __future__ import annotations

from pathlib import Path

from .calibration_club_binding_store import load_calibration_club_binding
from .calibration_revision_status import revision_bound_calibration_status
from .calibration_store import load_calibration_status, load_calibration_profile


def load_revision_bound_calibration_status(
    profile_path: str | Path | None,
    binding_path: str | Path | None,
) -> dict:
    """Return fail-closed optics revision state without physical camera access."""
    if profile_path is None or binding_path is None:
        result = load_calibration_status(profile_path)
        result["binding_loaded"] = False
        result["revision_compatible"] = False
        result["club_geometry_compatible"] = False
        if profile_path is None and binding_path is not None:
            result["state"] = "profile_invalid"
        return result
    try:
        profile = load_calibration_profile(profile_path)
    except (OSError, ValueError, TypeError, KeyError):
        result = load_calibration_status(profile_path)
        result["binding_loaded"] = False
        result["revision_compatible"] = False
        result["club_geometry_compatible"] = False
        return result
    try:
        binding = load_calibration_club_binding(binding_path)
    except (OSError, ValueError, TypeError, KeyError):
        result = revision_bound_calibration_status(
            profile, expected_revision=None, camera_mode_id=None, image_size=None
        )
        result["binding_loaded"] = False
        result["club_geometry_compatible"] = False
        return result
    result = revision_bound_calibration_status(
        profile, expected_revision=binding.calibration_revision,
        camera_mode_id=None, image_size=None
    )
    result["binding_loaded"] = True
    result["club_geometry_compatible"] = False
    return result
