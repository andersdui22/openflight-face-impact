"""Versioned synthetic offline evidence payload for future Socket.IO transport.

Serialization does not emit a Socket.IO event or establish a physical measurement.
"""

from __future__ import annotations

import math

from .offline_impact_evidence import OfflineImpactEvidence


def serialize_offline_impact_evidence(evidence: OfflineImpactEvidence) -> dict:
    """Produce a JSON-safe, explicitly synthetic and identity-bound result."""
    if not isinstance(evidence, OfflineImpactEvidence):
        raise ValueError("offline transport requires typed impact evidence")
    if evidence.physically_validated is not False or evidence.position_uncertainty_mm is not None:
        raise ValueError("offline transport cannot claim physical validation")
    payload = {
        "schema_version": 1,
        "source": "offline_synthetic_analysis",
        "shot_id": evidence.shot_id,
        "session_id": evidence.session_id,
        "accepted": evidence.accepted_for_offline_analysis,
        "reason": evidence.reason,
        "physically_validated": False,
        "position_uncertainty_mm": None,
    }
    if evidence.accepted_for_offline_analysis:
        if (evidence.frame_index is None or isinstance(evidence.frame_index, bool)
                or not isinstance(evidence.frame_index, int)
                or evidence.frame_index < 0):
            raise ValueError("accepted offline frame index must be nonnegative")
        if (any(not isinstance(value, (int, float)) or isinstance(value, bool)
                or not math.isfinite(value) for value in (evidence.x_mm, evidence.y_mm))
                or evidence.horizontal_region not in ("heel", "center", "toe")
                or evidence.vertical_region not in ("low", "center", "high")):
            raise ValueError("accepted offline impact coordinates or regions invalid")
        payload.update({
            "frame_index": evidence.frame_index,
            "x_mm": float(evidence.x_mm),
            "y_mm": float(evidence.y_mm),
            "horizontal_region": evidence.horizontal_region,
            "vertical_region": evidence.vertical_region,
        })
    return payload
