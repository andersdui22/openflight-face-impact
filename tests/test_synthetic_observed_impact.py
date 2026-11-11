"""Known synthetic pixels through ball, face pose and contact geometry."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.synthetic_observed_impact import calculate_synthetic_observed_impact

SIZE = (640, 400)
RADIUS_MM = 21.35
LANDMARKS = np.array([[-44, -19], [42, -17], [36, 22], [-35, 18], [8, 12], [-9, -4]])
POLYGON = SyntheticFacePolygon(
    np.array([[-45.0, -25.0], [45.0, -25.0], [45.0, 25.0], [-45.0, 25.0]])
)
RIM_ANGLES = np.array([0, 0.34, 0.93, 1.61, 2.57, 3.02, 3.84, 4.96, 5.71])


@pytest.fixture
def calibration():
    return CheckerboardCalibration(
        SIZE,
        np.array([[530.0, 0, 315.0], [0, 525.0, 198.0], [0, 0, 1]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.01]),
        0.0,
        (),
    )


def project(calibration, points):
    image, _ = cv.projectPoints(
        np.asarray(points, dtype=float),
        np.zeros(3),
        np.zeros(3),
        calibration.camera_matrix,
        calibration.distortion,
    )
    return image.reshape(-1, 2)


def synthetic_pixels(
    calibration,
    local_ball,
    *,
    tilt=(0.29, -0.32, 0.2),
    translation=(64.0, -22.0, 420.0),
    rim_angles=RIM_ANGLES,
):
    tilt_rotation, _ = cv.Rodrigues(np.array(tilt, dtype=float))
    rotation = tilt_rotation @ np.diag([1.0, -1.0, -1.0])
    translation = np.array(translation)
    face_points = np.column_stack((LANDMARKS, np.zeros(len(LANDMARKS))))
    face_pixels = project(calibration, face_points @ rotation.T + translation)

    ball_center = rotation @ local_ball + translation
    direction = ball_center / np.linalg.norm(ball_center)
    transverse = np.cross(direction, [0.0, 1.0, 0.0])
    transverse /= np.linalg.norm(transverse)
    vertical = np.cross(direction, transverse)
    ratio = RADIUS_MM / np.linalg.norm(ball_center)
    ring_center = ball_center * (1.0 - ratio**2)
    ring_radius = RADIUS_MM * np.sqrt(1.0 - ratio**2)
    ring = ring_center + ring_radius * (
        np.cos(rim_angles)[:, None] * transverse + np.sin(rim_angles)[:, None] * vertical
    )
    return project(calibration, ring), face_pixels


def impact(
    calibration,
    ball_pixels,
    face_pixels,
    *,
    size=SIZE,
    landmarks=LANDMARKS,
    polygon=POLYGON,
    margin=0.1,
):
    return calculate_synthetic_observed_impact(
        calibration,
        ball_pixels,
        landmarks,
        face_pixels,
        polygon,
        image_size=size,
        ball_radius_mm=RADIUS_MM,
        max_ball_residual_rad=1e-6,
        max_face_rms_px=0.5,
        min_face_margin_px=margin,
        contact_tolerance_mm=0.01,
    )


@pytest.mark.parametrize(
    ("local", "region", "vertical"),
    [
        ([12.0, 5.0, RADIUS_MM], "toe", "high"),
        ([-13.0, -7.0, RADIUS_MM], "heel", "low"),
    ],
)
def test_recovers_known_signed_contact_in_millimetres(calibration, local, region, vertical):
    ball_pixels, face_pixels = synthetic_pixels(calibration, local)
    result = impact(calibration, ball_pixels, face_pixels)
    assert result.status is SyntheticImpactStatus.OK
    assert result.x_mm == pytest.approx(local[0], abs=0.01)
    assert result.y_mm == pytest.approx(local[1], abs=0.01)
    assert result.horizontal_region == region
    assert result.vertical_region == vertical
    assert result.rejection_reason is None


@pytest.mark.parametrize(
    ("local", "status"),
    [
        ([10.0, 0.0, RADIUS_MM + 4.0], SyntheticImpactStatus.NO_TANGENCY),
        ([55.0, 0.0, RADIUS_MM], SyntheticImpactStatus.OUTSIDE_FACE),
    ],
)
def test_separation_and_polygon_exclusion_have_no_contact_coordinates(
    calibration,
    local,
    status,
):
    ball_pixels, face_pixels = synthetic_pixels(calibration, local)
    result = impact(calibration, ball_pixels, face_pixels)
    assert result.status is status
    assert result.x_mm is None and result.y_mm is None
    assert result.horizontal_region is None and result.vertical_region is None
    assert result.rejection_reason


def test_partial_ball_rim_is_rejected(calibration):
    ball_pixels, face_pixels = synthetic_pixels(
        calibration,
        np.array([10.0, 0.0, RADIUS_MM]),
        rim_angles=np.linspace(-0.8, 0.8, 8),
    )
    result = impact(calibration, ball_pixels, face_pixels)
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "more than half" in result.rejection_reason
    assert result.x_mm is None and result.y_mm is None


def test_ambiguous_face_pose_is_rejected(calibration):
    ball_pixels, face_pixels = synthetic_pixels(
        calibration,
        np.array([10.0, 0.0, RADIUS_MM]),
        tilt=(0.10, 0.08, 0.1),
        translation=(0.0, 0.0, 1800.0),
    )
    result = impact(calibration, ball_pixels, face_pixels)
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "ambiguous" in result.rejection_reason
    assert result.x_mm is None and result.y_mm is None


def test_mismatched_calibration_size_is_rejected(calibration):
    ball_pixels, face_pixels = synthetic_pixels(calibration, [10.0, 0.0, RADIUS_MM])
    result = impact(calibration, ball_pixels, face_pixels, size=(320, 200))
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "dimensions" in result.rejection_reason
    assert result.x_mm is None and result.y_mm is None


def test_invalid_polygon_is_rejected_by_existing_contact_pipeline(calibration):
    ball_pixels, face_pixels = synthetic_pixels(calibration, [10.0, 0.0, RADIUS_MM])
    polygon = SyntheticFacePolygon(np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]]))
    result = impact(calibration, ball_pixels, face_pixels, polygon=polygon)
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "polygon" in result.rejection_reason
    assert result.x_mm is None and result.y_mm is None


def test_gate20_clipped_ball_contour_fails_before_geometry(calibration):
    ball_pixels, face_pixels = synthetic_pixels(calibration, [10., 0., RADIUS_MM])
    ball_pixels[0] = [0., 50.]
    result = calculate_synthetic_observed_impact(
        calibration, ball_pixels, LANDMARKS, face_pixels, POLYGON,
        image_size=SIZE, ball_radius_mm=RADIUS_MM,
        max_ball_residual_rad=1e-6, max_face_rms_px=0.5,
        min_face_margin_px=0.1, contact_tolerance_mm=0.01,
        ball_border_margin_px=2.,
    )
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "border margin" in result.rejection_reason
    assert result.x_mm is None and result.y_mm is None


def test_gate20_valid_contour_integrates_with_observed_impact(calibration):
    ball_pixels, face_pixels = synthetic_pixels(calibration, [12., 5., RADIUS_MM])
    result = calculate_synthetic_observed_impact(
        calibration, ball_pixels, LANDMARKS, face_pixels, POLYGON,
        image_size=SIZE, ball_radius_mm=RADIUS_MM,
        max_ball_residual_rad=1e-6, max_face_rms_px=0.5,
        min_face_margin_px=0.1, contact_tolerance_mm=0.01,
        ball_border_margin_px=1.,
    )
    assert result.status is SyntheticImpactStatus.OK
    assert result.x_mm == pytest.approx(12., abs=0.01)


def test_gate22_timing_provenance_allows_explicit_synthetic_candidate(calibration):
    from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture

    ball_pixels, face_pixels = synthetic_pixels(calibration, [12., 5., RADIUS_MM])
    frame = lambda sensor, host: CameraFrame(np.zeros((2, 2), dtype=np.uint8), sensor, host, 100, 1.)
    capture = TriggeredCapture(
        frames=(frame(100, 1000), frame(200, 2000), frame(300, 3000)),
        pre_trigger_count=2, trigger_host_timestamp_ns=2500,
        shot_id="shot-1", session_id="session-1",
    )
    options = dict(
        image_size=SIZE, ball_radius_mm=RADIUS_MM,
        max_ball_residual_rad=1e-6, max_face_rms_px=0.5,
        min_face_margin_px=0.1, contact_tolerance_mm=0.01,
    )
    accepted = calculate_synthetic_observed_impact(
        calibration, ball_pixels, LANDMARKS, face_pixels, POLYGON,
        capture=capture, candidate_frame_index=2, **options,
    )
    assert accepted.status is SyntheticImpactStatus.OK
    rejected = calculate_synthetic_observed_impact(
        calibration, ball_pixels, LANDMARKS, face_pixels, POLYGON,
        capture=capture, candidate_frame_index=3, **options,
    )
    assert rejected.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert rejected.x_mm is None and rejected.y_mm is None
    assert "candidate frame index" in rejected.rejection_reason
    missing = calculate_synthetic_observed_impact(
        calibration, ball_pixels, LANDMARKS, face_pixels, POLYGON,
        candidate_frame_index=2, **options,
    )
    assert missing.status is SyntheticImpactStatus.INVALID_GEOMETRY
