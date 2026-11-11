"""Gate 19: explicit, hardware-free calibration profile revision checks.

A digest identifies exact serialized offline optics evidence. It is not a
camera serial number, physical mode verification or calibration expiration.
"""

from __future__ import annotations

import hashlib
import re

from .calibration_profile import CameraCalibrationProfile


def calibration_revision(profile: CameraCalibrationProfile) -> str:
    """Return a stable SHA-256 revision for a strictly validated profile."""
    if not isinstance(profile, CameraCalibrationProfile):
        raise ValueError("a validated calibration profile is required")
    return hashlib.sha256(profile.to_json().encode("utf-8")).hexdigest()


def require_calibration_revision(
    profile: CameraCalibrationProfile,
    *,
    expected_revision: str | None,
) -> str:
    """Fail closed when the expected revision is absent or stale.

    The expected revision must come from an independently stored binding;
    never infer it from the candidate profile itself.
    """
    if not isinstance(expected_revision, str) or not re.fullmatch(
        r"[0-9a-f]{64}", expected_revision
    ):
        raise ValueError("an explicit SHA-256 calibration revision is required")
    actual = calibration_revision(profile)
    if actual != expected_revision:
        raise ValueError("calibration profile revision is stale or incompatible")
    return actual
