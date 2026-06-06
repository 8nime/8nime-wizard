#!/usr/bin/env python3
"""Assemble the 8nime anime build headlessly and zip it.

Produces the build zip (addons/ + userdata/) that the 8nime Wizard downloads
and extracts. No running Kodi required: builds a fresh Kodi profile directory
from the pinned addon URLs + repo config, applies the Bingie->anime skin
patches, then zips it. Runs in CI (ubuntu) or locally.

    build-anime.py --out dist/8nime-2026.06.06.zip --version 2026.06.06 \
                   [--helper-src ../8nime-bingie-helper]

The manual deploy-windows.py / apply-anime-bingie.py scripts ran against a live
Kodi profile by hand. This does the same work with zero manual steps:
  * downloads every addon/module from the pinned URLs (deploy-windows.ADDON_ZIPS)
  * stages the wizard (real raw URLs, AUTOINSTALL/AUTOUPDATE on)
  * seeds userdata (guisettings -> skin.bingie, advancedsettings, sources)
  * runs apply-anime-bingie.apply(verify_live=False) for the skin/anime patches
  * zips addons/ + userdata/ (no packages cache, no Addons33.db — Kodi rebuilds
    it and enables addons on first scan after the wizard wipes+extracts)
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import socket
import sys
import tempfile
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# urllib.request.urlretrieve has NO default timeout — a single stalled connection
# blocks the whole build forever. A process-wide socket timeout makes stalled
# reads fail (and retry) instead of hanging. This also covers the urlretrieve
# calls inside apply-anime-bingie (same process).
DOWNLOAD_TIMEOUT = 45
DOWNLOAD_RETRIES = 3
DOWNLOAD_WORKERS = 8
socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
HELPER_ID = "plugin.video.8nime.bingie.helper"
WIZARD_ID = "plugin.program.8nime.wizard"

# Minimal Kodi 21 (Omega) guisettings seed. patch_guisettings normalises the
# skin + unknownsources entries; we just need the file to exist with the keys.
GUISETTINGS_SEED = """<settings version="2">
    <setting id="lookandfeel.skin">skin.bingie</setting>
    <setting id="lookandfeel.skintheme" default="true">SKINDEFAULT</setting>
    <setting id="addons.unknownsources">true</setting>
</settings>
"""


def _load(modname: str, filename: str):
    spec = importlib.util.spec_from_file_location(modname, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


deploy = _load("deploy_windows", "deploy-windows.py")
anime = _load("apply_anime_bingie", "apply-anime-bingie.py")


def _valid_zip(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        with zipfile.ZipFile(path) as zf:
            return zf.testzip() is None
    except zipfile.BadZipFile:
        return False


def _fetch(url: str, cache_dir: Path):
    """Download url into cache_dir (reused if already valid). Returns (url, path|None, status)."""
    dest = cache_dir / url.rsplit("/", 1)[-1]
    if _valid_zip(dest):
        return url, dest, "cached"
    last = ""
    for _ in range(DOWNLOAD_RETRIES):
        try:
            part = dest.with_name(dest.name + ".part")
            urllib.request.urlretrieve(url, part)
            part.replace(dest)
            if _valid_zip(dest):
                return url, dest, "downloaded"
            last = "corrupt zip"
        except Exception as exc:  # noqa: BLE001
            last = str(exc)
    return url, None, last


def stage_addons(addons_dir: Path, packages_dir: Path, cache_dir: Path) -> list[str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    urls = deploy.ADDON_ZIPS + deploy.MODULE_ZIPS

    # Parallel downloads — the bottleneck is ~32 zips over slow hosts, not CPU.
    results: dict[str, Path] = {}
    with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as ex:
        for url, dest, status in ex.map(lambda u: _fetch(u, cache_dir), urls):
            if dest is None:
                raise SystemExit(f"Required addon download failed: {url} ({status})")
            print(f"  [{status}] {dest.name}")
            results[url] = dest

    installed: list[str] = []
    for url in urls:
        dest = results[url]
        shutil.copy2(dest, packages_dir / dest.name)
        try:
            installed.extend(deploy.extract_addon_zip(dest, addons_dir))
        except zipfile.BadZipFile as exc:
            raise SystemExit(f"Bad zip {dest.name}: {exc}")
    return installed


HELPER_IGNORE = shutil.ignore_patterns(
    ".git", ".github", "tests", "dist", "__pycache__", "*.pyc",
    ".gitignore", "requirements-dev.txt", ".releaserc.json", ".releaserc",
)


def stage_helper(helper_src: Path, staging: Path) -> Path:
    """Copy the helper addon minus dev files, so the shipped addon is clean."""
    dest = staging / HELPER_ID
    shutil.copytree(helper_src, dest, ignore=HELPER_IGNORE)
    return dest


def stage_wizard(addons_dir: Path) -> None:
    src = ROOT / "wizard" / WIZARD_ID
    dest = addons_dir / WIZARD_ID
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    deploy.sync_hosted_configs(dest)
    # Keep the shipped uservar (real raw URLs, AUTOINSTALL/AUTOUPDATE/ENABLE=Yes).
    # patch_uservar_local is a dev-only override and is intentionally NOT used.


def write_userdata(userdata: Path) -> None:
    userdata.mkdir(parents=True, exist_ok=True)
    (userdata / "guisettings.xml").write_text(GUISETTINGS_SEED, encoding="utf-8")
    deploy.patch_guisettings(userdata)

    adv = ROOT / "config" / "advancedsettings" / "anime-streaming.xml"
    if adv.exists():
        shutil.copy2(adv, userdata / "advancedsettings.xml")
        print("  -> userdata/advancedsettings.xml")

    deploy.write_sources(userdata)


def set_build_version(userdata: Path, version: str) -> None:
    """Stamp the wizard's recorded build version so it doesn't show a phantom
    update (apply-anime-bingie.write_wizard_settings hardcodes 1.0.0)."""
    settings = userdata / "addon_data" / WIZARD_ID / "settings.xml"
    if not settings.exists():
        return
    text = settings.read_text(encoding="utf-8")
    text = re.sub(
        r'(<setting id="buildversion"[^>]*>)[^<]*(</setting>)',
        rf"\g<1>{version}\g<2>",
        text,
    )
    settings.write_text(text, encoding="utf-8")


def zip_build(kodi_home: Path, out_zip: Path) -> Path:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    if out_zip.exists():
        out_zip.unlink()
    count = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for base in ("addons", "userdata"):
            root = kodi_home / base
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(kodi_home).as_posix())
                    count += 1
    print(f"  zipped {count} files")
    return out_zip


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble the 8nime anime build zip.")
    ap.add_argument("--out", required=True, help="output zip path")
    ap.add_argument("--version", default="dev", help="build version (e.g. 2026.06.06)")
    ap.add_argument("--helper-src", default=None,
                    help="path to the 8nime-bingie-helper checkout (default: sibling dir)")
    ap.add_argument("--cache-dir", default=None,
                    help="persistent dir to cache addon downloads (reused across CI runs)")
    args = ap.parse_args()

    helper_src = Path(args.helper_src) if args.helper_src else (ROOT.parent / "8nime-bingie-helper")
    helper_src = helper_src.resolve()
    if not (helper_src / "addon.xml").exists():
        raise SystemExit(f"AniList helper source not found (need addon.xml): {helper_src}")

    with tempfile.TemporaryDirectory() as tmp:
        kodi_home = Path(tmp) / "kodi"
        addons_dir = kodi_home / "addons"
        packages_dir = addons_dir / "packages"
        userdata = kodi_home / "userdata"
        addons_dir.mkdir(parents=True)
        packages_dir.mkdir(parents=True)

        # apply-anime-bingie copies ANILIST_HELPER_SRC into the profile; point it
        # at a clean staged copy of the helper checkout (no .git/tests/dev files).
        anime.ANILIST_HELPER_SRC = stage_helper(helper_src, Path(tmp) / "_helper")

        cache_dir = Path(args.cache_dir).resolve() if args.cache_dir else (Path(tmp) / "_cache")

        print(f"Assembling 8nime build v{args.version}")
        print(f"\n[1/6] Downloading addons + modules (parallel x{DOWNLOAD_WORKERS})...")
        stage_addons(addons_dir, packages_dir, cache_dir)
        print("\n[2/6] Staging wizard...")
        stage_wizard(addons_dir)
        print("\n[3/6] Seeding userdata...")
        write_userdata(userdata)
        print("\n[4/6] Applying anime skin patches + branding...")
        anime.apply(kodi_home, verify_live=False)
        set_build_version(userdata, args.version)
        print("\n[5/6] Pruning download cache...")
        shutil.rmtree(packages_dir, ignore_errors=True)
        print("\n[6/6] Zipping build...")
        out = zip_build(kodi_home, Path(args.out))

    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"\nBuild written: {out} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
