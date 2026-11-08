"""Windows CI smoke: start the real OpenFlight mock server without hardware."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


def main() -> None:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    command = [
        sys.executable, "-m", "openflight.server",
        "--mock", "--host", "127.0.0.1", "--web-port", str(port),
    ]
    proc = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )
    try:
        deadline = time.monotonic() + 35
        url = f"http://127.0.0.1:{port}/"
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                output = proc.stderr.read().decode("utf-8", errors="replace")[-6000:]
                raise RuntimeError(f"Backend exited with {proc.returncode}: {output}")
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    print(f"Real backend responded HTTP {response.status}")
                    return
            except urllib.error.HTTPError as error:
                # An HTTP 404 is sufficient to prove the Flask server is listening.
                print(f"Real backend responded HTTP {error.code}")
                return
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(0.25)
        raise TimeoutError("Real Windows mock backend did not listen within 35s")
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        if proc.stderr:
            proc.stderr.close()


if __name__ == "__main__":
    main()
