"""Gate 18: synthetic club model metadata and provenance guards."""

import pytest

from openflight.camera.club_face_model import ClubFaceModel, ClubFamily, FaceSurface


@pytest.mark.parametrize("family", list(ClubFamily))
def test_every_family_starts_with_unknown_geometry(family):
    model = ClubFaceModel(family, f"unknown:{family.value}")
    assert model.surface is FaceSurface.UNKNOWN
    assert model.width_mm is None
    assert model.height_mm is None
    assert model.geometry_known is False


def test_sourced_curved_wood_geometry_is_explicit():
    model = ClubFaceModel(
        ClubFamily.WOOD, "synthetic-wood", FaceSurface.CURVED,
        width_mm=76.0, height_mm=36.0, bulge_radius_mm=260.0,
        roll_radius_mm=280.0, evidence_source="synthetic-test-fixture",
    )
    assert model.geometry_known is True
    assert model.bulge_radius_mm == 260.0


def test_sourced_planar_iron_is_distinct_from_curved_wood():
    model = ClubFaceModel(
        ClubFamily.IRON, "synthetic-iron", FaceSurface.PLANAR,
        width_mm=65.0, height_mm=30.0,
        evidence_source="synthetic-test-fixture",
    )
    assert model.geometry_known is True
    assert model.bulge_radius_mm is None


@pytest.mark.parametrize("value", [0, -2, float("nan"), float("inf"), True, "50"])
def test_invalid_dimensions_rejected(value):
    with pytest.raises(ValueError, match="finite positive"):
        ClubFaceModel(
            ClubFamily.DRIVER, "invalid", FaceSurface.CURVED,
            width_mm=value, evidence_source="synthetic-test-fixture",
        )


def test_unsourced_dimensions_rejected():
    with pytest.raises(ValueError, match="provenance"):
        ClubFaceModel(
            ClubFamily.WEDGE, "unknown-wedge", FaceSurface.PLANAR,
            width_mm=55.0,
        )


def test_bulge_roll_cannot_be_applied_to_planar_or_unknown():
    for surface in (FaceSurface.PLANAR, FaceSurface.UNKNOWN):
        with pytest.raises(ValueError, match="curved"):
            ClubFaceModel(
                ClubFamily.IRON, "invalid", surface,
                bulge_radius_mm=300.0,
                evidence_source="synthetic-test-fixture",
            )


def test_invalid_family_and_model_identity_rejected():
    with pytest.raises(ValueError, match="family"):
        ClubFaceModel("putter", "not-supported")
    with pytest.raises(ValueError, match="identity"):
        ClubFaceModel(ClubFamily.WEDGE, " ")
