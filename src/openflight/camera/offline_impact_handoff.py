"""Gates 20-24: complete synthetic offline assessment-to-export handoff.

The input is a previously assessed offline batch; this function never
observes a physical contact instant or upgrades synthetic geometry to truth.
"""

from __future__ import annotations

from dataclasses import dataclass

from .offline_capture_batch import OfflineCaptureBatchResult, capture_fingerprint
from .offline_impact_evidence import OfflineImpactEvidence, export_offline_impact_evidence
from .offline_temporal_evidence import (
    OfflineTemporalEvidence, assess_offline_temporal_evidence,
)
from .synthetic_batch_audit import audit_synthetic_candidate_batch
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineImpactHandoff:
    """Audited synthetic batch with temporal evidence and safe export."""

    temporal: OfflineTemporalEvidence
    impact: OfflineImpactEvidence


def prepare_offline_impact_handoff(
    capture: TriggeredCapture,
    batch: OfflineCaptureBatchResult,
    *,
    max_sensor_gap_ns: int,
    max_host_gap_ns: int,
    max_frames: int = 32,
) -> OfflineImpactHandoff:
    """Reaudit a batch, validate timing, and export only admissible evidence."""
    if not isinstance(batch, OfflineCaptureBatchResult):
        raise ValueError("handoff requires a typed offline capture batch")
    if (not batch.source_capture_fingerprint
            or batch.source_capture_fingerprint != capture_fingerprint(capture)):
        raise ValueError("offline batch does not belong to this capture")
    audit = audit_synthetic_candidate_batch(batch.frames)
    if audit != batch.audit:
        raise ValueError("offline batch audit does not match frame assessments")
    temporal = assess_offline_temporal_evidence(
        capture, batch.frames,
        max_sensor_gap_ns=max_sensor_gap_ns,
        max_host_gap_ns=max_host_gap_ns,
        max_frames=max_frames,
    )
    return OfflineImpactHandoff(
        temporal=temporal,
        impact=export_offline_impact_evidence(capture, batch.frames, temporal),
    )
