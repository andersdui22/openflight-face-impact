"""Gate 19: fail-closed offline binding storage tests."""

import json

import pytest

from openflight.camera.calibration_club_binding import CalibrationClubBinding
from openflight.camera.calibration_club_binding_store import (
    deserialize_calibration_club_binding,
    load_calibration_club_binding,
    save_calibration_club_binding,
    serialize_calibration_club_binding,
)


def binding():
    return CalibrationClubBinding("a" * 64, "synthetic-iron", "b" * 64)


def test_binding_roundtrip_and_separate_file(tmp_path):
    destination = tmp_path / "club-binding.json"
    save_calibration_club_binding(destination, binding())
    assert load_calibration_club_binding(destination) == binding()
    assert json.loads(destination.read_text(encoding="utf-8"))["version"] == 1
    assert serialize_calibration_club_binding(binding()) == (
        serialize_calibration_club_binding(binding())
    )


@pytest.mark.parametrize("patch", [
    {"version": 2},
    {"version": True},
    {"calibration_revision": "not-a-revision"},
    {"club_geometry_revision": None},
    {"club_model_id": ""},
])
def test_invalid_stored_binding_rejected(patch):
    data = json.loads(serialize_calibration_club_binding(binding()))
    data.update(patch)
    with pytest.raises(ValueError):
        deserialize_calibration_club_binding(json.dumps(data))


def test_unknown_field_and_missing_revision_rejected():
    data = json.loads(serialize_calibration_club_binding(binding()))
    data["unrecognized"] = "unexpected"
    with pytest.raises(ValueError, match="schema"):
        deserialize_calibration_club_binding(json.dumps(data))
    data.pop("unrecognized")
    data.pop("club_geometry_revision")
    with pytest.raises(ValueError, match="schema"):
        deserialize_calibration_club_binding(json.dumps(data))


def test_invalid_json_and_missing_file_fail_closed(tmp_path):
    with pytest.raises(json.JSONDecodeError):
        deserialize_calibration_club_binding("{not-json")
    with pytest.raises(OSError):
        load_calibration_club_binding(tmp_path / "not-present.json")


def test_cannot_save_missing_geometry_revision(tmp_path):
    with pytest.raises(ValueError, match="geometry revision"):
        save_calibration_club_binding(
            tmp_path / "bad.json", CalibrationClubBinding("a" * 64, "synthetic-iron")
        )
