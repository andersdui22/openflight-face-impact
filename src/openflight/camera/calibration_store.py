"""Offline calibration profile persistence with strict validation.

Loading a file does not imply the physical USB capture mode is known.
No camera is opened or accessed by this module.
"""

from __future__ import annotations

from pathlib import Path

from .calibration_profile import CameraCalibrationProfile
from .calibration_status import calibration_status


def save_calibration_profile(path: str | Path, profile: CameraCalibrationProfile) -> None:
    """Write an explicitly supplied, validated offline profile."""
    if not isinstance(profile, CameraCalibrationProfile):
        raise ValueError("a validated calibration profile is required")
    destination = Path(path)
    destination.write_text(profile.to_json() + "\n", encoding="utf-8")


def load_calibration_profile(path: str | Path) -> CameraCalibrationProfile:
    """Load a versioned profile; propagate malformed-file errors."""
    return CameraCalibrationProfile.from_json(Path(path).read_text(encoding="utf-8"))


def load_calibration_status(
    path: str | Path | None,
    *,
    camera_mode_id: str | None = None,
    image_size: tuple[int, int] | None = None,
) -> dict:
    """Fail closed for absent, unreadable, or incompatible profile evidence.

    Physical camera mode identity must be verified independently by the caller.
    """
    if path is None:
        return calibration_status(None, camera_mode_id=camera_mode_id, image_size=image_size)
    try:
        profile = load_calibration_profile(path)
    except (OSError, ValueError, TypeError, KeyError):
        status = calibration_status(None, camera_mode_id=camera_mode_id, image_size=image_size)
        status["state"] = "profile_invalid"
        return status
    return calibration_status(profile, camera_mode_id=camera_mode_id, image_size=image_size)
