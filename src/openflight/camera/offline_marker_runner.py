"""Controlled marker-image adapter for the existing synthetic offline runner.

The fiducial image is an explicitly separate, labelled-reference observation.
No camera capture or physical face recognition is implied.
"""

from __future__ import annotations

import numpy as np

from .experimental_face_markers import (
    associate_markers_with_reference,
    extract_unlabelled_bright_markers,
)
from .offline_impact_runner import analyze_and_publish_offline_capture
from .synthetic_frame_candidates import SyntheticFrameCandidate


def analyze_marker_observed_offline_capture(
    calibration,
    capture,
    marker_images_by_frame,
    reference_pixels_px,
    landmarks_face_mm,
    polygon,
    *,
    max_marker_distance_px,
    marker_threshold=220,
    marker_min_area_px=5.,
    marker_max_area_px=400.,
    marker_min_circularity=0.6,
    **analysis_options,
):
    """Extract real image pixels, associate trusted labels, run offline analysis.

    All requested frame observations must be present and unambiguous. A failed
    marker association aborts before publishing; never substitute guessed
    coordinates or silently reuse a previous frame's observation.
    """
    if not isinstance(marker_images_by_frame, dict) or not marker_images_by_frame:
        raise ValueError("marker observations require nonempty frame mapping")
    if (not isinstance(reference_pixels_px, np.ndarray)
            or reference_pixels_px.ndim != 2
            or reference_pixels_px.shape[1] != 2
            or reference_pixels_px.dtype.kind not in "iuf"
            or not np.all(np.isfinite(reference_pixels_px))
            or not 3 <= len(reference_pixels_px) <= 8):
        raise ValueError("marker reference must contain 3..8 finite labelled Nx2 pixels")
    if not isinstance(max_marker_distance_px, (int, float)) or isinstance(max_marker_distance_px, bool):
        raise ValueError("marker distance budget must be numeric")
    if not callable(analysis_options.get("emit")):
        raise ValueError("marker runner requires callable emitter")
    if any(not isinstance(index, int) or isinstance(index, bool)
           for index in marker_images_by_frame):
        raise ValueError("marker frame indices must be integers")
    candidates = []
    for frame_index, image in sorted(marker_images_by_frame.items()):
        if (not isinstance(frame_index, int) or isinstance(frame_index, bool)
                or not 0 <= frame_index < len(capture.frames)):
            raise ValueError("marker frame index outside capture")
        observation = extract_unlabelled_bright_markers(
            image,
            threshold=marker_threshold,
            min_area_px=marker_min_area_px,
            max_area_px=marker_max_area_px,
            min_circularity=marker_min_circularity,
            expected_count=len(reference_pixels_px),
        )
        if observation.image_shape != capture.frames[frame_index].image.shape[:2]:
            raise ValueError("marker image dimensions differ from capture frame")
        labelled_pixels = associate_markers_with_reference(
            observation,
            reference_pixels_px,
            max_distance_px=max_marker_distance_px,
        )
        candidates.append(SyntheticFrameCandidate(frame_index, labelled_pixels))
    return analyze_and_publish_offline_capture(
        calibration, capture, tuple(candidates),
        landmarks_face_mm, polygon, **analysis_options,
    )
