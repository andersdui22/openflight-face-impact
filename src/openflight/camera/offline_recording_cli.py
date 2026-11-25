"""Record or replay a controlled synthetic fixture without opening a camera."""

import argparse
import json
from pathlib import Path

from openflight.camera.offline_session_archive import OfflineSessionArchive
from openflight.camera.synthetic_offline_impact_demo import publish_synthetic_offline_impact_demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record", type=Path, metavar="DIRECTORY")
    mode.add_argument("--replay", type=Path, metavar="ZIP")
    parser.add_argument("--case", default="contact")
    parser.add_argument("--app-sha", required=True, help="Independently known recording producer SHA")
    parser.add_argument("--archive", type=Path, help="Optional local synthetic session SQLite database")
    args = parser.parse_args()
    archive = OfflineSessionArchive(args.archive) if args.archive else None
    try:
        result = publish_synthetic_offline_impact_demo(
            args.case, lambda *_args, **_kwargs: None, recipient="local-cli",
            session_id="synthetic-recording-cli-v1",
            recording_path=args.replay, recording_directory=args.record, app_sha=args.app_sha,
            save=archive.save if archive else None,
        )
    except ValueError as error:
        parser.exit(2, f"{error}\n")
    if result is None:
        parser.error("unknown synthetic fixture case")
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
