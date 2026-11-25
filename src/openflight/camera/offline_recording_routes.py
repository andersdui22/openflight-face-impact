"""Loopback-only routes for synthetic recording admission and replay."""

import re
import sqlite3
import subprocess
import sys
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, request

from .offline_session_archive import OfflineSessionArchive

recording_routes = Blueprint("offline_recordings", __name__, url_prefix="/api/face-impact/recordings")


def _producer_sha():
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        return (Path(bundle) / "face-impact-source-sha.txt").read_text(encoding="utf-8-sig").strip()
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[3],
        text=True, timeout=3,
    ).strip()


@recording_routes.route("", defaults={"action": "imports"}, methods=["GET", "POST"])
@recording_routes.route("/<action>", methods=["GET", "POST"])
def recording_request(action):
    from .offline_recording_register import MAX_IMPORT_BYTES, OfflineRecordingRegister

    path = current_app.config.get("OFFLINE_IMPACT_ARCHIVE_PATH")
    if path is None or request.remote_addr not in ("127.0.0.1", "::1"):
        return {"error": "Local recording register unavailable"}, 404
    if request.headers.get("X-OpenFlight-Recording") != "1":
        return {"error": "Recording client header required"}, 403
    origin = request.headers.get("Origin", "")
    if origin not in ("", "null") and not re.fullmatch(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?", origin):
        return {"error": "Local recording origin required"}, 403
    register = OfflineRecordingRegister(OfflineSessionArchive(path))
    try:
        if action == "imports" and request.method == "GET":
            return jsonify(recordings=register.list_imports())
        if action == "imports" and request.method == "POST":
            if request.content_length is None or not 0 < request.content_length <= MAX_IMPORT_BYTES:
                return {"error": "Recording ZIP exceeds the 2 MiB import limit or is empty"}, 413
            return jsonify(recording=register.import_zip(request.get_data()))
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        if not isinstance(data, dict):
            return {"error": "Expected a JSON object"}, 400
        if action == "fixtures" and request.method == "POST":
            digest = register.create_fixture(data.get("case"), _producer_sha())
            return jsonify(digest=digest)
        if request.method == "GET" and re.fullmatch(r"[0-9a-f]{64}", action):
            return Response(register.fixture_zip(action), mimetype="application/zip")
        if action == "remove-import" and request.method == "POST":
            return jsonify(removed=register.remove_import(data.get("digest")))
        if action == "replay" and request.method == "POST":
            return jsonify(result=register.replay(data.get("digest")))
    except (ValueError, KeyError, TypeError) as error:
        return {"error": str(error)}, 422
    except (OSError, sqlite3.Error, subprocess.SubprocessError):
        return {"error": "Local recording storage or producer revision unavailable"}, 503
    return {"error": "Recording operation not found"}, 404
