"""Offline synthetic bright silhouette extraction regressions."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.ball_contour_extraction import extract_single_bright_contour


def image_with_disk():
    image = np.zeros((100, 120), dtype=np.uint8)
    cv.circle(image, (60, 50), 15, 220, thickness=-1)
    return image


def extract(image, **overrides):
    options = dict(threshold=100, min_area_px=100., border_margin_px=2.)
    options.update(overrides)
    return extract_single_bright_contour(image, **options)


def test_single_synthetic_disk_contour_is_extracted():
    contour = extract(image_with_disk())
    assert contour.dtype == np.float64
    assert len(contour) >= 5
    assert contour[:, 0].min() == pytest.approx(45.)
    assert contour[:, 0].max() == pytest.approx(75.)


def test_empty_image_is_rejected():
    with pytest.raises(ValueError, match="exactly one"):
        extract(np.zeros((100, 120), dtype=np.uint8))


def test_two_disks_are_ambiguous():
    image = image_with_disk()
    cv.circle(image, (20, 20), 10, 220, thickness=-1)
    with pytest.raises(ValueError, match="exactly one"):
        extract(image)


def test_border_touching_disk_is_rejected():
    image = np.zeros((100, 120), dtype=np.uint8)
    cv.circle(image, (4, 50), 15, 220, thickness=-1)
    with pytest.raises(ValueError, match="border margin"):
        extract(image)


@pytest.mark.parametrize("bad", [
    np.zeros((100, 120, 3), dtype=np.uint8),
    np.zeros((100, 120), dtype=np.uint16),
    np.zeros((2, 120), dtype=np.uint8),
])
def test_invalid_image_domain_rejected(bad):
    with pytest.raises(ValueError, match="contour image"):
        extract(bad)


@pytest.mark.parametrize("threshold", [-1, 255, 100., True])
def test_invalid_threshold_rejected(threshold):
    with pytest.raises(ValueError, match="threshold"):
        extract(image_with_disk(), threshold=threshold)


@pytest.mark.parametrize("area", [0., -1., float("nan"), True])
def test_invalid_area_rejected(area):
    with pytest.raises(ValueError, match="minimum area"):
        extract(image_with_disk(), min_area_px=area)


def test_circularity_accepts_synthetic_disk():
    assert len(extract(image_with_disk(), min_circularity=0.8)) >= 5


def test_circularity_rejects_elongated_bright_shape():
    image = np.zeros((100, 120), dtype=np.uint8)
    cv.rectangle(image, (20, 40), (100, 50), 220, thickness=-1)
    with pytest.raises(ValueError, match="circularity"):
        extract(image, min_circularity=0.8)


@pytest.mark.parametrize("minimum", [-0.1, 1.1, float("nan"), True])
def test_circularity_limit_must_be_valid(minimum):
    with pytest.raises(ValueError, match="minimum circularity"):
        extract(image_with_disk(), min_circularity=minimum)
