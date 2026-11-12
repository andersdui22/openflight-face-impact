"""Opt-in integrity-checked preflight for synthetic/offline camera captures.

No impact inference, event publication or physical camera validation occurs.
"""
from __future__ import annotations

from dataclasses import dataclass

from .offline_capture_batch import capture_fingerprint
from .offline_capture_quality import OfflineCaptureQuality, require_usable_offline_capture
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineCapturePreflight:
    """Immutable evidence that a specific capture passed offline preflight."""

    source_fingerprint: str
    quality: OfflineCaptureQuality


def preflight_offline_capture(
    capture: TriggeredCapture,
    *,
    max_frames: int = 512,
    max_sensor_gap_ns: int = 100_000_000,
    max_host_gap_ns: int = 100_000_000,
) -> OfflineCapturePreflight:
    """Validate image/timing quality while binding result to exact frame bytes.

    Fingerprints before and after assessment catch mutation during validation.
    The returned digest must be checked again by any downstream consumer.
    """
    before = capture_fingerprint(capture)
    quality = require_usable_offline_capture(
        capture,
        max_frames=max_frames,
        max_sensor_gap_ns=max_sensor_gap_ns,
        max_host_gap_ns=max_host_gap_ns,
    )
    if capture_fingerprint(capture) != before:
        raise ValueError("capture changed during offline preflight")
    return OfflineCapturePreflight(source_fingerprint=before, quality=quality)


def require_matching_preflight(
    capture: TriggeredCapture,
    preflight: OfflineCapturePreflight,
) -> OfflineCaptureQuality:
    """Fail closed when previously checked frames or metadata have changed."""
    if not isinstance(preflight, OfflineCapturePreflight):
        raise ValueError("typed offline preflight required")
    if capture_fingerprint(capture) != preflight.source_fingerprint:
        raise ValueError("capture differs from offline preflight")
    return preflight.quality
