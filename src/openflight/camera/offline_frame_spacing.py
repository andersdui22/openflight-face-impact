"""Gate 22 offline frame-spacing diagnostics, without physical contact inference.

Sensor and host clocks are assessed independently. Their deltas cannot
establish exposure synchronization, impact timing, or actual camera FPS.
"""

from __future__ import annotations

from dataclasses import dataclass

from .trigger_timing_quality import assess_trigger_timing
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineFrameSpacing:
    """Immutable capture-clock spacing evidence only."""

    accepted: bool
    reason: str
    sensor_intervals_ns: tuple[int, ...]
    host_intervals_ns: tuple[int, ...]
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("frame spacing cannot confirm physical contact")


def assess_offline_frame_spacing(
    capture: TriggeredCapture,
    *,
    max_sensor_gap_ns: int,
    max_host_gap_ns: int,
) -> OfflineFrameSpacing:
    """Reject missing timing evidence and excessive gaps, never infer contact.

    Gap limits must be selected by the caller for a controlled offline
    fixture; passing them does not validate a physical camera frame rate.
    """
    for name, limit in (
        ("max_sensor_gap_ns", max_sensor_gap_ns),
        ("max_host_gap_ns", max_host_gap_ns),
    ):
        if type(limit) is not int or limit <= 0:
            raise ValueError(f"{name} must be a positive integer")

    timing = assess_trigger_timing(capture)
    if not timing.valid:
        return OfflineFrameSpacing(
            False, f"invalid trigger timing: {timing.reason}", (), (),
        )
    sensor = tuple(
        b.sensor_timestamp_ns - a.sensor_timestamp_ns
        for a, b in zip(capture.frames, capture.frames[1:])
    )
    host = tuple(
        b.host_timestamp_ns - a.host_timestamp_ns
        for a, b in zip(capture.frames, capture.frames[1:])
    )
    if any(delta > max_sensor_gap_ns for delta in sensor):
        return OfflineFrameSpacing(
            False, "sensor clock gap exceeds offline limit", sensor, host,
        )
    if any(delta > max_host_gap_ns for delta in host):
        return OfflineFrameSpacing(
            False, "host clock gap exceeds offline limit", sensor, host,
        )
    return OfflineFrameSpacing(
        True, "capture frame spacing within offline limits; contact unverified",
        sensor, host,
    )
