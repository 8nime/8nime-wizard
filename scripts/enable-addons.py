#!/usr/bin/env python3
"""Enable all 8nime addons in Kodi's Addons33.db. Close Kodi first."""

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "deploy-windows.py"
spec = importlib.util.spec_from_file_location("deploy_windows", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if __name__ == "__main__":
    home = mod.find_kodi_home()
    if not home:
        print("Kodi profile not found.")
        sys.exit(1)
    print(f"Kodi home: {home}")
    count = mod.enable_addons(home, mod.ENABLE_ADDONS)
    if count:
        print("Restart Kodi to apply.")
    else:
        print("All target addons already enabled.")
