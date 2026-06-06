#!/usr/bin/env python3
"""Remove 8nime/Bingie build; keep only repository addons."""

from __future__ import annotations

import importlib.util
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "scripts" / "deploy-windows.py"

spec = importlib.util.spec_from_file_location("deploy_windows", DEPLOY)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)

# Repositories to keep
KEEP_ADDONS = {
    "repository.bingie",
    "repository.hooty",
    # Kodi stock addons (Microsoft Store install)
    "metadata.album.universal",
    "metadata.artists.universal",
    "metadata.common.fanart.tv",
    "metadata.generic.albums",
    "metadata.themoviedb.org.python",
    "metadata.tvshows.themoviedb.org.python",
    "peripheral.joystick",
    "service.xbmc.versioncheck",
    "game.controller.snes",
}

REMOVE_ADDON_DATA = [
    "plugin.program.8nime.wizard",
    "skin.bingie",
    "plugin.video.otaku",
    "plugin.video.8nime.bingie.helper",
    "script.skinshortcuts",
    "script.bingie.widgets",
    "script.bingie.helper",
]

EMPTY_SOURCES = """<sources>
    <programs>
        <default pathversion="1"></default>
    </programs>
    <video>
        <default pathversion="1"></default>
    </video>
    <music>
        <default pathversion="1"></default>
    </music>
    <pictures>
        <default pathversion="1"></default>
    </pictures>
    <files>
        <default pathversion="1"></default>
    </files>
</sources>
"""


def reset_build(kodi_home: Path | None = None) -> None:
    kodi_home = kodi_home or deploy.find_kodi_home()
    if not kodi_home:
        raise SystemExit("Kodi profile not found.")

    addons_dir = kodi_home / "addons"
    userdata = kodi_home / "userdata"
    removed: list[str] = []

    print(f"Resetting Kodi build at {kodi_home}")
    print("Make sure Kodi is fully closed.\n")

    # Remove deployed addon folders
    for entry in sorted(addons_dir.iterdir()):
        name = entry.name
        if name in ("packages", "temp"):
            continue
        if not entry.is_dir():
            continue
        if name in KEEP_ADDONS:
            print(f"  keep  {name}")
            continue
        shutil.rmtree(entry)
        removed.append(name)
        print(f"  remove {name}")

    # Clear downloaded packages
    packages = addons_dir / "packages"
    if packages.is_dir():
        for item in packages.iterdir():
            if item.is_file():
                item.unlink()
        print("  cleared addons/packages")

    # Reset userdata configs we created
    for name in ("advancedsettings.xml", "guisettings.xml"):
        path = userdata / name
        if path.exists():
            path.unlink()
            print(f"  deleted userdata/{name} (Kodi will recreate defaults)")

    sources = userdata / "sources.xml"
    sources.write_text(EMPTY_SOURCES, encoding="utf-8")
    print("  reset userdata/sources.xml")

    # Clean addon_data
    addon_data = userdata / "addon_data"
    for name in REMOVE_ADDON_DATA:
        path = addon_data / name
        if path.exists():
            shutil.rmtree(path)
            print(f"  removed addon_data/{name}")

    # Purge removed addons from database
    db_path = userdata / "Database" / "Addons33.db"
    if db_path.exists() and removed:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        for addon_id in removed:
            cur.execute("DELETE FROM installed WHERE addonID=?", (addon_id,))
            cur.execute("DELETE FROM addons WHERE id=?", (addon_id,))
        conn.commit()
        conn.close()
        print(f"  purged {len(removed)} addon(s) from Addons33.db")

    # Remove marker files
    for marker in kodi_home.glob("8NIME_*.txt"):
        marker.unlink()
        print(f"  deleted {marker.name}")

    print("\nDone. Remaining addons:")
    for name in sorted(p.name for p in addons_dir.iterdir() if p.is_dir() and p.name not in ("packages", "temp")):
        print(f"  - {name}")

    print("\nRestart Kodi. It will boot with default Estuary skin and mouse cursor.")
    print("Install addons via: Settings -> Add-ons -> Install from repository")


if __name__ == "__main__":
    reset_build()
