"""Synthetic planar pixel-to-millimeter reference mapping.

This is a mathematical test utility, not a calibrated physical camera model.
A planar affine mapping cannot account for lens distortion or perspective.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SyntheticPlanarCalibration:
    """Affine mapping from image (column, row) pixels to planar (x, y) mm."""

    pixel_to_mm: np.ndarray

    @classmethod
    def from_references(
        cls,
        pixels: np.ndarray,
        millimeters: np.ndarray,
    ) -> SyntheticPlanarCalibration:
        """Fit a nondegenerate affine map from at least three known pairs.

        References must be Nx2, finite, with non-collinear pixel coordinates.
        For more than three points the fit must be consistent to 1e-7 mm;
        inconsistent/noisy real observations are deliberately unsupported.
        """
        px = np.asarray(pixels, dtype=float)
        mm = np.asarray(millimeters, dtype=float)
        if (
            px.ndim != 2
            or px.shape[1:] != (2,)
            or mm.shape != px.shape
            or len(px) < 3
            or not np.isfinite(px).all()
            or not np.isfinite(mm).all()
        ):
            raise ValueError("Expected at least three finite Nx2 reference pairs")
        design = np.column_stack((px, np.ones(len(px))))
        if np.linalg.matrix_rank(design) != 3:
            raise ValueError("Pixel references must not be collinear")
        fit, _, _, _ = np.linalg.lstsq(design, mm, rcond=None)
        if np.max(np.abs(design @ fit - mm)) > 1e-7:
            raise ValueError("Reference pairs do not define a consistent affine map")
        if abs(np.linalg.det(fit[:2, :])) < 1e-12:
            raise ValueError("Millimeter reference mapping is not invertible")
        return cls(pixel_to_mm=fit)

    def to_millimeters(self, pixels: np.ndarray) -> np.ndarray:
        """Map Nx2 image pixel positions to planar millimeter positions."""
        px = np.asarray(pixels, dtype=float)
        if px.ndim != 2 or px.shape[1:] != (2,) or not np.isfinite(px).all():
            raise ValueError("Expected finite Nx2 pixel positions")
        return np.column_stack((px, np.ones(len(px)))) @ self.pixel_to_mm

    def to_pixels(self, millimeters: np.ndarray) -> np.ndarray:
        """Invert the synthetic planar map for finite Nx2 millimeter positions."""
        mm = np.asarray(millimeters, dtype=float)
        if mm.ndim != 2 or mm.shape[1:] != (2,) or not np.isfinite(mm).all():
            raise ValueError("Expected finite Nx2 millimeter positions")
        inverse = np.linalg.inv(self.pixel_to_mm[:2, :])
        return (mm - self.pixel_to_mm[2, :]) @ inverse
