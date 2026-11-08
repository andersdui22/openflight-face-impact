"""CI-only end-to-end Windows smoke of the real bootstrap and Electron.

Requires the existing backend installed, npm ci, and npm run build.
No hardware is connected; the backend is started with --mock.
"""
from __future__ import annotations

import os
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if os.name != "nt":
        raise RuntimeError("This smoke test is intended for Windows CI only")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    with tempfile.TemporaryFile(mode="w+b") as output:
        env = os.environ.copy()
        env["OPENFLIGHT_WEB_PORT"] = str(port)
        env["OPENFLIGHT_PYTHON"] = os.sys.executable
        env["OPENFLIGHT_STARTUP_TIMEOUT_MS"] = "45000"
        proc = subprocess.Popen(
            ["node", "scripts/windows-bootstrap.mjs"],
            cwd=ROOT,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        try:
            deadline = time.monotonic() + 55
            url = f"http://127.0.0.1:{port}/"
            ready = False
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError(f"Launcher exited prematurely ({proc.returncode})")
                try:
                    with urllib.request.urlopen(url, timeout=1) as response:
                        ready = response.status == 200
                        if ready:
                            body = response.read(8192).decode("utf-8", errors="replace")
                            if "<html" not in body.lower():
                                raise RuntimeError("Backend did not serve built React HTML")
                            break
                except (urllib.error.URLError, TimeoutError):
                    time.sleep(0.25)
            if not ready:
                raise TimeoutError("Combined bootstrap did not serve React within 55s")
            # A running launcher alone is insufficient; verify Electron exists.
            deadline = time.monotonic() + 15
            found_electron = False
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError(f"Launcher exited after backend ready ({proc.returncode})")
                tasklist = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq electron.exe", "/FO", "CSV", "/NH"],
                    capture_output=True, text=True, check=True,
                )
                if '"electron.exe"' in tasklist.stdout.lower():
                    found_electron = True
                    break
                time.sleep(0.5)
            if not found_electron:
                raise RuntimeError("Electron process was not observed on Windows")
            print("Windows bootstrap: Flask served React HTML and Electron process launched")
        finally:
            if proc.poll() is None:
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True, check=False,
                )
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)
            output.seek(0)
            print(output.read().decode("utf-8", errors="replace")[-8000:])


if __name__ == "__main__":
    main()
