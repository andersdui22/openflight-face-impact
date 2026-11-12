"""Gate 21 synthetic multi-frame image observation regression tests."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.offline_face_observation_batch import (
    observe_synthetic_face_frames,
)
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture_from_images(images):
    return TriggeredCapture(
        tuple(CameraFrame(image, 100 * (i + 1), 1000 * (i + 1), 100, 1.)
              for i, image in enumerate(images)),
        1, 1500, shot_id="synthetic-shot", session_id="synthetic-session",
    )


def rectangle():
    image = np.zeros((160, 240), dtype=np.uint8)
    cv.fillConvexPoly(image, np.array(
        [[50, 40], [170, 43], [162, 118], [46, 112]], np.int32,
    ), 230)
    return image


def observe(images, indices):
    return observe_synthetic_face_frames(
        capture_from_images(images), indices, image_size=(240, 160),
    )


def test_image_derived_candidates_preserve_frame_and_identity():
    face = rectangle()
    result = observe([np.zeros_like(face), face, np.zeros_like(face)], (0, 1, 2))
    assert len(result.candidates) == 1
    assert result.candidates[0].frame_index == 1
    assert result.observations[0].shot_id == "synthetic-shot"
    assert result.observations[0].session_id == "synthetic-session"
    assert result.candidates[0].face_pixels_px.flags.writeable is False
    assert [index for index, _ in result.rejected] == [0, 2]
    assert result.physical_clubface_confirmed is False


def test_multiple_shapes_and_occlusion_fail_closed():
    good = rectangle()
    multiple = good.copy()
    cv.rectangle(multiple, (185, 35), (215, 65), 230, -1)
    occluded = good.copy()
    cv.circle(occluded, (105, 75), 15, 0, -1)
    result = observe([good, multiple, occluded], (0, 1, 2))
    assert [item.frame_index for item in result.candidates] == [0]
    assert [index for index, _ in result.rejected] == [1, 2]
    assert all(reason for _, reason in result.rejected)


def test_noisy_background_below_threshold_does_not_change_observation():
    good = rectangle()
    noise = np.random.default_rng(123).integers(
        0, 60, good.shape, dtype=np.uint8,
    )
    noisy = np.maximum(good, noise)
    result = observe([good, noisy], (0, 1))
    assert len(result.candidates) == 2
    np.testing.assert_array_equal(
        result.candidates[0].face_pixels_px,
        result.candidates[1].face_pixels_px,
    )


@pytest.mark.parametrize("indices", [(), (0, 0), (-1,), (2,), (True,), [0]])
def test_invalid_frame_selection_rejected(indices):
    with pytest.raises(ValueError, match="frame indices"):
        observe([rectangle(), rectangle()], indices)


def test_ambiguous_batch_never_selects_contact_frame():
    good = rectangle()
    result = observe([good, good], (0, 1))
    assert len(result.candidates) == 2
    assert not hasattr(result, "contact_frame_index")
    assert result.physical_clubface_confirmed is False
