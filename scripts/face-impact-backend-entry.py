"""PyInstaller entry point for the development-only Windows mock backend."""

import json
import sys

from openflight.server import main

if __name__ == "__main__":
    if sys.argv[1:2] == ["--offline-recording"]:
        from openflight.camera.offline_recording_cli import main as recording_main

        del sys.argv[1]
        recording_main()
    elif sys.argv[1:] == ["--media-foundation-inventory"]:
        from openflight.camera.windows_media_foundation import scan_devices

        print(json.dumps({"devices": scan_devices()}))
    elif sys.argv[1:] == ["--media-foundation-mode-contract"]:
        from openflight.camera.windows_media_foundation import validated_mode

        print(json.dumps([validated_mode(mode, 11).settings() for mode in json.load(sys.stdin)]))
    else:
        main()
