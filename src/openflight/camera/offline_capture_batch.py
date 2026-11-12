"""Gates 20-24: single offline entry point for frame candidates and audit.

This orchestrates explicit synthetic observations, never detects physical
contact timing or assigns physically measured confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_batch_audit import SyntheticBatchAudit, audit_synthetic_candidate_batch
from .synthetic_face_polygon import SyntheticFacePolygon
from .synthetic_frame_candidates import (
    AssessedFrameCandidate, SyntheticFrameCandidate, assess_synthetic_frame_candidates,
)
from .triggered_buffer import TriggeredCapture


def capture_fingerprint(capture: TriggeredCapture) -> str:
    """Bind offline assessments to exact frame bytes, timing and identity."""
    if not isinstance(capture, TriggeredCapture):
        raise ValueError("capture fingerprint requires a typed capture")
    digest = hashlib.sha256()
    header = (capture.shot_id, capture.session_id,
              capture.pre_trigger_count, capture.trigger_host_timestamp_ns,
              len(capture.frames))
    digest.update(repr(header).encode("utf-8"))
    for frame in capture.frames:
        image = np.asarray(frame.image)
        if image.dtype.hasobject:
            raise ValueError("capture image cannot have object dtype")
        metadata = (frame.sensor_timestamp_ns, frame.host_timestamp_ns,
                    frame.exposure_us, frame.analogue_gain,
                    image.shape, image.dtype.str)
        digest.update(repr(metadata).encode("utf-8"))
        if frame.sensor_timestamp_is_host_alias is not False:
            digest.update(b"host-arrival-alias")
        digest.update(np.ascontiguousarray(image).tobytes())
    return digest.hexdigest()



@dataclass(frozen=True)
class OfflineCaptureBatchResult:
    """Frame-preserving synthetic assessments and their consistency audit."""

    frames: tuple[AssessedFrameCandidate, ...]
    audit: SyntheticBatchAudit
    source_capture_fingerprint: str = ""


def assess_offline_capture_batch(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    capture: TriggeredCapture,
    candidates: tuple[SyntheticFrameCandidate, ...],
    landmarks_face_mm: np.ndarray,
    polygon: SyntheticFacePolygon,
    *,
    ball_radius_mm: float,
    max_ball_residual_rad: float,
    max_face_rms_px: float,
    min_face_margin_px: float,
    contact_tolerance_mm: float,
    threshold: int,
    min_area_px: float,
    ball_border_margin_px: float,
    min_circularity: float = 0.0,
    max_candidates: int = 32,
) -> OfflineCaptureBatchResult:
    """Compose candidate extraction, synthetic geometry and evidence audit.

    A successful synthetic geometry result is not proof of physical impact.
    Every candidate is supplied explicitly; no best frame is selected.
    """
    source_fingerprint = capture_fingerprint(capture)
    frames = assess_synthetic_frame_candidates(
        calibration, capture, candidates, landmarks_face_mm, polygon,
        ball_radius_mm=ball_radius_mm,
        max_ball_residual_rad=max_ball_residual_rad,
        max_face_rms_px=max_face_rms_px,
        min_face_margin_px=min_face_margin_px,
        contact_tolerance_mm=contact_tolerance_mm,
        threshold=threshold,
        min_area_px=min_area_px,
        ball_border_margin_px=ball_border_margin_px,
        min_circularity=min_circularity,
        max_candidates=max_candidates,
    )
    if capture_fingerprint(capture) != source_fingerprint:
        raise ValueError("capture changed during offline assessment")
    return OfflineCaptureBatchResult(
        frames=frames,
        audit=audit_synthetic_candidate_batch(frames),
        source_capture_fingerprint=source_fingerprint,
    )
