"""Gate 19: versioned offline calibration-to-club binding persistence.

A stored binding must be independently retained and later checked against
both the candidate optics and club geometry. This file never opens a camera.
"""

from __future__ import annotations

import json
import re
import os
import tempfile
from pathlib import Path

from .calibration_club_binding import CalibrationClubBinding

BINDING_SCHEMA_VERSION = 1


def serialize_calibration_club_binding(binding: CalibrationClubBinding) -> str:
    """Serialize only a fully specified, revision-bound model association."""
    if not isinstance(binding, CalibrationClubBinding):
        raise ValueError("validated calibration-to-club binding required")
    if not re.fullmatch(r"[0-9a-f]{64}", binding.calibration_revision):
        raise ValueError("valid calibration revision required")
    if not isinstance(binding.club_geometry_revision, str) or not re.fullmatch(
        r"[0-9a-f]{64}", binding.club_geometry_revision
    ):
        raise ValueError("valid club geometry revision required")
    return json.dumps({
        "version": BINDING_SCHEMA_VERSION,
        "calibration_revision": binding.calibration_revision,
        "club_model_id": binding.club_model_id,
        "club_geometry_revision": binding.club_geometry_revision,
    }, sort_keys=True, separators=(",", ":"), allow_nan=False)


def deserialize_calibration_club_binding(content: str) -> CalibrationClubBinding:
    """Reject unknown fields, versions and missing revision bindings."""
    data = json.loads(content)
    if not isinstance(data, dict) or set(data) != {
        "version", "calibration_revision", "club_model_id",
        "club_geometry_revision",
    } or type(data["version"]) is not int or data["version"] != BINDING_SCHEMA_VERSION:
        raise ValueError("unsupported calibration-club binding schema")
    binding = CalibrationClubBinding(
        calibration_revision=data["calibration_revision"],
        club_model_id=data["club_model_id"],
        club_geometry_revision=data["club_geometry_revision"],
    )
    serialize_calibration_club_binding(binding)
    return binding


def save_calibration_club_binding(
    path: str | Path, binding: CalibrationClubBinding
) -> None:
    """Persist a separately supplied revision binding for later comparison."""
    payload = serialize_calibration_club_binding(binding) + "\n"
    destination = Path(path)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_calibration_club_binding(path: str | Path) -> CalibrationClubBinding:
    """Load an independently stored binding; errors propagate fail-closed."""
    return deserialize_calibration_club_binding(
        Path(path).read_text(encoding="utf-8")
    )
