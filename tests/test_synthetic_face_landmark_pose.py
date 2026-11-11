"""Synthetic planar correspondences with known metric position and orientation."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.synthetic_face_frame import SyntheticFaceFrame, world_to_synthetic_face
from openflight.camera.synthetic_face_landmark_pose import estimate_synthetic_face_pose

SIZE = (640, 400)
LANDMARKS = np.array([[-44, -19], [42, -17], [36, 22], [-35, 18], [8, 12], [-9, -4]])


@pytest.fixture
def calibration():
    return CheckerboardCalibration(
        SIZE,
        np.array([[530.0, 0, 315], [0, 525.0, 198], [0, 0, 1]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.01]),
        0.0,
        (),
    )


def project(calibration, rotation, translation, landmarks=LANDMARKS):
    points = np.column_stack((landmarks, np.zeros(len(landmarks)))).astype(float)
    rvec, _ = cv.Rodrigues(rotation)
    image, _ = cv.projectPoints(
        points, rvec, translation, calibration.camera_matrix, calibration.distortion
    )
    return image.reshape(-1, 2)


def rotation_from_front(tilt):
    rotation, _ = cv.Rodrigues(np.array(tilt, dtype=float))
    return rotation @ np.diag([1.0, -1.0, -1.0])


@pytest.mark.parametrize(
    ("tilt", "translation"),
    [((0.29, -0.32, 0.2), [64.0, -22.0, 420.0]),
     ((-0.32, 0.35, -0.17), [-134.0, 55.0, 530.0])],
)
def test_known_metric_pose_and_face_frame(calibration, tilt, translation):
    rotation = rotation_from_front(tilt)
    translation = np.array(translation)
    result = estimate_synthetic_face_pose(
        calibration, LANDMARKS, project(calibration, rotation, translation),
        image_size=SIZE, max_rms_px=0.5, min_margin_px=0.1,
    )
    pose = result.pose_model_to_camera
    np.testing.assert_allclose(pose.translation_model_to_world_mm, translation, atol=1e-5)
    np.testing.assert_allclose(pose.rotation_model_to_world, rotation, atol=1e-7)
    assert result.rms_px < 1e-6
    assert result.runner_up_rms_px > 0.1

    axes = np.eye(3)
    frame = SyntheticFaceFrame(np.zeros(3), *axes)
    known_local_mm = np.array([10.0, -3.0, 21.35])
    ball_camera_mm = rotation @ known_local_mm + translation
    local = world_to_synthetic_face(ball_camera_mm, frame, pose)
    np.testing.assert_allclose(local, known_local_mm, atol=1e-5)


def test_weak_perspective_has_two_similarly_good_candidates(calibration):
    rotation = rotation_from_front((0.10, 0.08, 0.1))
    pixels = project(calibration, rotation, np.array([0.0, 0.0, 1800.0]))
    with pytest.raises(ValueError, match="ambiguous"):
        estimate_synthetic_face_pose(
            calibration, LANDMARKS, pixels, image_size=SIZE, max_rms_px=0.5, min_margin_px=0.1,
        )


def test_bad_correspondences_fail_reprojection(calibration):
    pixels = project(calibration, rotation_from_front((0.29, -0.32, 0.2)),
                     np.array([64.0, -22.0, 420.0]))
    pixels[-1] += [15, 12]
    with pytest.raises(ValueError, match="reprojection"):
        estimate_synthetic_face_pose(
            calibration, LANDMARKS, pixels, image_size=SIZE, max_rms_px=0.5, min_margin_px=0.1,
        )


def test_back_of_face_is_rejected(calibration):
    pixels = project(calibration, np.eye(3), np.array([0.0, 0.0, 420.0]))
    with pytest.raises(ValueError, match="reprojection"):
        estimate_synthetic_face_pose(
            calibration, LANDMARKS, pixels, image_size=SIZE, max_rms_px=0.5, min_margin_px=0.1,
        )


@pytest.mark.parametrize(
    ("landmarks", "size", "message"),
    [(LANDMARKS, (320, 200), "dimensions"),
     (LANDMARKS[:-1], SIZE, "corresponding"),
     (np.column_stack((np.arange(6), np.zeros(6))), SIZE, "planar spread"),
     (np.vstack((LANDMARKS[:-1], LANDMARKS[0])), SIZE, "distinct")],
)
def test_invalid_inputs(calibration, landmarks, size, message):
    pixels = project(calibration, rotation_from_front((0.29, -0.32, 0.2)),
                     np.array([64.0, -22.0, 420.0]))
    with pytest.raises(ValueError, match=message):
        estimate_synthetic_face_pose(
            calibration, landmarks, pixels, image_size=size, max_rms_px=0.5, min_margin_px=0.1,
        )


@pytest.mark.parametrize("bad_limit", [
    None, True, False, "0.5", [], {}, np.array([0.5]),
    0., -1., float("nan"), float("inf"),
])
@pytest.mark.parametrize("field", ["max_rms_px", "min_margin_px"])
def test_gate21_malformed_pose_quality_threshold_fails_closed(
    calibration, bad_limit, field,
):
    pixels = project(
        calibration, rotation_from_front((0.29, -0.32, 0.2)),
        np.array([64.0, -22.0, 420.0]),
    )
    limits = {"max_rms_px": 0.5, "min_margin_px": 0.1}
    limits[field] = bad_limit
    with pytest.raises(ValueError, match="pose score thresholds"):
        estimate_synthetic_face_pose(
            calibration, LANDMARKS, pixels, image_size=SIZE, **limits,
        )


def test_gate21_landmark_border_margin_accepts_clear_synthetic_pose(calibration):
    pixels = project(
        calibration, rotation_from_front((0.29, -0.32, 0.2)),
        np.array([64.0, -22.0, 420.0]),
    )
    result = estimate_synthetic_face_pose(
        calibration, LANDMARKS, pixels, image_size=SIZE,
        max_rms_px=0.5, min_margin_px=0.1,
        landmark_border_margin_px=2.,
    )
    assert result.rms_px < 1e-6


def test_gate21_landmark_border_margin_rejects_excluded_observation(calibration):
    pixels = project(
        calibration, rotation_from_front((0.29, -0.32, 0.2)),
        np.array([64.0, -22.0, 420.0]),
    )
    with pytest.raises(ValueError, match="excluded image border"):
        estimate_synthetic_face_pose(
            calibration, LANDMARKS, pixels, image_size=SIZE,
            max_rms_px=0.5, min_margin_px=0.1,
            landmark_border_margin_px=200.,
        )


@pytest.mark.parametrize("margin", [-1., float("nan"), float("inf"), True])
def test_gate21_landmark_border_margin_rejects_invalid_limit(calibration, margin):
    pixels = project(
        calibration, rotation_from_front((0.29, -0.32, 0.2)),
        np.array([64.0, -22.0, 420.0]),
    )
    with pytest.raises(ValueError, match="landmark border margin"):
        estimate_synthetic_face_pose(
            calibration, LANDMARKS, pixels, image_size=SIZE,
            max_rms_px=0.5, min_margin_px=0.1,
            landmark_border_margin_px=margin,
        )
