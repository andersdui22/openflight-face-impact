"""Bounded, software-only quality assessment of a triggered image sequence."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .offline_frame_quality import OfflineFrameQuality, require_usable_offline_frame
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineCaptureQuality:
    """Per-frame diagnostics; no physical accuracy or contact claim."""

    frame_count: int
    frame_quality: tuple[OfflineFrameQuality, ...]
    min_sensor_interval_ns: int | None
    max_sensor_interval_ns: int | None


def require_usable_offline_capture(
    capture: TriggeredCapture,
    *,
    max_frames: int = 512,
    max_sensor_gap_ns: int = 100_000_000,
    max_host_gap_ns: int = 100_000_000,
) -> OfflineCaptureQuality:
    """Validate a complete immutable-identity capture before image analysis.

    Every frame must pass image preflight. Timestamps must be strictly increasing
    in both domains; a rejected frame aborts the whole sequence. This is not
    proof that an impact occurred between frames.
    """
    if not isinstance(capture, TriggeredCapture):
        raise ValueError("expected TriggeredCapture")
    for name, value in (
        ("max_frames", max_frames),
        ("max_sensor_gap_ns", max_sensor_gap_ns),
        ("max_host_gap_ns", max_host_gap_ns),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    frames = capture.frames
    if not 1 <= len(frames) <= max_frames:
        raise ValueError("capture frame count outside allowed bounds")
    if not 0 <= capture.pre_trigger_count <= len(frames):
        raise ValueError("invalid pre-trigger frame count")
    if not isinstance(capture.shot_id, str) or not capture.shot_id.strip():
        raise ValueError("capture requires a shot identity")
    if not isinstance(capture.session_id, str) or not capture.session_id.strip():
        raise ValueError("capture requires a session identity")
    if not isinstance(capture.trigger_host_timestamp_ns, int) or isinstance(capture.trigger_host_timestamp_ns, bool) or capture.trigger_host_timestamp_ns < 0:
        raise ValueError("invalid capture trigger timestamp")
    qualities = []
    intervals = []
    expected_shape = None
    for index, frame in enumerate(frames):
        for name in ("sensor_timestamp_ns", "host_timestamp_ns", "exposure_us"):
            value = getattr(frame, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"invalid frame {name}")
        if frame.exposure_us == 0:
            raise ValueError("invalid frame exposure_us")
        if (not isinstance(frame.analogue_gain, (int, float))
                or isinstance(frame.analogue_gain, bool)
                or not math.isfinite(frame.analogue_gain)
                or frame.analogue_gain <= 0):
            raise ValueError("invalid frame analogue_gain")
        quality = require_usable_offline_frame(frame.image)
        shape = (quality.height, quality.width)
        if expected_shape is not None and shape != expected_shape:
            raise ValueError("capture frame dimensions changed")
        expected_shape = shape
        if index:
            previous = frames[index - 1]
            sensor_gap = frame.sensor_timestamp_ns - previous.sensor_timestamp_ns
            host_gap = frame.host_timestamp_ns - previous.host_timestamp_ns
            if not 0 < sensor_gap <= max_sensor_gap_ns:
                raise ValueError("capture sensor timestamp discontinuity")
            if not 0 < host_gap <= max_host_gap_ns:
                raise ValueError("capture host timestamp discontinuity")
            intervals.append(sensor_gap)
        qualities.append(quality)
    return OfflineCaptureQuality(
        frame_count=len(frames),
        frame_quality=tuple(qualities),
        min_sensor_interval_ns=min(intervals) if intervals else None,
        max_sensor_interval_ns=max(intervals) if intervals else None,
    )
