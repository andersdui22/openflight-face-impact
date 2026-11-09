"""Run the Windows launcher twice with the real Electron renderer in CI."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_PACKAGE = ROOT / "ui" / "package.json"


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def wait_for_debugger(proc: subprocess.Popen, port: int) -> None:
    deadline = time.monotonic() + 65
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Launcher exited before Electron became ready ({proc.returncode})")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1) as reply:
                if "Electron/" in json.load(reply).get("User-Agent", ""):
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.25)
    raise TimeoutError("Electron debugging endpoint did not become ready")


def check_launch(env: dict[str, str], port: int, debug_port: int) -> None:
    app_url = f"http://127.0.0.1:{port}/"
    with tempfile.TemporaryFile(mode="w+b") as output:
        proc = subprocess.Popen(
            ["node", "scripts/windows-bootstrap.mjs"],
            cwd=ROOT,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        try:
            wait_for_debugger(proc, debug_port)
            with urllib.request.urlopen(app_url + "api/camera/usb/status", timeout=3) as reply:
                if json.load(reply) != {"enabled": False, "state": "disabled"}:
                    raise RuntimeError("USB acquisition must be disabled during the smoke test")
            subprocess.run(
                ["node", "tests/windows_electron_renderer_smoke.mjs", str(debug_port), app_url],
                cwd=ROOT,
                check=True,
                timeout=65,
            )
            if proc.wait(timeout=20) != 0:
                raise RuntimeError(f"Launcher exited with status {proc.returncode} after window close")
            with socket.socket() as probe:
                probe.settimeout(2)
                if probe.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("Python backend still listens after Electron closed")
        finally:
            if proc.poll() is None:
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                proc.wait(timeout=10)
            output.seek(0)
            print(output.read().decode("utf-8", errors="replace")[-8000:])


def main() -> None:
    if os.name != "nt":
        raise RuntimeError("This smoke test is intended for Windows CI only")
    # Append an Electron inspection flag for this isolated checkout only.
    original = UI_PACKAGE.read_bytes()
    package = json.loads(original)
    with tempfile.TemporaryDirectory(prefix="openflight-win-smoke-") as directory:
        port = free_port()
        debug_port = free_port()
        while debug_port == port:
            debug_port = free_port()
        env = os.environ.copy()
        env.pop("OPENFLIGHT_USB_CAMERA_INDEX", None)
        env["OPENFLIGHT_WEB_PORT"] = str(port)
        env["OPENFLIGHT_PYTHON"] = sys.executable
        env["OPENFLIGHT_STARTUP_TIMEOUT_MS"] = "45000"
        env["OPENFLIGHT_PROFILES_PATH"] = str(Path(directory) / "profiles.json")
        package["scripts"]["electron"] += (
            f' --remote-debugging-address=127.0.0.1 --remote-debugging-port={debug_port}'
            f' --user-data-dir="{Path(directory) / "electron"}"'
        )
        try:
            UI_PACKAGE.write_text(json.dumps(package), encoding="utf-8")
            check_launch(env, port, debug_port)
            check_launch(env, port, debug_port)
        finally:
            UI_PACKAGE.write_bytes(original)
    print("OpenFlight released the Python port and restarted successfully")


if __name__ == "__main__":
    main()
