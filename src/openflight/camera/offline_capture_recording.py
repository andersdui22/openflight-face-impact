"""Persist bounded adapter rasters for later offline review."""

from __future__ import annotations

import json
import os
import re
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import numpy as np

from .offline_capture_batch import capture_fingerprint
from .triggered_buffer import TriggeredCapture

_MAX_CAPTURE_BYTES = 64 * 1024 * 1024
_MAX_FRAMES = 512


def save_offline_capture(
    directory: Path,
    capture: TriggeredCapture,
    *,
    app_sha: str,
    source: str,
) -> Path:
    """Write a ZIP of lossless uint8 rasters and provenance on the caller's worker."""
    if not re.fullmatch(r"[0-9a-f]{40}", app_sha) or source not in ("usb_preview_adapter", "synthetic_fixture"):
        raise ValueError("app SHA and known acquisition source required")
    if (not capture.shot_id or not capture.session_id
            or not 0 < capture.pre_trigger_count < len(capture.frames) <= _MAX_FRAMES):
        raise ValueError("complete capture and shot/session identity required")

    shape = capture.frames[0].image.shape
    if len(shape) != 2 or not all(shape):
        raise ValueError("nonempty monochrome rasters required")
    if len(capture.frames) * shape[0] * shape[1] > _MAX_CAPTURE_BYTES:
        raise ValueError("capture exceeds recording size limit")

    frames = []
    for index, frame in enumerate(capture.frames):
        if frame.image.shape != shape or frame.image.dtype != np.uint8:
            raise ValueError("capture rasters must share uint8 dimensions")
        alias = frame.sensor_timestamp_is_host_alias
        frames.append({
            "file": f"frames/{index:04d}.gray8",
            "host_timestamp_ns": frame.host_timestamp_ns,
            "sensor_timestamp_ns": None if alias else frame.sensor_timestamp_ns,
            "sensor_timestamp_is_host_alias": alias,
            "exposure_us": None if alias else frame.exposure_us,
            "analogue_gain": None if alias else frame.analogue_gain,
        })

    fingerprint = capture_fingerprint(capture)
    manifest = {
        "schema_version": 1,
        "source": source,
        "physically_validated": False,
        "app_sha": app_sha,
        "capture_fingerprint": fingerprint,
        "shot_id": capture.shot_id,
        "session_id": capture.session_id,
        "trigger_host_timestamp_ns": capture.trigger_host_timestamp_ns,
        "pre_trigger_count": capture.pre_trigger_count,
        "width": shape[1],
        "height": shape[0],
        "frames": frames,
    }
    directory.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=directory, prefix="capture-", suffix=".partial", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with ZipFile(temporary, "w") as recording:
            for frame, entry in zip(capture.frames, frames):
                raster = frame.image.tobytes()
                entry["sha256"] = sha256(raster).hexdigest()
                recording.writestr(entry["file"], raster)
            recording.writestr("manifest.json", json.dumps(manifest, allow_nan=False))
        if capture_fingerprint(capture) != fingerprint:
            raise ValueError("capture changed during recording")
        final = temporary.with_suffix(".zip")
        os.replace(temporary, final)
        return final
    finally:
        temporary.unlink(missing_ok=True)
