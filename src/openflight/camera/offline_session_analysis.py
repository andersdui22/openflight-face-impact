"""Statistics and diagnostics for versioned synthetic archive evidence."""

from collections import Counter, defaultdict
from math import isfinite
from re import fullmatch
from statistics import mean, pstdev

from .offline_impact_evidence import OfflineImpactEvidence
from .offline_impact_transport import serialize_offline_impact_evidence
from .synthetic_face_polygon import contains_synthetic_face_point


def _number(value, low, high):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and low <= value <= high and isfinite(value))


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _vector(values, size, low, high):
    return (isinstance(values, list) and len(values) == size
            and all(_number(value, low, high) for value in values))


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _calibration_summary(calibration):
    size, matrix = calibration["image_size_px"], calibration["camera_matrix"]
    if (not _text(calibration["id"]) or not _vector(size, 2, 2, 65536)
            or not all(map(_integer, size))
            or not _vector(calibration["distortion"], 5, -1e4, 1e4)):
        raise ValueError("Saved calibration metadata is missing or malformed")
    if len(matrix) != 3 or not all(_vector(axis, 3, -1e7, 1e7) for axis in matrix):
        raise ValueError("Saved calibration matrix dimensions or values are invalid")
    fx, skew_x, _ = matrix[0]
    skew_y, fy, _ = matrix[1]
    if min(fx, fy) <= 0 or skew_x or skew_y or matrix[2] != [0, 0, 1]:
        raise ValueError("Saved calibration matrix has invalid focal lengths or axes")
    return {"id": calibration["id"], "image_size_px": size}


def _image_quality(frames, size):
    return all(
        [frame["width"], frame["height"]] == size
        and _number(frame["brightness_mean"], 0, 255)
        and _number(frame["contrast_span"], 5, 255)
        and _number(frame["saturated_fraction"], 0, 0.95)
        and _number(frame["dark_fraction"], 0, 0.95)
        for frame in frames
    )


def _timing(capture, limits):
    frames = capture["frames"]
    pre_count = capture["pre_trigger_count"]
    trigger = capture["trigger_host_timestamp_ns"]
    if not 2 <= len(frames) <= 512 or not _integer(pre_count) or not 0 < pre_count < len(frames):
        raise ValueError("Capture frame count or trigger boundary is invalid")
    if not _integer(trigger) or not 0 <= trigger < 2**63:
        raise ValueError("Host trigger timestamp is invalid")
    if any(not _integer(frame["exposure_us"]) or frame["exposure_us"] <= 0
           or not _number(frame["analogue_gain"], 0, 1e7) or frame["analogue_gain"] <= 0
           for frame in frames):
        raise ValueError("Saved frame exposure or gain is invalid")
    ranges = {}
    for domain in ("sensor", "host"):
        timestamps = [frame[f"{domain}_timestamp_ns"] for frame in frames]
        if any(not _integer(value) or not 0 <= value < 2**63 for value in timestamps):
            raise ValueError(f"{domain.capitalize()} timestamps are invalid")
        gaps = [after - before for before, after in zip(timestamps, timestamps[1:])]
        limit = limits[f"max_{domain}_gap_ns"]
        if not _integer(limit) or not 0 < min(gaps) <= max(gaps) <= limit < 2**63:
            raise ValueError(f"{domain.capitalize()} timestamps are out of sequence or exceed gaps")
        if domain == "host" and not timestamps[pre_count - 1] <= trigger <= timestamps[pre_count]:
            raise ValueError("Host trigger is outside the capture boundary")
        ranges[f"{domain}_gap_ns"] = [min(gaps), max(gaps)]
    return ranges


def _inspect(row, session_id):
    """Return safe evidence plus diagnostics, or a reason to exclude the row."""
    diagnostic = {"shot_id": None, "club_id": None, "status": "invalid"}
    try:
        evidence = row["evidence"]
        shot_id = evidence["shot_id"]
        if _text(shot_id):
            diagnostic["shot_id"] = shot_id
        if row["schema_version"] != 1 or evidence["session_id"] != session_id:
            raise ValueError("Saved shot schema or session identity is invalid")
        fields = ("frame_index", "x_mm", "y_mm", "horizontal_region", "vertical_region")
        typed = OfflineImpactEvidence(
            shot_id=shot_id, session_id=session_id,
            accepted_for_offline_analysis=evidence["accepted"], reason=evidence["reason"],
            physically_validated=evidence["physically_validated"],
            position_uncertainty_mm=evidence["position_uncertainty_mm"],
            **{field: evidence.get(field) for field in fields},
        )
        normalized = serialize_offline_impact_evidence(typed)
        if evidence != normalized:
            raise ValueError("Saved shot evidence is incompatible with synthetic analysis")

        provenance = row["provenance"]
        club = provenance["club"]
        club_id, outline = club["model_id"], club["outline_mm"]
        if club["kind"] != "synthetic" or not _text(club_id):
            raise ValueError("Synthetic club model is missing")
        if (not isinstance(outline, list) or not 3 <= len(outline) <= 128
                or not all(_vector(point, 2, -1000, 1000) for point in outline)):
            raise ValueError("Synthetic club outline is invalid")
        diagnostic["club_id"] = club_id
        # The shared polygon validator also checks geometry on rejected shots.
        inside = contains_synthetic_face_point(outline, [
            evidence.get("x_mm", 0), evidence.get("y_mm", 0),
        ])

        diagnostic["calibration"] = _calibration_summary(provenance["calibration"])
        size = diagnostic["calibration"]["image_size_px"]

        quality = provenance["quality"]
        capture, preflight = provenance["capture"], quality["preflight"]
        hashes = (capture["sha256"], capture["marker_raster_sha256"])
        if not all(isinstance(digest, str) and fullmatch(r"[0-9a-f]{64}", digest)
                   for digest in hashes):
            raise ValueError("Saved capture fingerprints are missing or malformed")
        frames = preflight["frame_quality"]
        if (not 2 <= len(frames) <= 512 or len(frames) != len(capture["frames"])
                or len(frames) != preflight["frame_count"] or not _image_quality(frames, size)):
            raise ValueError("Saved frame quality is incomplete or outside preflight limits")
        diagnostic["frames"] = [{key: frame[key] for key in (
            "brightness_mean", "contrast_span", "dark_fraction", "saturated_fraction",
        )} for frame in frames]
        calculation = provenance["calculation"]
        diagnostic.update(_timing(capture, calculation["parameters"]))
        if diagnostic["sensor_gap_ns"] != [preflight["min_sensor_interval_ns"],
                                            preflight["max_sensor_interval_ns"]]:
            raise ValueError("Saved preflight and sensor intervals disagree")
        status = "accepted" if typed.accepted_for_offline_analysis else "rejected"
        if (not _text(calculation["version"]) or quality["impact_status"] != status
                or (typed.accepted_for_offline_analysis
                    and (typed.frame_index >= len(frames) or not inside))):
            raise ValueError("Saved calculation status or impact location is inconsistent")
        diagnostic.update(
            status=status, reason=typed.reason, calculation_version=calculation["version"],
        )
        return diagnostic, normalized, outline
    except ValueError as error:
        diagnostic["reason"] = str(error)
    except (KeyError, TypeError, IndexError, OverflowError):
        diagnostic["reason"] = "Required saved evidence or provenance is missing or malformed"
    return diagnostic, None, None


def analyze_offline_session(session):
    """Summarize a single saved session by club, excluding invalid records."""
    session_id = session["session_id"]
    inspected = [_inspect(row, session_id) for row in session["shots"]]
    ids = Counter(diagnostic["shot_id"] for diagnostic, _, _ in inspected)
    outlines = defaultdict(set)
    for diagnostic, evidence, outline in inspected:
        if evidence is not None:
            outlines[diagnostic["club_id"]].add(tuple(map(tuple, outline)))

    clubs, evidence_rows = {}, []
    for diagnostic, evidence, outline in inspected:
        if evidence is None:
            continue
        club_id = diagnostic["club_id"]
        if ids[diagnostic["shot_id"]] != 1 or len(outlines[club_id]) != 1:
            diagnostic.update(status="invalid", reason="Conflicting shot identity or club geometry")
            continue
        group = clubs.setdefault(club_id, {"club_id": club_id, "outline_mm": outline,
                                           "points_mm": [], "rejected_count": 0})
        evidence_rows.append(evidence)
        if evidence["accepted"]:
            group["points_mm"].append([evidence["x_mm"], evidence["y_mm"]])
        else:
            group["rejected_count"] += 1

    for group in clubs.values():
        axes = list(zip(*group["points_mm"]))
        group["mean_mm"] = [mean(axis) for axis in axes] if axes else None
        group["spread_mm"] = (
            [pstdev(axis) for axis in axes] if len(group["points_mm"]) >= 2 else None
        )
    return {
        "schema_version": 1, "source": "offline_synthetic_analysis", "session_id": session_id,
        "clubs": list(clubs.values()), "evidence": evidence_rows,
        "diagnostics": [diagnostic for diagnostic, _, _ in inspected],
    }
