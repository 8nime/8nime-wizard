#!/usr/bin/env python3
"""Build the 8nime build zip locally and install it into a local Kodi profile.

Fast validation loop — no CI, no release, no waiting. It assembles the zip from
your LOCAL helper checkout (so uncommitted helper changes are included) and the
wizard/config working tree, then installs it into the Kodi profile exactly like
the wizard does on a fresh build (wipe addons/ + userdata/, extract). Nothing is
hand-edited; this is the scripted install path.

  # Kodi MUST be fully closed first (Windows file locks).
  python3 scripts/install-local-build.py                 # build + clean install
  python3 scripts/install-local-build.py --no-build      # reuse dist/8nime.zip
  python3 scripts/install-local-build.py --keep          # overlay (no wipe)
  python3 scripts/install-local-build.py --reset-only     # factory reset, no install

Defaults: Kodi home = the WSL mount of the Windows Kodi profile; helper checkout
= ../8nime-bingie-helper. Override with --kodi-home / --helper-src.
"""
import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KODI = Path(
    "/mnt/c/Users/bruno/AppData/Local/Packages/"
    "XBMCFoundation.Kodi_4n2hpmxwrvr6p/LocalCache/Roaming/Kodi"
)
DEFAULT_HELPER = ROOT.parent / "8nime-bingie-helper"
# These live in the Roaming profile and are safe to wipe — Kodi's bundled system
# addons live in the install/app package dir, not here, and are not touched.
WIPE_DIRS = ("addons", "userdata")


def _kodi_locked(kodi: Path) -> bool:
    """Best-effort: a live Kodi keeps an exclusive handle on this lock file."""
    lock = kodi / ".kodi_lock"  # not authoritative on Windows-via-WSL; advisory
    return lock.exists()


def main() -> int:
    ap = argparse.ArgumentParser(description="Build + install the 8nime build locally.")
    ap.add_argument("--kodi-home", default=str(DEFAULT_KODI))
    ap.add_argument("--helper-src", default=str(DEFAULT_HELPER))
    ap.add_argument("--zip", default=str(ROOT / "dist" / "8nime.zip"))
    ap.add_argument("--no-build", action="store_true", help="reuse the existing zip")
    ap.add_argument("--keep", action="store_true", help="overlay install (do NOT wipe)")
    ap.add_argument("--reset-only", action="store_true", help="factory reset, skip install")
    args = ap.parse_args()

    kodi = Path(args.kodi_home)
    zip_path = Path(args.zip)
    if not kodi.exists():
        sys.exit("Kodi home not found: %s (pass --kodi-home)" % kodi)

    if not args.reset_only and not args.no_build:
        print("[build] assembling %s from local sources..." % zip_path.name)
        subprocess.check_call([
            sys.executable, str(ROOT / "scripts" / "build-anime.py"),
            "--out", str(zip_path),
            "--version", "dev-local",
            "--helper-src", args.helper_src,
            "--cache-dir", str(ROOT / ".cache" / "packages"),
        ])

    if not args.keep:
        print("[reset] wiping %s ..." % ", ".join(WIPE_DIRS))
        for sub in WIPE_DIRS:
            shutil.rmtree(kodi / sub, ignore_errors=True)

    if args.reset_only:
        print("Factory reset done. Start Kodi for a vanilla profile.")
        return 0

    if not zip_path.exists():
        sys.exit("zip not found: %s (drop --no-build to build it)" % zip_path)

    print("[install] extracting build into %s ..." % kodi)
    with zipfile.ZipFile(zip_path) as zf:
        if zf.testzip() is not None:
            sys.exit("corrupt zip: %s" % zip_path)
        zf.extractall(kodi)

    print("Done. Start Kodi to test the build (it comes up fully enabled).")
    print("If Kodi was open during this, close it and re-run — file locks corrupt the extract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
