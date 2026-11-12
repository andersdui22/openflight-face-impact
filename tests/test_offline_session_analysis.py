"""Verify statistics and diagnostics with real synthetic replay evidence."""

from copy import deepcopy

import pytest

from openflight.camera.offline_session_analysis import analyze_offline_session
from openflight.camera.offline_session_archive import OfflineSessionArchive
from openflight.camera.synthetic_offline_impact_demo import publish_synthetic_offline_impact_demo


@pytest.fixture
def session(tmp_path):
    archive = OfflineSessionArchive(tmp_path / "shots.sqlite3")
    for case in ("contact", "missing-ball"):
        publish_synthetic_offline_impact_demo(
            case, lambda *_args, **_kw: None, recipient="local", save=archive.save,
        )
    return archive.load("synthetic-offline-demo-v1")


def test_statistics_group_clubs_and_calculate_two_axis_dispersion(session):
    accepted, _ = session["shots"]
    accepted["evidence"].update(x_mm=0.0, y_mm=2.0)
    second = deepcopy(accepted)
    second["evidence"].update(shot_id="second", x_mm=4.0, y_mm=8.0)
    other_club = deepcopy(accepted)
    other_club["evidence"]["shot_id"] = "other"
    other_club["provenance"]["club"]["model_id"] = "other-synthetic-model"
    session["shots"].extend([second, other_club])

    report = analyze_offline_session(session)
    first, other = report["clubs"]
    assert first["points_mm"] == [[0.0, 2.0], [4.0, 8.0]]
    assert first["mean_mm"] == [2.0, 5.0]
    assert first["spread_mm"] == [2.0, 3.0]
    assert first["rejected_count"] == 1
    assert other["mean_mm"] == [0.0, 2.0]
    assert other["spread_mm"] is None
    diagnostic = report["diagnostics"][0]
    assert diagnostic["status"] == "accepted"
    assert diagnostic["sensor_gap_ns"] == diagnostic["host_gap_ns"] == [8_000_000, 8_000_000]
    assert len(diagnostic["frames"]) == 2
    assert diagnostic["calibration"]["id"] == "synthetic-brown-five-v1"


@pytest.mark.parametrize(("part", "key", "value", "reason"), [
    ("quality", "preflight", {}, "missing or malformed"),
    ("calibration", "camera_matrix", [[0, 0, 0]] * 3, "calibration"),
    ("capture", "trigger_host_timestamp_ns", 0, "trigger"),
    ("capture", "sha256", None, "fingerprints"),
    ("calculation", "version", None, "calculation"),
    ("evidence", "x_mm", 500, "impact location"),
    ("evidence", "physically_validated", True, "physical"),
    ("evidence", "session_id", "different", "session identity"),
])
def test_invalid_rows_are_excluded_but_other_shots_remain(session, part, key, value, reason):
    accepted, rejected = session["shots"]
    target = accepted if part == "evidence" else accepted["provenance"]
    target[part][key] = value
    report = analyze_offline_session(session)
    assert report["evidence"] == [rejected["evidence"]]
    assert report["clubs"][0]["points_mm"] == []
    assert report["clubs"][0]["mean_mm"] is None
    invalid, valid = report["diagnostics"]
    assert invalid["status"] == "invalid"
    assert reason in invalid["reason"]
    assert valid["status"] == "rejected"


def test_conflicting_geometry_for_same_club_is_excluded(session):
    accepted, rejected = session["shots"]
    rejected["provenance"]["club"]["outline_mm"][0][0] += 1
    report = analyze_offline_session(session)
    assert not report["clubs"] and not report["evidence"]
    assert all(item["status"] == "invalid" for item in report["diagnostics"])
    assert accepted["evidence"]["accepted"] is True
