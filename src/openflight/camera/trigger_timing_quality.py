"""Gate 22 offline validation of capture timing; no physical contact inference."""

from __future__ import annotations

from dataclasses import dataclass

from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class TriggerTimingQuality:
    """Provenance-only timing assessment; no exposure/impact synchronization claim."""

    valid: bool
    reason: str | None
    frame_count: int
    trigger_between_host_frames: bool


def assess_trigger_timing(capture: TriggeredCapture) -> TriggerTimingQuality:
    """Fail closed on incomplete, out-of-order or unanchored capture metadata.

    Host timestamps and sensor timestamps are independent clocks; neither is
    treated as a physical contact timestamp. The trigger is a host-clock event.
    """
    frames = capture.frames
    count = len(frames)

    def reject(reason: str) -> TriggerTimingQuality:
        return TriggerTimingQuality(False, reason, count, False)

    if (
        not isinstance(capture.pre_trigger_count, int)
        or isinstance(capture.pre_trigger_count, bool)
        or not 0 < capture.pre_trigger_count < count
    ):
        return reject("missing pre-trigger or post-trigger frames")
    if (
        not isinstance(capture.trigger_host_timestamp_ns, int)
        or isinstance(capture.trigger_host_timestamp_ns, bool)
        or capture.trigger_host_timestamp_ns < 0
    ):
        return reject("invalid host trigger timestamp")
    if any(
        not isinstance(identity, str) or not identity.strip()
        for identity in (capture.shot_id, capture.session_id)
    ):
        return reject("missing capture identity")

    if any(frame.sensor_timestamp_is_host_alias is not False for frame in frames):
        return reject("independent sensor timestamp unavailable")

    for field in ("sensor_timestamp_ns", "host_timestamp_ns"):
        timestamps = [getattr(frame, field) for frame in frames]
        if any(not isinstance(t, int) or isinstance(t, bool) or t < 0 for t in timestamps):
            return reject(f"invalid {field}")
        if any(later <= earlier for earlier, later in zip(timestamps, timestamps[1:])):
            return reject(f"nonmonotonic {field}")

    last_pre = frames[capture.pre_trigger_count - 1].host_timestamp_ns
    first_post = frames[capture.pre_trigger_count].host_timestamp_ns
    trigger = capture.trigger_host_timestamp_ns
    if not last_pre <= trigger <= first_post:
        return reject("trigger not bracketed by host frame timestamps")
    return TriggerTimingQuality(True, None, count, True)


def validate_candidate_frame_index(
    capture: TriggeredCapture, candidate_index: int,
) -> int:
    """Validate a supplied candidate frame without claiming it is impact.

    The caller must identify a frame independently. A valid trigger cannot
    establish which exposure contained actual ball-to-face contact.
    """
    quality = assess_trigger_timing(capture)
    if not quality.valid:
        raise ValueError(f"invalid capture timing: {quality.reason}")
    if (
        not isinstance(candidate_index, int)
        or isinstance(candidate_index, bool)
        or not 0 <= candidate_index < quality.frame_count
    ):
        raise ValueError("candidate frame index is out of range")
    return candidate_index
