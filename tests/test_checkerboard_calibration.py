"""Offline calibration against known virtual optics and separate board views."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.calibrated_rays import calibrated_pixel_rays
from openflight.camera.checkerboard_calibration import Checkerboard, calibrate_checkerboard

BOARD = Checkerboard(8, 6, 24.0)
SIZE = (640, 400)
MATRIX = np.array([[530.0, 0.0, 315.0], [0.0, 525.0, 198.0], [0.0, 0.0, 1.0]])
DISTORTION = np.array([-0.24, 0.08, 0.002, -0.003, 0.0])


@pytest.fixture(scope="module")
def render_board():
    """Render by back-projecting each distorted pixel onto a board plane."""
    x, y = np.meshgrid(np.arange(SIZE[0]), np.arange(SIZE[1]))
    pixels = np.stack((x, y), axis=-1).astype(np.float64)
    normalized = cv.undistortPoints(pixels.reshape(-1, 1, 2), MATRIX, DISTORTION).reshape(-1, 2)
    rays = np.column_stack((normalized, np.ones(len(normalized))))

    def render(rotation, translation):
        rotation, _ = cv.Rodrigues(np.array(rotation, dtype=float))
        translation = np.array(translation, dtype=float)
        scale = (translation @ rotation[:, 2]) / (rays @ rotation[:, 2])
        board_points = (rays * scale[:, None] - translation) @ rotation
        squares = np.floor(board_points[:, :2] / BOARD.square_size_mm).astype(int)
        col, row = squares.T
        inside = (col >= -1) & (col < BOARD.columns) & (row >= -1) & (row < BOARD.rows)
        image = np.full(len(rays), 150, dtype=np.uint8)
        image[inside] = np.where((col[inside] + row[inside]) % 2, 235, 20)
        return cv.GaussianBlur(image.reshape(SIZE[::-1]), (3, 3), 0.6)

    return render


@pytest.fixture(scope="module")
def board_views(render_board):
    poses = [
        ((-0.35, 0.29, 0.04), (-226, -96, 520)),
        ((0.30, -0.33, 0.12), (25, -115, 465)),
        ((0.26, 0.38, -0.13), (-213, -20, 510)),
        ((-0.31, -0.27, 0.08), (25, -38, 550)),
        ((0.45, 0.12, -0.05), (-110, -101, 365)),
        ((-0.28, 0.40, -0.10), (-89, -83, 425)),
        ((0.18, -0.47, 0.22), (-146, -126, 500)),
        ((-0.36, -0.23, -0.19), (-116, -20, 410)),
        ((0.31, 0.20, 0.09), (-31, -110, 445)),
        ((-0.13, -0.44, 0.15), (-180, -111, 445)),
        ((-0.33, 0.23, 0.19), (-32, -53, 485)),
        ((0.21, 0.43, -0.21), (-170, -97, 420)),
        ((0.44, -0.19, 0.07), (-162, -43, 475)),
    ]
    return [render_board(*pose) for pose in poses]


def test_fits_images_and_validates_frozen_optics_on_separate_views(board_views):
    fit = calibrate_checkerboard(BOARD, board_views[:10], board_views[10:], max_validation_rms_px=0.6)
    assert fit.image_size == SIZE
    assert fit.fit_rms_px < 0.5
    assert len(fit.validation_rms_px) == 3
    assert max(fit.validation_rms_px) < 0.6
    np.testing.assert_allclose(fit.camera_matrix.diagonal()[:2], MATRIX.diagonal()[:2], atol=12)
    np.testing.assert_allclose(fit.camera_matrix[:2, 2], MATRIX[:2, 2], atol=9)

    # Verify correction against known off-axis rays, independent of board pose fitting.
    points = np.array([[-0.48, -0.27, 1.0], [0.41, 0.25, 1.0], [0.15, -0.23, 1.0]])
    distorted, _ = cv.projectPoints(points, np.zeros(3), np.zeros(3), MATRIX, DISTORTION)
    corrected = cv.undistortPoints(distorted, fit.camera_matrix, fit.distortion).reshape(-1, 2)
    np.testing.assert_allclose(corrected, points[:, :2], atol=0.021)


def test_rejects_too_few_fit_images(board_views):
    with pytest.raises(ValueError, match="at least 10 fit"):
        calibrate_checkerboard(BOARD, board_views[:9], board_views[10:], max_validation_rms_px=0.6)


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        (lambda images: images[0].copy(), "duplicates"),
        (lambda images: np.full_like(images[0], 150), "no complete checkerboard"),
        (lambda images: images[0][:-1], "different size"),
    ],
)
def test_rejects_invalid_held_out_images(board_views, replacement, message):
    validation = [replacement(board_views), *board_views[11:]]
    with pytest.raises(ValueError, match=message):
        calibrate_checkerboard(BOARD, board_views[:10], validation, max_validation_rms_px=0.6)


def test_rejects_held_out_residual_above_limit(board_views):
    with pytest.raises(ValueError, match="validation RMS limit"):
        calibrate_checkerboard(BOARD, board_views[:10], board_views[10:], max_validation_rms_px=0.001)


def test_rejects_frontoparallel_fit_views(render_board, board_views):
    flat = [
        render_board((0.0, 0.0, 0.0), (-90 + index, -64, 360 + 12 * index))
        for index in range(10)
    ]
    with pytest.raises(ValueError, match="more variation|invalid camera parameters"):
        calibrate_checkerboard(BOARD, flat, board_views[10:], max_validation_rms_px=0.6)


def test_calibration_to_synthetic_ball_and_face_rays(board_views):
    fit = calibrate_checkerboard(BOARD, board_views[:10], board_views[10:], max_validation_rms_px=0.6)
    # Known optical directions for a synthetic ball centre and two face points.
    scene = np.array([[-0.42, 0.17, 1.0], [0.32, -0.21, 1.0], [0.47, 0.23, 1.0]])
    pixels, _ = cv.projectPoints(scene, np.zeros(3), np.zeros(3), MATRIX, DISTORTION)
    rays = calibrated_pixel_rays(fit, pixels.reshape(-1, 2), image_size=SIZE)
    expected = scene / np.linalg.norm(scene, axis=1, keepdims=True)
    np.testing.assert_allclose(rays, expected, atol=0.021)
