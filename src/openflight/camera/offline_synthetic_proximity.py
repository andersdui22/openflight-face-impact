"""Gate 22: image-space proximity evidence, never physical contact detection.

Distances between synthetic silhouettes are in pixels, not calibrated 3D
contact distances. A minimum is not automatically an impact timestamp.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2 as cv
import numpy as np

from .offline_dual_object_sequence import OfflineDualObjectSequence
from .triggered_buffer import TriggeredCapture
from .offline_capture_batch import capture_fingerprint


@dataclass(frozen=True)
class SyntheticProximitySample:
    """One image-space ball-to-face separation with source timestamps."""

    frame_index: int
    sensor_timestamp_ns: int
    host_timestamp_ns: int
    separation_px: float


@dataclass(frozen=True)
class SyntheticProximityEvidence:
    """Ordered pixel distances, without asserting a contact instant."""

    samples: tuple[SyntheticProximitySample, ...]
    closest_frame_index: int | None
    reason: str
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("pixel proximity cannot confirm physical contact")


def assess_synthetic_proximity(
    capture: TriggeredCapture,
    sequence: OfflineDualObjectSequence,
    *,
    max_sensor_gap_ns: int,
    max_host_gap_ns: int,
) -> SyntheticProximityEvidence:
    """Return a unique closest observed frame only for sound temporal evidence.

    Multiple equally close frames, missing samples or discontinuous capture
    timing prevent ranking. A closest frame is not a contact-frame estimate.
    """
    if not isinstance(sequence, OfflineDualObjectSequence):
        raise ValueError("typed synthetic sequence required")
    if sequence.source_capture_fingerprint != capture_fingerprint(capture):
        raise ValueError("synthetic sequence does not belong to capture")
    if (type(max_sensor_gap_ns) is not int or max_sensor_gap_ns <= 0
            or type(max_host_gap_ns) is not int or max_host_gap_ns <= 0):
        raise ValueError("timestamp gap limits must be positive integers")
    if sequence.rejected:
        return SyntheticProximityEvidence((), None, "incomplete image sequence")
    if len(sequence.assessed) < 2:
        return SyntheticProximityEvidence((), None, "at least two observed frames required")
    samples = []
    previous = None
    for index, result in sorted(sequence.assessed, key=lambda pair: pair[0]):
        if type(index) is not int or not 0 <= index < len(capture.frames):
            raise ValueError("invalid frame index")
        frame = capture.frames[index]
        if previous is not None:
            prev_index, prev_sensor, prev_host = previous
            if (index != prev_index + 1
                    or not 0 < frame.sensor_timestamp_ns - prev_sensor <= max_sensor_gap_ns
                    or not 0 < frame.host_timestamp_ns - prev_host <= max_host_gap_ns):
                return SyntheticProximityEvidence((), None, "discontinuous frame timing")
        previous = (index, frame.sensor_timestamp_ns, frame.host_timestamp_ns)
        face = np.asarray(result.observation.face.pixels_px, dtype=np.float32)
        ball = np.asarray(result.observation.ball_contour_px, dtype=np.float32)
        if (face.shape != (4, 2) or ball.ndim != 2 or ball.shape[1] != 2
                or not np.all(np.isfinite(face)) or not np.all(np.isfinite(ball))):
            raise ValueError("invalid observed shape coordinates")
        # pointPolygonTest is signed: a ball point within the face silhouette
        # has zero image-space separation, not proof of 3D contact.
        polygon = face.reshape(-1, 1, 2)
        distance = min(max(0., -cv.pointPolygonTest(
            polygon, (float(x), float(y)), True,
        )) for x, y in ball)
        samples.append(SyntheticProximitySample(
            index, frame.sensor_timestamp_ns, frame.host_timestamp_ns,
            float(distance),
        ))
    min_distance = min(item.separation_px for item in samples)
    closest = [item.frame_index for item in samples
               if abs(item.separation_px - min_distance) <= 1e-6]
    if len(closest) != 1:
        return SyntheticProximityEvidence(
            tuple(samples), None, "equally close synthetic frames are ambiguous",
        )
    return SyntheticProximityEvidence(
        tuple(samples), closest[0],
        "unique minimum image-space separation; physical contact unverified",
    )
