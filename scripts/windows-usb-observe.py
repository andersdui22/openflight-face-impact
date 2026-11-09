"""Record status from the existing OpenFlight USB capture over loopback."""

import argparse
import json
import platform
import subprocess
import time
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.request import urlopen

STATUS_URL = "http://127.0.0.1:8080/api/camera/usb/status"


def opencv_version():
    for package in ("opencv-python-headless", "opencv-python"):
        try:
            return f"{package} {version(package)}"
        except PackageNotFoundError:
            continue
    return None


def observe(seconds, write):
    start = time.monotonic()
    first = previous = None
    while True:
        with urlopen(STATUS_URL, timeout=3) as response:
            status = json.load(response)
        elapsed = time.monotonic() - start
        if not isinstance(status, dict):
            raise ValueError("USB status must be a JSON object")
        write(event="status", elapsed_s=round(elapsed, 3), status=status)
        count = status.get("frames_received")
        if status.get("enabled") is not True or status.get("state") != "running" or status.get("last_error"):
            raise RuntimeError("USB capture is not running cleanly")
        if type(count) is not int or count < 1 or (previous is not None and count <= previous):
            raise RuntimeError("USB frame counter did not advance")
        if first is None:
            first, first_elapsed = count, elapsed
        previous = count
        if elapsed - first_elapsed >= seconds:
            interval = elapsed - first_elapsed
            write(event="complete", observed_seconds=round(interval, 3),
                  frame_count_delta=count - first,
                  interval_delivered_fps=round((count - first) / interval, 2))
            return
        time.sleep(min(2, seconds - (elapsed - first_elapsed)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, choices=(10, 60), default=60)
    parser.add_argument("--index", type=int, required=True, help="Index set in the launcher")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.index < 0:
        parser.error("--index must be non-negative")

    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    with args.out.open("x", encoding="utf-8") as log:
        def write(**record):
            record["utc"] = datetime.now(timezone.utc).isoformat()
            print(json.dumps(record, allow_nan=False), file=log, flush=True)

        write(event="start", commit=sha, platform=platform.platform(), opencv=opencv_version(),
              operator_index=args.index, requested_mode={"width": 640, "height": 400, "fps": 120},
              duration_s=args.seconds, endpoint=STATUS_URL)
        print(f"Recording USB status to {args.out}", flush=True)
        try:
            observe(args.seconds, write)
        except (OSError, ValueError, RuntimeError, KeyboardInterrupt) as error:
            write(event="error", detail=str(error) or type(error).__name__)
            print(f"Stopped. Keep {args.out} and the launcher log.")
            return 1
    print(f"Completed. Keep {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
