"""PyInstaller entry point for the development-only Windows mock backend."""

import sys

from openflight.server import main

if __name__ == "__main__":
    if sys.argv[1:2] == ["--offline-recording"]:
        from openflight.camera.offline_recording_cli import main as recording_main

        del sys.argv[1]
        recording_main()
    else:
        main()
