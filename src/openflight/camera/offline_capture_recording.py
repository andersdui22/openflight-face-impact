"""Persist bounded adapter rasters for later offline review."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_STORED, BadZipFile, ZipFile

import numpy as np

from .offline_capture_batch import capture_fingerprint
from .triggered_buffer import CameraFrame, TriggeredCapture

_MAX_CAPTURE_BYTES = 64 * 1024 * 1024
MAX_RECORDING_FRAMES = 512


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
            or not 0 < capture.pre_trigger_count < len(capture.frames) <= MAX_RECORDING_FRAMES):
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
        if alias and (frame.sensor_timestamp_ns != frame.host_timestamp_ns
                      or frame.exposure_us != 0 or type(frame.analogue_gain) is not float
                      or frame.analogue_gain != 0.0):
            raise ValueError("noncanonical USB host-alias metadata")
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


@dataclass(frozen=True)
class OfflineCaptureRecording:
    capture: TriggeredCapture
    source: str
    app_sha: str
    fingerprint: str


_MAX_MANIFEST = 512 * 1024


def _unique_json_object(pairs):
    values = dict(pairs)
    if len(values) != len(pairs):
        raise ValueError("duplicate recording metadata field")
    return values


def _uint(value):
    return type(value) is int and 0 <= value < 2**63


def _read_manifest(archive):
    info = archive.getinfo("manifest.json")
    if info.file_size > _MAX_MANIFEST or info.compress_type != ZIP_STORED:
        raise ValueError("unsupported recording manifest size or compression")
    manifest = json.loads(archive.read(info), object_pairs_hook=_unique_json_object)
    if (not isinstance(manifest, dict) or set(manifest) != {
            "schema_version", "source", "physically_validated", "app_sha", "capture_fingerprint",
            "shot_id", "session_id", "trigger_host_timestamp_ns", "pre_trigger_count",
            "width", "height", "frames",
    } or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or manifest["physically_validated"] is not False):
        raise ValueError("unsupported recording manifest")
    if (manifest["source"] not in ("synthetic_fixture", "usb_preview_adapter")
            or any(not isinstance(manifest[key], str) or not re.fullmatch(pattern, manifest[key])
                   for key, pattern in (("app_sha", r"[0-9a-f]{40}"),
                                        ("capture_fingerprint", r"[0-9a-f]{64}")))
            or any(not isinstance(manifest[key], str) or not manifest[key].strip()
                   for key in ("shot_id", "session_id"))):
        raise ValueError("invalid recording identity")
    frames = manifest["frames"]
    width, height, pre, trigger = (manifest[key] for key in
                                    ("width", "height", "pre_trigger_count", "trigger_host_timestamp_ns"))
    if (not all(_uint(value) for value in (width, height, pre, trigger))
            or not isinstance(frames, list) or not 0 < pre < len(frames) <= MAX_RECORDING_FRAMES
            or not width or not height or width * height * len(frames) > _MAX_CAPTURE_BYTES):
        raise ValueError("invalid recording dimensions or capture window")
    expected = {"manifest.json", *(f"frames/{index:04d}.gray8" for index in range(len(frames)))}
    if len(archive.infolist()) != len(expected) or set(archive.namelist()) != expected:
        raise ValueError("unexpected or duplicate recording members")
    return manifest


def _read_frame(archive, entry, name, shape):
    if (not isinstance(entry, dict) or set(entry) != {
            "file", "sha256", "host_timestamp_ns", "sensor_timestamp_ns",
            "sensor_timestamp_is_host_alias", "exposure_us", "analogue_gain",
    } or entry["file"] != name or not isinstance(entry["sha256"], str)
            or not _uint(entry["host_timestamp_ns"])
            or type(entry["sensor_timestamp_is_host_alias"]) is not bool):
        raise ValueError("invalid recording frame metadata")
    host = entry["host_timestamp_ns"]
    sensor, exposure, gain = (entry[key] for key in
                              ("sensor_timestamp_ns", "exposure_us", "analogue_gain"))
    alias = entry["sensor_timestamp_is_host_alias"]
    if alias:
        if (sensor, exposure, gain) != (None, None, None):
            raise ValueError("host-alias frame contains independent sensor metadata")
        # Reconstruct the legacy ring fields for exact fingerprint verification.
        sensor, exposure, gain = host, 0, 0.0
    elif (not _uint(sensor) or not _uint(exposure) or type(gain) not in (int, float)
          or not 0 <= gain < 2**63):
        raise ValueError("invalid recording sensor metadata")

    info = archive.getinfo(name)
    if info.compress_type != ZIP_STORED or info.file_size != shape[0] * shape[1]:
        raise ValueError("invalid recording raster size or compression")
    raster = archive.read(info)
    if sha256(raster).hexdigest() != entry["sha256"]:
        raise ValueError("recording raster hash mismatch")
    return CameraFrame(np.frombuffer(raster, dtype=np.uint8).reshape(shape),
                       sensor, host, exposure, gain, alias)


def load_offline_capture(path: Path) -> OfflineCaptureRecording:
    """Verify a bounded v1 recording without extracting any ZIP members."""
    try:
        with path.open("rb") as stream:
            if os.fstat(stream.fileno()).st_size > _MAX_CAPTURE_BYTES + 2 * _MAX_MANIFEST:
                raise ValueError("recording exceeds archive size limit")
            with ZipFile(stream) as archive:
                manifest = _read_manifest(archive)
                shape = manifest["height"], manifest["width"]
                frames = tuple(
                    _read_frame(archive, entry, f"frames/{index:04d}.gray8", shape)
                    for index, entry in enumerate(manifest["frames"])
                )
    except (OSError, BadZipFile, RuntimeError, KeyError, UnicodeError, RecursionError) as error:
        raise ValueError("unreadable offline recording") from error

    capture = TriggeredCapture(
        frames, manifest["pre_trigger_count"], manifest["trigger_host_timestamp_ns"],
        manifest["shot_id"], manifest["session_id"],
    )
    if capture_fingerprint(capture) != manifest["capture_fingerprint"]:
        raise ValueError("recording capture fingerprint mismatch")
    return OfflineCaptureRecording(
        capture, manifest["source"], manifest["app_sha"], manifest["capture_fingerprint"],
    )
