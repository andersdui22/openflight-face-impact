"""Persistent trusted fixture receipts and separately imported raster ZIPs."""

import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import numpy as np

from .calibration_club_binding import CalibrationClubBinding
from .calibration_profile import CameraCalibrationProfile
from .club_face_model import ClubFaceModel, ClubFamily, FaceSurface
from .offline_capture_recording import load_offline_capture, save_offline_capture
from .offline_marker_runner import analyze_marker_observed_offline_capture
from .offline_recorded_replay import (
    RecordedCaptureAdmission,
    RecordedReplayRejected,
    prepare_recorded_replay,
)
from .synthetic_face_polygon import SyntheticFacePolygon
from .synthetic_offline_impact_demo import publish_synthetic_offline_impact_demo

MAX_IMPORT_BYTES = 2 * 1024 * 1024
FIXTURE_CASES = ("contact", "heel-contact", "compact-contact", "missing-markers", "ambiguous-contact")


class OfflineRecordingRegister:
    """Use the archive's SQLite transaction boundary; imports never create receipts."""

    def __init__(self, archive):
        self.archive = archive

    @staticmethod
    def _schema(connection):
        connection.execute("""
            CREATE TABLE IF NOT EXISTS offline_recording_receipts (
                zip_sha TEXT PRIMARY KEY, receipt TEXT NOT NULL, receipt_sha TEXT NOT NULL, fixture_zip BLOB NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS offline_recording_imports (
                zip_sha TEXT PRIMARY KEY, imported_zip BLOB NOT NULL
            )
        """)

    def create_fixture(self, case, app_sha):
        if case not in FIXTURE_CASES:
            raise ValueError("unknown recording fixture")
        result = []

        def admit(capture, reference):
            with TemporaryDirectory() as tmp:
                path = save_offline_capture(Path(tmp), capture, app_sha=app_sha, source="synthetic_fixture")
                payload = path.read_bytes()
                digest = sha256(payload).hexdigest()
                recording = load_offline_capture(path)
            receipt = {
                "schema_version": 1, "app_sha": app_sha, "case": case, "zip_sha": digest,
                "capture_fingerprint": recording.fingerprint,
                "session_id": capture.session_id, "shot_id": capture.shot_id,
                "timing_source": "synthetic_independent_fixture_clocks", **reference,
            }
            with self.archive._connection() as db:  # pylint: disable=protected-access
                self._schema(db)
                document = json.dumps(receipt, allow_nan=False)
                cursor = db.execute("""
                    INSERT INTO offline_recording_receipts
                    SELECT ?, ?, ?, ? WHERE (SELECT COUNT(*) FROM offline_recording_receipts) < 32
                """, (digest, document, sha256(document.encode()).hexdigest(), payload))
                if not cursor.rowcount:
                    raise ValueError("local fixture register is full (32 recordings)")
            result.append(digest)

        publish_synthetic_offline_impact_demo(
            case, lambda *_args, **_kwargs: None, recipient="local-register",
            session_id=f"synthetic-recorded-{uuid4().hex}", register_fixture=admit,
        )
        return result[0]

    def _read(self, digest):
        with self.archive._connection() as db:  # pylint: disable=protected-access
            self._schema(db)
            row = db.execute("""
                SELECT receipt, fixture_zip, imported_zip, receipt_sha FROM offline_recording_receipts
                LEFT JOIN offline_recording_imports USING (zip_sha) WHERE zip_sha = ?
            """, (digest,)).fetchone()
        if row is None:
            raise ValueError("No independent receipt matches this ZIP")
        if sha256(row[0].encode()).hexdigest() != row[3]:
            raise ValueError("Independent recording receipt changed")
        receipt = json.loads(row[0])
        if receipt.get("schema_version") != 1 or receipt.get("zip_sha") != digest:
            raise ValueError("Recording receipt metadata is invalid")
        return receipt, row[1], row[2]

    @staticmethod
    def _summary(receipt):
        return {key: receipt[key] for key in (
            "zip_sha", "case", "app_sha", "capture_fingerprint", "session_id", "shot_id",
            "timing_source", "camera_identity", "camera_mode_id", "binding",
        )}

    def list_imports(self):
        with self.archive._connection() as db:  # pylint: disable=protected-access
            self._schema(db)
            rows = db.execute("""
                SELECT receipt, receipt_sha FROM offline_recording_receipts
                JOIN offline_recording_imports USING (zip_sha) ORDER BY offline_recording_imports.rowid DESC
            """).fetchall()
        return [self._summary(json.loads(document)) for document, digest in rows
                if sha256(document.encode()).hexdigest() == digest]

    def fixture_zip(self, digest):
        return self._read(digest)[1]

    def import_zip(self, payload):
        if not 0 < len(payload) <= MAX_IMPORT_BYTES:
            raise ValueError("Recording ZIP must be between 1 byte and 2 MiB")
        digest = sha256(payload).hexdigest()
        receipt, _, _ = self._read(digest)
        with self.archive._connection() as db:  # pylint: disable=protected-access
            self._schema(db)
            db.execute("INSERT OR IGNORE INTO offline_recording_imports VALUES (?, ?)", (digest, payload))
        return self._summary(receipt)

    def remove_import(self, digest):
        """Release imported bytes while retaining the receipt and saved history."""
        with self.archive._connection() as db:  # pylint: disable=protected-access
            self._schema(db)
            return bool(db.execute(
                "DELETE FROM offline_recording_imports WHERE zip_sha = ?", (digest,),
            ).rowcount)

    def replay(self, digest):
        receipt, _, payload = self._read(digest)
        if payload is None or sha256(payload).hexdigest() != digest:
            raise ValueError("Imported recording is missing or changed")
        profile = CameraCalibrationProfile.from_json(receipt["profile"])
        fields = receipt["club"]
        club = ClubFaceModel(**{**fields, "family": ClubFamily(fields["family"]),
                               "surface": FaceSurface(fields["surface"])})
        admission = RecordedCaptureAdmission(
            receipt["capture_fingerprint"], receipt["app_sha"], "synthetic_fixture",
            receipt["camera_identity"], receipt["camera_mode_id"], CalibrationClubBinding(**receipt["binding"]),
        )
        options = receipt["parameters"]
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.zip"
            path.write_bytes(payload)
            recording, preflight = prepare_recorded_replay(
                path, admission=admission, camera_identity=receipt["camera_identity"], profile=profile, club=club,
                max_sensor_gap_ns=options["max_sensor_gap_ns"], max_host_gap_ns=options["max_host_gap_ns"],
            )
        capture = recording.capture
        if (capture.session_id, capture.shot_id) != (receipt["session_id"], receipt["shot_id"]):
            raise ValueError("Recorded session or shot identity differs from receipt")
        observations = {}
        for index, raster in receipt["observations"].items():
            raw = bytes.fromhex(raster)
            if sha256(raw).hexdigest() != receipt["observation_sha256"].get(index):
                raise ValueError("Reference observation digest differs from receipt")
            observations[int(index)] = np.frombuffer(raw, dtype=np.uint8).reshape(capture.frames[0].image.shape)
        if set(observations) != set(range(len(capture.frames))):
            raise ValueError("Reference observation missing for captured frame")
        try:
            result = analyze_marker_observed_offline_capture(
                profile.calibration, capture, observations, np.asarray(receipt["reference_pixels"]),
                np.asarray(receipt["landmarks"]), SyntheticFacePolygon(np.asarray(receipt["outline"])),
                preflight=preflight, emit=lambda *_args, **_kwargs: None, recipient="local-register", **options,
            )
        except ValueError as error:
            raise RecordedReplayRejected("landmark_or_geometry", str(error)) from error
        if result["accepted"]:
            provenance = receipt["session_provenance"]
            provenance["capture"].update(acquisition="synthetic-recording-v1", recording_sha256=digest)
            provenance["quality"]["impact_status"] = "accepted"
            self.archive.save(result, provenance)
        return result
