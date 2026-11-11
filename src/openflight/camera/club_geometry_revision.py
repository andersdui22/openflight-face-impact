"""Gate 18/19: deterministic digest of explicitly declared club geometry.

A digest detects changes to metadata; it does not validate source credibility
or prove the dimensions were physically measured.
"""

from __future__ import annotations

import hashlib
import json

from .club_face_model import ClubFaceModel


def club_geometry_revision(model: ClubFaceModel) -> str:
    """Return stable SHA-256 for a validated club model's declared geometry."""
    if not isinstance(model, ClubFaceModel):
        raise ValueError("a validated club model is required")
    content = {
        "schema_version": 1,
        "family": model.family.value,
        "model_id": model.model_id,
        "surface": model.surface.value,
        "width_mm": model.width_mm,
        "height_mm": model.height_mm,
        "bulge_radius_mm": model.bulge_radius_mm,
        "roll_radius_mm": model.roll_radius_mm,
        "evidence_source": model.evidence_source,
    }
    encoded = json.dumps(
        content, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
