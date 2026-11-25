"""Read-only Windows Plug and Play camera inventory, independent of capture."""

import json
import os
import subprocess
import sys
from pathlib import Path

_QUERY = """
$ErrorActionPreference = 'Stop'
Get-PnpDevice -PresentOnly | Where-Object { $_.Class -in 'Camera','Image' } |
    Select-Object FriendlyName,InstanceId,Status |
    ConvertTo-Json -Compress
"""


def windows_camera_inventory():
    """List present PnP identities without mapping them to OpenCV indices."""
    if sys.platform != "win32":
        return []
    powershell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / (
        "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    command = "[Console]::OutputEncoding = [Text.UTF8Encoding]::new(); " + _QUERY
    result = subprocess.run(
        [str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, encoding="utf-8", timeout=8, check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    rows = json.loads(result.stdout) if result.stdout.strip() else []
    if isinstance(rows, dict):
        rows = [rows]
    identities = {}
    for row in rows:
        instance = row.get("InstanceId")
        if isinstance(instance, str) and instance.strip():
            identities[instance.casefold()] = {
                "identity": instance,
                "name": row.get("FriendlyName") or instance,
                "status": row.get("Status"),
                "capture_identity_verified": False,
            }
    return sorted(identities.values(), key=lambda row: (row["name"], row["identity"]))
