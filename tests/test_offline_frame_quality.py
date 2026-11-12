"""Deterministic software-only frame preflight tests."""
import numpy as np
import pytest

from openflight.camera.offline_frame_quality import (
    inspect_offline_frame,
    require_usable_offline_frame,
)


def test_balanced_frame_reports_observed_diagnostics():
    image = np.tile(np.array([20, 60, 120, 200], dtype=np.uint8), (4, 1))
    result = require_usable_offline_frame(image)
    assert (result.width, result.height) == (4, 4)
    assert result.brightness_mean == 100.0
    assert result.saturated_fraction == 0.0
    assert result.dark_fraction == 0.0
    assert result.contrast_span > 100


@pytest.mark.parametrize("image,reason", [
    (None, "numpy"),
    (np.zeros((0, 5), dtype=np.uint8), "at least 2x2"),
    (np.zeros((2, 2, 3), dtype=np.uint8), "grayscale"),
    (np.zeros((2, 2), dtype=np.float32), "grayscale"),
    (np.zeros((1, 5), dtype=np.uint8), "at least 2x2"),
])
def test_invalid_frames_rejected(image, reason):
    with pytest.raises(ValueError, match=reason):
        inspect_offline_frame(image)


def test_noncontiguous_frame_rejected():
    image = np.zeros((4, 8), dtype=np.uint8)[:, ::2]
    with pytest.raises(ValueError, match="contiguous"):
        inspect_offline_frame(image)


@pytest.mark.parametrize("level,reason", [
    (0, "underexposed"),
    (255, "overexposed"),
    (100, "insufficient contrast"),
])
def test_unusable_frames_fail_closed(level, reason):
    with pytest.raises(ValueError, match=reason):
        require_usable_offline_frame(np.full((10, 10), level, dtype=np.uint8))


@pytest.mark.parametrize("kwargs", [
    {"max_dark_fraction": -1},
    {"max_saturated_fraction": 1.1},
    {"min_contrast_span": float("nan")},
    {"min_contrast_span": True},
])
def test_invalid_thresholds_rejected(kwargs):
    with pytest.raises(ValueError):
        require_usable_offline_frame(np.ones((2, 2), dtype=np.uint8), **kwargs)
