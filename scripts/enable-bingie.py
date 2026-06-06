#!/usr/bin/env python3
"""Re-enable Bingie skin after troubleshooting."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "scripts" / "deploy-windows.py"

spec = importlib.util.spec_from_file_location("deploy_windows", DEPLOY)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def enable_bingie(kodi_home: Path | None = None) -> None:
    kodi_home = kodi_home or deploy.find_kodi_home()
    if not kodi_home:
        raise SystemExit("Kodi profile not found.")

    gui = kodi_home / "userdata" / "guisettings.xml"
    if not gui.exists():
        raise SystemExit(f"guisettings.xml not found: {gui}")

    text = gui.read_text(encoding="utf-8", errors="replace")
    text = re.sub(
        r'<setting id="lookandfeel\.skin"[^>]*>[^<]+</setting>',
        '<setting id="lookandfeel.skin">skin.bingie</setting>',
        text,
    )
    gui.write_text(text, encoding="utf-8")

    marker = kodi_home / "8NIME_BINGIE_DISABLED.txt"
    if marker.exists():
        marker.unlink()

    print(f"Bingie enabled -> skin.bingie ({kodi_home})")
    print("Restart Kodi. If home is blank, run: python3 scripts/fix-deps.py")


if __name__ == "__main__":
    enable_bingie()
