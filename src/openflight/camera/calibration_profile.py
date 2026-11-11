"""Versioned, hardware-evidence-aware camera calibration profile.

This module stores offline optics; it never asserts that a physical camera
was calibrated or that a profile is compatible solely from image dimensions.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration

PROFILE_VERSION = 1


@dataclass(frozen=True)
class CameraCalibrationProfile:
    """Immutable metadata for a validated offline Brown-five optics fit."""

    calibration: CheckerboardCalibration
    camera_mode_id: str
    evidence_kind: str = "synthetic_offline"

    def __post_init__(self) -> None:
        if not isinstance(self.camera_mode_id, str) or not self.camera_mode_id.strip():
            raise ValueError("camera mode identity must be a nonempty string")
        if self.evidence_kind != "synthetic_offline":
            raise ValueError("physical calibration evidence is not supported by Gate 16")
        cal = self.calibration
        if not isinstance(cal, CheckerboardCalibration):
            raise ValueError("invalid calibration object")
        if (
            not isinstance(cal.image_size, tuple)
            or len(cal.image_size) != 2
            or any(type(n) is not int or n <= 0 for n in cal.image_size)
        ):
            raise ValueError("image size must contain two positive integers")
        matrix = np.asarray(cal.camera_matrix)
        distortion = np.asarray(cal.distortion)
        if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
            raise ValueError("camera matrix must be finite 3x3")
        if distortion.shape != (5,) or not np.all(np.isfinite(distortion)):
            raise ValueError("distortion must be five finite coefficients")
        fx, fy = matrix[0, 0], matrix[1, 1]
        canonical = np.array([[fx, 0, matrix[0, 2]], [0, fy, matrix[1, 2]], [0, 0, 1]])
        if fx <= 0 or fy <= 0 or not np.array_equal(matrix, canonical):
            raise ValueError("camera matrix must be canonical with positive focal lengths")
        scores = cal.validation_rms_px
        if (
            not isinstance(scores, tuple)
            or not scores
            or any(not isinstance(s, (int, float)) or not math.isfinite(s) or s < 0 for s in scores)
            or not math.isfinite(cal.fit_rms_px)
            or cal.fit_rms_px < 0
        ):
            raise ValueError("calibration residual evidence must be finite and nonnegative")

    def require_mode(self, camera_mode_id: str, image_size: tuple[int, int]) -> None:
        """Fail closed if either explicit mode identity or dimensions differ."""
        if (
            not isinstance(camera_mode_id, str)
            or not camera_mode_id.strip()
            or not isinstance(image_size, tuple)
            or len(image_size) != 2
            or any(type(dimension) is not int or dimension <= 0 for dimension in image_size)
            or camera_mode_id != self.camera_mode_id
            or image_size != self.calibration.image_size
        ):
            raise ValueError("calibration profile is incompatible with camera mode")

    def to_json(self) -> str:
        """Serialize deterministic, versioned optics without claiming physical validity."""
        cal = self.calibration
        return json.dumps({
            "version": PROFILE_VERSION,
            "evidence_kind": self.evidence_kind,
            "camera_mode_id": self.camera_mode_id,
            "image_size": list(cal.image_size),
            "camera_matrix": np.asarray(cal.camera_matrix).tolist(),
            "distortion": np.asarray(cal.distortion).tolist(),
            "fit_rms_px": cal.fit_rms_px,
            "validation_rms_px": list(cal.validation_rms_px),
        }, sort_keys=True, allow_nan=False)

    @classmethod
    def from_json(cls, content: str) -> CameraCalibrationProfile:
        """Reject unknown fields and versions instead of silently guessing."""
        data = json.loads(content)
        if not isinstance(data, dict) or set(data) != {
            "version", "evidence_kind", "camera_mode_id", "image_size",
            "camera_matrix", "distortion", "fit_rms_px", "validation_rms_px",
        } or type(data["version"]) is not int or data["version"] != PROFILE_VERSION:
            raise ValueError("unsupported calibration profile schema or version")
        size = data["image_size"]
        if not isinstance(size, list) or len(size) != 2:
            raise ValueError("invalid image size")
        scores = data["validation_rms_px"]
        if not isinstance(scores, list):
            raise ValueError("invalid validation residuals")
        cal = CheckerboardCalibration(
            tuple(size), np.asarray(data["camera_matrix"]),
            np.asarray(data["distortion"]), data["fit_rms_px"], tuple(scores),
        )
        return cls(cal, data["camera_mode_id"], data["evidence_kind"])
