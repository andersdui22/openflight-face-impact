"""Media Foundation native capture handle used by the existing USB owner."""

from __future__ import annotations

import ctypes as c
import math
import sys
from pathlib import Path

import numpy as np

_FORMATS = {1: "YUY2", 2: "NV12", 3: "MJPG"}
MAX_WINDOW_BYTES = 64 * 1024 * 1024


class Mode(c.Structure):
    _fields_ = [(key, c.c_uint32) for key in ("width", "height", "numerator", "denominator", "format")]

    def settings(self):
        return {key: getattr(self, key) for key, _ in self._fields_} | {"pixel_format": _FORMATS[self.format]}


class Sample(c.Structure):
    _fields_ = [("time_100ns", c.c_int64), ("duration_100ns", c.c_int64),
                ("size", c.c_uint32), ("flags", c.c_uint32), ("discontinuity", c.c_uint32)]


_DEVICE = c.CFUNCTYPE(None, c.c_wchar_p, c.c_wchar_p)
_MODE = c.CFUNCTYPE(None, c.POINTER(Mode))


def _library():
    if sys.platform != "win32":
        raise OSError("Media Foundation is available on Windows")
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3] / "out/face-impact-native"))
    # Only load the bundled or locally built absolute DLL. No search path fallback.
    library = c.CDLL(str(root / "face_impact_mf.dll"))
    signatures = {
        "ofi_scan": (c.c_int32, [_DEVICE]),
        "ofi_modes": (c.c_int32, [c.c_wchar_p, _MODE]),
        "ofi_open": (c.c_int32, [c.c_wchar_p, c.POINTER(Mode), c.POINTER(c.c_void_p)]),
        "ofi_identity": (c.c_wchar_p, [c.c_void_p]),
        "ofi_read": (c.c_int32, [c.c_void_p, c.c_void_p, c.c_uint32, c.POINTER(Sample)]),
        "ofi_control": (c.c_int32, [c.c_void_p, c.c_uint32, c.c_int32, c.POINTER(c.c_int32), c.POINTER(c.c_int32)]),
        "ofi_close": (None, [c.c_void_p]),
    }
    for name, (result, arguments) in signatures.items():
        function = getattr(library, name)
        function.restype = result
        function.argtypes = arguments
    return library


def _check(result, action):
    if result < 0:
        raise RuntimeError(f"Media Foundation {action} failed (0x{result & 0xffffffff:08X})")


def scan_devices():
    devices = []
    _check(_library().ofi_scan(_DEVICE(lambda link, name: devices.append({
        "identity": link, "name": name, "status": "Media Foundation",
    }))), "enumeration")
    counts = {}
    for device in devices:
        identity = device["identity"].casefold()
        counts[identity] = counts.get(identity, 0) + 1
    return [device for device in devices if counts[device["identity"].casefold()] == 1]


def announced_modes(identity):
    modes = {}

    def add(pointer):
        mode = pointer.contents
        if 0 < mode.width * mode.height <= 1920 * 1080 and mode.format in _FORMATS:
            row = mode.settings()
            modes[tuple(row.values())] = row

    _check(_library().ofi_modes(identity, _MODE(add)), "mode enumeration")
    return sorted(modes.values(), key=lambda m: (-m["numerator"] / m["denominator"], m["width"], m["format"]))


def validated_mode(data, frame_count):
    keys = ("width", "height", "numerator", "denominator", "format")
    if not isinstance(data, dict) or any(type(data.get(key)) is not int or not 0 < data[key] <= 65535
                                         for key in keys):
        raise ValueError("Select a valid advertised camera mode")
    mode = Mode(*(data[key] for key in keys))
    pixels = mode.width * mode.height
    if (mode.format not in _FORMATS or pixels > 1920 * 1080
            or (mode.format in (1, 2) and mode.width % 2)
            or (mode.format == 2 and mode.height % 2)
            or 5 * pixels * frame_count > MAX_WINDOW_BYTES):
        raise ValueError("Mode exceeds supported raster or buffered memory limits")
    return mode


class MediaFoundationCamera:
    """Read native samples on the existing camera reader thread."""

    capture_backend = "media_foundation"

    def __init__(self, identity, mode, exposure_mode):
        self._dll = _library()
        self._handle = c.c_void_p()
        self.mode = mode
        self._exposure_mode = exposure_mode
        self.sample_metadata = None
        self.native_payload = None
        self._buffer = c.create_string_buffer(4 * mode.width * mode.height)
        _check(self._dll.ofi_open(identity, c.byref(mode), c.byref(self._handle)), "exact-device open")
        self.opened_identity = self._dll.ofi_identity(self._handle)
        if exposure_mode == "auto":
            self._control(15, True, 0, 1)

    def isOpened(self):
        return bool(self._handle)

    def _control(self, prop, setting, value=0, flags=2):
        current, flag = c.c_int32(value), c.c_int32(flags)
        status = self._dll.ofi_control(self._handle, prop, setting, c.byref(current), c.byref(flag))
        return (current.value, flag.value) if status >= 0 else None

    def set(self, prop, value):
        if prop == 15 and self._exposure_mode != "manual":
            return False
        return prop in (14, 15) and self._control(prop, True, int(value)) is not None

    def get(self, prop):
        negotiation = {3: self.mode.width, 4: self.mode.height, 5: self.mode.numerator / self.mode.denominator}
        if prop in negotiation:
            return negotiation[prop]
        control = self._control(prop, False)
        return control[0] if control is not None else math.nan

    def mode_diagnostics(self):
        return self.mode.settings()

    def exposure_diagnostics(self):
        reported = self._control(15, False)
        return {"requested_mode": self._exposure_mode,
                "reported_mode": {1: "auto", 2: "manual"}.get(reported[1]) if reported else None}

    def read(self):
        for _ in range(32):
            sample = Sample()
            result = self._dll.ofi_read(self._handle, self._buffer, len(self._buffer), c.byref(sample))
            _check(result, "sample read")
            if result == 0:
                break
        else:
            raise RuntimeError("Media Foundation supplied no usable samples")
        payload = c.string_at(self._buffer, sample.size)
        image = analysis_raster(payload, self.mode)
        self.native_payload = payload
        self.sample_metadata = {
            "sample_time_100ns": sample.time_100ns if sample.time_100ns >= 0 else None,
            "sample_duration_100ns": sample.duration_100ns if sample.duration_100ns >= 0 else None,
            "flags": sample.flags, "discontinuity": bool(sample.discontinuity),
            "sequence": None, "provenance": "media_foundation_stream_sample",
        }
        return True, image

    def release(self):
        if self._handle:
            self._dll.ofi_close(self._handle)
            self._handle = c.c_void_p()


def analysis_raster(payload, mode):
    width, height = mode.width, mode.height
    if mode.format == 3:
        import cv2

        # Verify JPEG dimensions before invoking a decoder, which allocates based on its header.
        _check_jpeg_dimensions(payload, width, height)
        image = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_GRAYSCALE)
        if image is None or image.shape != (height, width):
            raise ValueError("Invalid Media Foundation MJPG sample")
        return image
    size = width * height
    expected = 2 * size if mode.format == 1 else size * 3 // 2
    if len(payload) != expected:
        raise ValueError("Unsupported Media Foundation raster stride or sample size")
    raw = np.frombuffer(payload, np.uint8)
    luminance = raw[::2] if mode.format == 1 else raw[:size]
    return luminance.reshape(height, width)


def _check_jpeg_dimensions(payload, width, height):
    # Bound JPEG decoding to the advertised native mode.
    if payload[:2] != b"\xff\xd8":
        raise ValueError("Invalid Media Foundation JPEG header")
    position = 2
    while position + 4 <= len(payload) and payload[position] == 255:
        marker = payload[position + 1]
        if marker == 255:
            position += 1
            continue
        if marker in (0xDA, 0xD9):
            break
        length = int.from_bytes(payload[position + 2:position + 4], "big")
        if length < 2 or position + 2 + length > len(payload):
            break
        if marker in (0xC0, 0xC1, 0xC2) and length >= 8:
            dimensions = (int.from_bytes(payload[position + 7:position + 9], "big"),
                          int.from_bytes(payload[position + 5:position + 7], "big"))
            if dimensions == (width, height):
                return
            break
        position += 2 + length
    raise ValueError("Media Foundation JPEG dimensions differ from negotiated mode")
