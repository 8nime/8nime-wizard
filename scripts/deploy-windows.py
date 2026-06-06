#!/usr/bin/env python3
"""Deploy 8nime build to Windows Kodi (Microsoft Store install)."""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOWS_USER = os.environ.get("WIN_USER", "bruno")


def find_kodi_home() -> Path | None:
    """Locate the active Windows Kodi profile directory."""
    candidates: list[Path] = []

    packages = Path(f"/mnt/c/Users/{WINDOWS_USER}/AppData/Local/Packages")
    if packages.is_dir():
        for pkg in packages.glob("XBMCFoundation.Kodi_*"):
            candidates.append(pkg / "LocalCache/Roaming/Kodi")

    candidates.append(Path(f"/mnt/c/Users/{WINDOWS_USER}/AppData/Roaming/Kodi"))

    # Prefer the profile with the newest kodi.log (active instance)
    best: Path | None = None
    best_mtime = -1.0
    for path in candidates:
        if not path.is_dir():
            continue
        log = path / "kodi.log"
        mtime = log.stat().st_mtime if log.exists() else path.stat().st_mtime
        if mtime > best_mtime:
            best_mtime = mtime
            best = path
    return best

BINGIE_BASE = "https://raw.githubusercontent.com/matke-84/repository.bingie/main/omega"
HOOTY_BASE = "https://raw.githubusercontent.com/Goldenfreddy0703/repository.hooty/master"
KODI_MIRROR = "https://mirrors.kodi.tv/addons/omega"
# dEXE community repo — source for OptiKlean and WatchNixtoons2 (the box's WNT2
# 0.14.18 was installed from here; the old G-Source repo URL is dead/404).
DEXE_BASE = "https://raw.githubusercontent.com/deklica/repo.dexe/master"
# OldManJax animaniac repo — source for FANime F (plugin.video.fanimef). The Crew
# repo aggregates this datadir; Fanime is hosted here, not in The Crew's own zips.
ANIMANIAC_BASE = "https://raw.githubusercontent.com/OldManJax/repository.animaniac/master"

# Bingie stack + Otaku (8nime Free)
ADDON_ZIPS = [
    f"{BINGIE_BASE}/repository.bingie/repository.bingie-1.0.0.zip",
    f"{BINGIE_BASE}/skin.bingie/skin.bingie-2.0.2.zip",
    f"{BINGIE_BASE}/plugin.video.tmdb.bingie.helper/plugin.video.tmdb.bingie.helper-1.0.2.zip",
    f"{BINGIE_BASE}/script.bingie.helper/script.bingie.helper-1.1.2.zip",
    f"{BINGIE_BASE}/script.bingie.toolbox/script.bingie.toolbox-1.0.0.zip",
    f"{BINGIE_BASE}/script.bingie.widgets/script.bingie.widgets-1.0.1.zip",
    f"{BINGIE_BASE}/script.module.bingie/script.module.bingie-1.0.0.zip",
    f"{BINGIE_BASE}/plugin.program.autocompletion/plugin.program.autocompletion-2.1.3.zip",
    f"{BINGIE_BASE}/resource.images.studios.coloured/resource.images.studios.coloured-1.0.0012.zip",
    f"{BINGIE_BASE}/script.skin.helper.colorpicker/script.skin.helper.colorpicker-2.0.3.zip",
    f"{BINGIE_BASE}/script.skin.helper.skinbackup/script.skin.helper.skinbackup-1.0.22.zip",
    f"{KODI_MIRROR}/script.skinshortcuts/script.skinshortcuts-2.0.3.zip",
    f"{HOOTY_BASE}/repo/zips/plugin.video.otaku/plugin.video.otaku-5.2.99.zip",
    f"{HOOTY_BASE}/repo/zips/context.otaku/context.otaku-1.0.35.zip",
    f"{HOOTY_BASE}/repository.hooty-1.0.zip",
    # WatchNixtoons2 free source (deps script.module.requests/six already below;
    # inputstream.adaptive is a Kodi built-in). Bundled so the build ships with a
    # working alternate backend for the 8nime Bingie Helper.
    f"{DEXE_BASE}/zips/plugin.video.watchnixtoons2/plugin.video.watchnixtoons2-0.14.18.zip",
    # FANime F free source (deps simplejson/requests/beautifulsoup4/six already
    # below; inputstream.adaptive built-in). Scrapes animixplay/gogoanime.
    f"{ANIMANIAC_BASE}/plugin.video.fanimef/plugin.video.fanimef-1.1.8.zip",
]

# Python modules required by Bingie/Otaku (verified omega mirror versions)
MODULE_ZIPS = [
    # requests stack (script.module.requests declares these; missing urllib3 breaks widgets)
    f"{KODI_MIRROR}/script.module.urllib3/script.module.urllib3-1.26.16+matrix.1.zip",
    f"{KODI_MIRROR}/script.module.certifi/script.module.certifi-2023.5.7.zip",
    f"{KODI_MIRROR}/script.module.chardet/script.module.chardet-5.1.0.zip",
    f"{KODI_MIRROR}/script.module.idna/script.module.idna-3.10.0.zip",
    f"{KODI_MIRROR}/script.module.requests/script.module.requests-2.31.0.zip",
    # skinshortcuts stack (without unidecode Bingie home/menu XML never generates)
    f"{KODI_MIRROR}/script.module.unidecode/script.module.unidecode-1.1.1+matrix.2.zip",
    f"{KODI_MIRROR}/script.module.simpleeval/script.module.simpleeval-0.9.10.zip",
    f"{KODI_MIRROR}/script.module.simplejson/script.module.simplejson-3.19.1+matrix.1.zip",
    f"{KODI_MIRROR}/script.module.simplecache/script.module.simplecache-2.0.2.zip",
    f"{KODI_MIRROR}/script.module.beautifulsoup4/script.module.beautifulsoup4-4.12.2.zip",
    f"{KODI_MIRROR}/script.module.addon.signals/script.module.addon.signals-0.0.6+matrix.1.zip",
    f"{KODI_MIRROR}/script.module.infotagger/script.module.infotagger-0.0.5.zip",
    f"{KODI_MIRROR}/script.module.qrcode/script.module.qrcode-6.1.0+matrix.3.zip",
    f"{KODI_MIRROR}/script.module.autocompletion/script.module.autocompletion-2.1.1.zip",
    f"{KODI_MIRROR}/script.module.six/script.module.six-1.16.0+matrix.1.zip",
    f"{KODI_MIRROR}/script.module.inputstreamhelper/script.module.inputstreamhelper-0.8.5.zip",
    f"{KODI_MIRROR}/script.module.pyqrcode/script.module.pyqrcode-1.2.1+matrix.4.zip",
]


def download(url: str, dest: Path) -> bool:
    try:
        print(f"  GET {url}")
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as exc:
        print(f"  SKIP ({exc})")
        return False


def extract_addon_zip(zip_path: Path, addons_dir: Path) -> list[str]:
    installed = []
    with zipfile.ZipFile(zip_path) as zf:
        # Find top-level addon folders (contain addon.xml)
        roots = set()
        for name in zf.namelist():
            parts = name.split("/")
            if len(parts) >= 2 and parts[1] == "addon.xml":
                roots.add(parts[0])
        if not roots:
            for name in zf.namelist():
                if name.endswith("/addon.xml"):
                    roots.add(name.split("/")[0])

        extract_dir = zip_path.parent / "extracted" / zip_path.stem
        zf.extractall(extract_dir)

        for root in sorted(roots):
            src = extract_dir / root
            if not (src / "addon.xml").exists():
                continue
            dest = addons_dir / root
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            installed.append(root)
            print(f"  -> addons/{root}")
    return installed


def sync_hosted_configs(wizard_addons: Path) -> None:
    text_dir = wizard_addons / "resources" / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    hosted = ROOT / "hosted"
    for name in [
        "builds.txt", "addons.json", "addons-anime.json", "addons-skins.json",
        "advanced.json", "notify.txt", "youtube.txt",
    ]:
        src = hosted / name
        if src.exists():
            shutil.copy2(src, text_dir / name)


def patch_uservar_local(wizard_addons: Path) -> None:
    uservar = wizard_addons / "uservar.py"
    content = uservar.read_text()
    content = content.replace(
        "BUILDFILE = BASE_URL + '/builds.txt'",
        "BUILDFILE = 'http://'",
    )
    content = content.replace(
        "ADDONFILE = BASE_URL + '/addons.json'",
        "ADDONFILE = 'http://'",
    )
    content = content.replace(
        "ADVANCEDFILE = BASE_URL + '/advanced.json'",
        "ADVANCEDFILE = 'http://'",
    )
    content = content.replace("AUTOINSTALL = 'Yes'", "AUTOINSTALL = 'No'")
    content = content.replace("AUTOUPDATE = 'Yes'", "AUTOUPDATE = 'No'")
    content = content.replace("ENABLE = 'Yes'", "ENABLE = 'No'")
    uservar.write_text(content)


def patch_guisettings(userdata: Path) -> None:
    gui = userdata / "guisettings.xml"
    if not gui.exists():
        return
    text = gui.read_text(encoding="utf-8", errors="replace")
    text = re.sub(
        r'<setting id="lookandfeel\.skin"[^>]*>[^<]+</setting>',
        '<setting id="lookandfeel.skin">skin.bingie</setting>',
        text,
    )
    text = re.sub(
        r'(<setting id="lookandfeel\.skintheme"[^>]*)( default="true")?(>)[^<]+(</setting>)',
        r'\1\3SKINDEFAULT\4',
        text,
    )
    # Allow sideloaded addons. Without this Kodi (19+/21) can re-disable our
    # directly-installed addons on startup because their origin isn't a trusted
    # repo — silently undoing the enabled=1 we set in Addons33.db.
    if re.search(r'<setting id="addons\.unknownsources"', text):
        text = re.sub(
            r'(<setting id="addons\.unknownsources"[^>]*)( default="true")?(>)[^<]*(</setting>)',
            r'\1\3true\4',
            text,
        )
    else:
        text = text.replace(
            "</settings>",
            '    <setting id="addons.unknownsources">true</setting>\n</settings>',
            1,
        )
    gui.write_text(text, encoding="utf-8")
    print("  Patched guisettings.xml -> skin.bingie + addons.unknownsources=true")


def write_sources(userdata: Path) -> None:
    sources = userdata / "sources.xml"
    content = """<sources>
    <programs>
        <default pathversion="1"></default>
        <source>
            <name>8nime</name>
            <path pathversion="1">special://home/addons/</path>
            <allowsharing>true</allowsharing>
        </source>
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
        <source>
            <name>Bingie Repo</name>
            <path pathversion="1">https://matke-84.github.io/repository.bingie/</path>
            <allowsharing>true</allowsharing>
        </source>
        <source>
            <name>Hooty Repo</name>
            <path pathversion="1">https://goldenfreddy0703.github.io/repository.hooty/</path>
            <allowsharing>true</allowsharing>
        </source>
        <source>
            <name>dEXE Repo</name>
            <path pathversion="1">https://raw.githubusercontent.com/deklica/repo.dexe/master/repo/</path>
            <allowsharing>true</allowsharing>
        </source>
    </files>
</sources>
"""
    sources.write_text(content, encoding="utf-8")
    print("  Wrote sources.xml with Bingie + Hooty repos")


# Addons that must be enabled for 8nime to work
ENABLE_ADDONS = [
    "skin.bingie",
    "plugin.video.otaku",
    "plugin.video.tmdb.bingie.helper",
    "plugin.program.8nime.wizard",
    "plugin.program.autocompletion",
    "context.otaku",
    "repository.bingie",
    "repository.hooty",
    "repository.dexe",
    "plugin.program.optiklean",
    "script.bingie.helper",
    "script.bingie.toolbox",
    "script.bingie.widgets",
    "script.module.bingie",
    "script.skinshortcuts",
    "resource.images.studios.coloured",
]


def enable_addons(kodi_home: Path, addon_ids: list[str] | None = None) -> int:
    """Enable addons in Addons33.db. Kodi must be closed or the DB may be locked."""
    db_path = kodi_home / "userdata" / "Database" / "Addons33.db"
    if not db_path.exists():
        print("  Addons33.db not found — Kodi will register addons on next launch.")
        return 0

    # Always enable the curated list, any explicit ids, AND every addon we
    # actually shipped into addons/ (every folder carrying an addon.xml). The
    # old prefix filter (plugin./skin./context./repository.) silently skipped
    # script.module.* deps, script.skin.helper.*, script.skinshortcuts and
    # resource.* — leaving them enabled=0 so Kodi could not resolve
    # `import requests` and could not even load skin.bingie (Estuary fallback).
    targets = set(addon_ids or [])
    targets.update(ENABLE_ADDONS)
    addons_root = kodi_home / "addons"
    if addons_root.is_dir():
        for folder in addons_root.iterdir():
            if folder.name == "packages":
                continue
            if folder.is_dir() and (folder / "addon.xml").exists():
                targets.add(folder.name)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    enabled_count = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for addon_id in sorted(targets):
        # UPSERT: enable_addons may run before Kodi has registered the row, so a
        # plain UPDATE would no-op and leave the dep disabled. Insert it ourselves.
        cur.execute(
            "UPDATE installed SET enabled=1, disabledReason=0, lastUpdated=? WHERE addonID=?",
            (now, addon_id),
        )
        if cur.rowcount:
            enabled_count += cur.rowcount
            print(f"  enabled {addon_id}")
        else:
            cur.execute(
                "INSERT INTO installed (addonID, enabled, installDate, lastUpdated, origin, disabledReason) "
                "VALUES (?, 1, ?, ?, '', 0)",
                (addon_id, now, now),
            )
            enabled_count += 1
            print(f"  registered+enabled {addon_id}")

    conn.commit()
    conn.close()
    print(f"  Enabled {enabled_count} addon(s) in database.")
    return enabled_count


def write_deploy_marker(kodi_home: Path) -> None:
    marker = kodi_home / "8NIME_DEPLOYED.txt"
    marker.write_text(
        "8nime deployed to this Kodi profile.\n"
        f"Path: {kodi_home}\n"
        "If Kodi looks fresh, check Add-ons menu — Bingie skin may have failed and fallen back to Estuary.\n",
        encoding="utf-8",
    )


def main() -> int:
    kodi_home = find_kodi_home()
    if not kodi_home or not kodi_home.exists():
        print("ERROR: Could not find a Kodi profile directory on Windows.")
        print("Expected Microsoft Store path under AppData/Local/Packages/XBMCFoundation.Kodi_*/LocalCache/Roaming/Kodi")
        return 1

    addons_dir = kodi_home / "addons"
    userdata = kodi_home / "userdata"
    packages_dir = addons_dir / "packages"
    addons_dir.mkdir(parents=True, exist_ok=True)
    packages_dir.mkdir(parents=True, exist_ok=True)

    print(f"Kodi home: {kodi_home}")
    print("  (Microsoft Store Kodi maps this as %APPDATA%\\Roaming\\Kodi when running)")
    print("\n[1/7] Downloading and installing addons...")

    all_installed: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for url in ADDON_ZIPS + MODULE_ZIPS:
            name = url.rsplit("/", 1)[-1]
            dest = tmp_path / name
            if not download(url, dest):
                continue
            shutil.copy2(dest, packages_dir / name)
            try:
                installed = extract_addon_zip(dest, addons_dir)
                all_installed.extend(installed)
            except zipfile.BadZipFile as exc:
                print(f"  BAD ZIP {name}: {exc}")

    print("\n[2/7] Deploying 8nimeWizard...")
    wizard_src = ROOT / "wizard" / "plugin.program.8nime.wizard"
    wizard_dest = addons_dir / "plugin.program.8nime.wizard"
    if wizard_dest.exists():
        shutil.rmtree(wizard_dest)
    shutil.copytree(wizard_src, wizard_dest)
    sync_hosted_configs(wizard_dest)
    patch_uservar_local(wizard_dest)
    print("  -> addons/plugin.program.8nime.wizard")

    print("\n[3/7] Applying advancedsettings...")
    adv_src = ROOT / "config" / "advancedsettings" / "anime-streaming.xml"
    adv_dest = userdata / "advancedsettings.xml"
    shutil.copy2(adv_src, adv_dest)
    print("  -> userdata/advancedsettings.xml")

    print("\n[4/7] Configuring Kodi...")
    patch_guisettings(userdata)
    write_sources(userdata)
    write_deploy_marker(kodi_home)

    print("\n[5/7] Enabling addons in database...")
    print("  (Close Kodi first if this step fails with 'database is locked')")
    enable_addons(kodi_home)

    print("\n[6/7] Applying 8nime skin patches and branding...")
    anime = ROOT / "scripts" / "apply-anime-bingie.py"
    spec = importlib.util.spec_from_file_location("apply_anime_bingie", anime)
    anime_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(anime_mod)
    anime_mod.apply(kodi_home)

    print("\n[7/7] Summary")
    print(f"  Installed {len(set(all_installed))} addons")
    for addon in sorted(set(all_installed)):
        print(f"    - {addon}")

    print("\nDone. Close Kodi completely, then reopen it.")
    print("Video add-ons: Add-ons > Video add-ons > Otaku")
    print("If addons show as disabled: Settings > Add-ons > My add-ons > Video add-ons > Otaku > Enable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
