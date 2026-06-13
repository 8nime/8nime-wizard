#!/usr/bin/env python3
"""Apply 8nime Bingie skin patches (Otaku / AniList)."""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "config" / "skin-patches" / "anime"
STOCK = ROOT / "config" / "skin-patches" / "stock"
MEDIA_SRC = ROOT / "config" / "branding"
DEPLOY = ROOT / "scripts" / "deploy-windows.py"
ANILIST_HELPER_SRC = ROOT / "addons" / "plugin.video.8nime.bingie.helper"
ANILIST_HELPER_ID = "plugin.video.8nime.bingie.helper"
WIZARD_ID = "plugin.program.8nime.wizard"
HOOTY_OTAKU = (
    "https://raw.githubusercontent.com/Goldenfreddy0703/repository.hooty/master"
    "/repo/zips/plugin.video.otaku/plugin.video.otaku-5.2.99.zip"
)
HOOTY_CONTEXT = (
    "https://raw.githubusercontent.com/Goldenfreddy0703/repository.hooty/master"
    "/repo/zips/context.otaku/context.otaku-1.0.35.zip"
)
DEXE_REPO = (
    "https://raw.githubusercontent.com/deklica/repo.dexe/master"
    "/repo/repository.dexe/repository.dexe-1.0.11.zip"
)
OPTIKLEAN = (
    "https://raw.githubusercontent.com/deklica/repo.dexe/master"
    "/zips/plugin.program.optiklean/plugin.program.optiklean-2.3.0.zip"
)
OPTIKLEAN_ID = "plugin.program.optiklean"
DEXE_REPO_ID = "repository.dexe"

spec = importlib.util.spec_from_file_location("deploy_windows", DEPLOY)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def ensure_patches_built() -> None:
    required = [
        PATCHES / "IncludesPaths.xml",
        PATCHES / "IncludesDialogVideoInfo.xml",
        PATCHES / "IncludesDefaultSkinSettings.xml",
        PATCHES / "Custom_1119_Category2_Hub.xml",
        PATCHES / "Custom_1117_Categories_Hub.xml",
        PATCHES / "shortcuts" / "movies.DATA.xml",
        PATCHES / "shortcuts" / "moviehub.DATA.xml",
        PATCHES / "IncludesHomeBingie.xml",
        PATCHES / "Custom_1101_StartUp.xml",
        PATCHES / "Custom_1102_StartUp2.xml",
        PATCHES / "screensaver-bingie.xml",
    ]
    if not all(p.exists() for p in required):
        raise SystemExit("Missing patch files in config/skin-patches/anime/ — check the repo.")


def install_zip_addon(url: str, kodi_home: Path) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "addon.zip"
        urllib.request.urlretrieve(url, zip_path)
        return deploy.extract_addon_zip(zip_path, kodi_home / "addons")


def _force_enable_addons(kodi_home: Path, addon_ids: list[str]) -> None:
    """Ensure addons are enabled even if deploy.enable_addons skipped them."""
    import sqlite3
    from datetime import datetime

    db_path = kodi_home / "userdata" / "Database" / "Addons33.db"
    if not db_path.exists():
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for addon_id in addon_ids:
        cur.execute(
            "UPDATE installed SET enabled=1, disabledReason=0, lastUpdated=? WHERE addonID=?",
            (now, addon_id),
        )
        if cur.rowcount:
            print(f"  enabled {addon_id} in Addons33.db")
        else:
            cur.execute(
                "INSERT INTO installed (addonID, enabled, installDate, lastUpdated, origin, disabledReason) "
                "VALUES (?, 1, ?, ?, '', 0)",
                (addon_id, now, now),
            )
            print(f"  registered {addon_id} in Addons33.db")
    conn.commit()
    conn.close()


def ensure_anilist_helper(kodi_home: Path) -> None:
    dest = kodi_home / "addons" / ANILIST_HELPER_ID
    if not ANILIST_HELPER_SRC.exists():
        raise SystemExit(f"Missing addon source: {ANILIST_HELPER_SRC}")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ANILIST_HELPER_SRC, dest)
    print(f"  installed {ANILIST_HELPER_ID}")
    deploy.enable_addons(kodi_home, [ANILIST_HELPER_ID])
    _force_enable_addons(kodi_home, [ANILIST_HELPER_ID])
    sync_anilist_token(kodi_home)  # head start only; the helper has its own login + mirrors its token back to Otaku


def sync_anilist_token(kodi_home: Path) -> None:
    """Seed the helper with Otaku's AniList token if one already exists.

    Convenience only: the helper now has its own login (Settings -> Log in with
    AniList, QR-based) and mirrors its token back to Otaku, so this is just a
    head start for users already signed in via Otaku."""
    otaku_settings = kodi_home / "userdata" / "addon_data" / "plugin.video.otaku" / "settings.xml"
    helper_settings = kodi_home / "userdata" / "addon_data" / ANILIST_HELPER_ID / "settings.xml"
    if not otaku_settings.exists():
        print("  AniList: log in via the helper's Settings -> Log in with AniList (scan the QR)")
        return
    otaku_text = otaku_settings.read_text(encoding="utf-8")
    match = re.search(r'<setting id="anilist\.token"[^>]*>([^<]*)</setting>', otaku_text)
    if not match or not match.group(1).strip():
        print("  AniList: log in via the helper's Settings -> Log in with AniList (scan the QR)")
        return
    token = match.group(1).strip()
    helper_settings.parent.mkdir(parents=True, exist_ok=True)
    if helper_settings.exists() and 'version="2"' in helper_settings.read_text(encoding="utf-8"):
        text = helper_settings.read_text(encoding="utf-8")
        pattern = r'(<setting id="anilist_token"[^>]*>)([^<]*)(</setting>)'
        if re.search(pattern, text):
            text = re.sub(pattern, rf"\g<1>{token}\g<3>", text, count=1)
        else:
            text = text.replace(
                "</settings>",
                f'    <setting id="anilist_token" default="true">{token}</setting>\n</settings>',
                1,
            )
        helper_settings.write_text(text, encoding="utf-8")
        print("  synced AniList token from Otaku to helper")
        return
    helper_settings.write_text(
        "\n".join(
            [
                '<settings version="2">',
                f'    <setting id="anilist_token" default="true">{token}</setting>',
                '    <setting id="title_language" default="true">english</setting>',
                "</settings>",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("  created helper settings with Otaku AniList token")


def ensure_optiklean(kodi_home: Path) -> None:
    """Install OptiKlean cache/maintenance addon from dEXE community repository."""
    addons = kodi_home / "addons"
    if not (addons / DEXE_REPO_ID / "addon.xml").exists():
        print(f"  Installing {DEXE_REPO_ID} …")
        install_zip_addon(DEXE_REPO, kodi_home)
    if not (addons / OPTIKLEAN_ID / "addon.xml").exists():
        print(f"  Installing {OPTIKLEAN_ID} …")
        install_zip_addon(OPTIKLEAN, kodi_home)
    deploy.enable_addons(kodi_home, [DEXE_REPO_ID, OPTIKLEAN_ID])
    _force_enable_addons(kodi_home, [DEXE_REPO_ID, OPTIKLEAN_ID])


def ensure_otaku_stack(kodi_home: Path) -> None:
    addons = kodi_home / "addons"
    for addon_id, url in (
        ("plugin.video.otaku", HOOTY_OTAKU),
        ("context.otaku", HOOTY_CONTEXT),
    ):
        if not (addons / addon_id / "addon.xml").exists():
            print(f"  Installing {addon_id} …")
            install_zip_addon(url, kodi_home)
    deploy.enable_addons(kodi_home, ["plugin.video.otaku", "context.otaku"])
    _force_enable_addons(kodi_home, ["plugin.video.otaku", "context.otaku"])


def merge_settings_snippet(settings_xml: Path, snippet_xml: Path) -> int:
    """Merge legacy skin-style settings snippets (type= attribute)."""
    if not snippet_xml.exists():
        return 0
    snippet = snippet_xml.read_text(encoding="utf-8")
    if 'version="2"' in snippet:
        return 0

    if settings_xml.exists():
        text = settings_xml.read_text(encoding="utf-8")
    else:
        text = "<settings>\n</settings>"
        settings_xml.parent.mkdir(parents=True, exist_ok=True)

    changed = 0
    for block in re.finditer(r"<setting id=\"([^\"]+)\" type=\"([^\"]+)\">([^<]*)</setting>", snippet):
        sid, stype, value = block.group(1), block.group(2), block.group(3)
        pattern = rf'(<setting id="{re.escape(sid)}" type="[^"]+">)([^<]*)(</setting>)'
        if re.search(pattern, text):
            new_text, n = re.subn(pattern, rf"\g<1>{value}\g<3>", text, count=1)
            if n:
                text = new_text
                changed += 1
        else:
            insert = f'    <setting id="{sid}" type="{stype}">{value}</setting>\n'
            text = text.replace("</settings>", insert + "</settings>", 1)
            changed += 1

    if changed:
        settings_xml.write_text(text, encoding="utf-8")
    return changed


def otaku_addon_version(kodi_home: Path) -> str:
    addon_xml = kodi_home / "addons" / "plugin.video.otaku" / "addon.xml"
    if not addon_xml.exists():
        return "5.2.99"
    text = addon_xml.read_text(encoding="utf-8")
    match = re.search(
        r'<addon id="plugin\.video\.otaku"[^>]*\bversion="([^"]+)"',
        text,
    )
    return match.group(1) if match else "5.2.99"


def merge_otaku_settings(settings_xml: Path, snippet_xml: Path, kodi_home: Path | None = None) -> int:
    """Merge Kodi 21 settings (version=2) for plugin.video.otaku."""
    if not snippet_xml.exists():
        return 0

    snippet = snippet_xml.read_text(encoding="utf-8")
    overrides = {
        m.group(1): m.group(2)
        for m in re.finditer(
            r'<setting id="([^"]+)"[^>]*>([^<]*)</setting>',
            snippet,
        )
    }
    if not overrides:
        return 0

    if kodi_home is not None:
        overrides["version"] = otaku_addon_version(kodi_home)

    settings_xml.parent.mkdir(parents=True, exist_ok=True)
    if settings_xml.exists() and 'version="2"' in settings_xml.read_text(encoding="utf-8"):
        text = settings_xml.read_text(encoding="utf-8")
        changed = 0
        for sid, value in overrides.items():
            pattern = rf'(<setting id="{re.escape(sid)}"[^>]*>)([^<]*)(</setting>)'
            if re.search(pattern, text):
                new_text, n = re.subn(pattern, rf"\g<1>{value}\g<3>", text, count=1)
                if n:
                    text = new_text
                    changed += 1
            else:
                insert = f'    <setting id="{sid}" default="true">{value}</setting>\n'
                text = text.replace("</settings>", insert + "</settings>", 1)
                changed += 1
        if changed:
            settings_xml.write_text(text, encoding="utf-8")
        return changed

    lines = ['<settings version="2">']
    for sid, value in overrides.items():
        lines.append(f'    <setting id="{sid}" default="true">{value}</setting>')
    lines.append("</settings>")
    lines.append("")
    settings_xml.write_text("\n".join(lines), encoding="utf-8")
    return len(overrides)


def finalize_otaku_settings(settings_xml: Path, kodi_home: Path) -> None:
    """Force changelog/version keys Otaku checks on every plugin invoke."""
    if not settings_xml.exists():
        return

    addon_version = otaku_addon_version(kodi_home)
    text = settings_xml.read_text(encoding="utf-8")
    patches = {
        "showchangelog": "1",
        "first_time": "false",
        "version": addon_version,
    }
    for sid, value in patches.items():
        pattern = rf'(<setting id="{re.escape(sid)}"[^>]*>)([^<]*)(</setting>)'
        if re.search(pattern, text):
            text, _ = re.subn(pattern, rf"\g<1>{value}\g<3>", text, count=1)
        else:
            insert = f'    <setting id="{sid}" default="true">{value}</setting>\n'
            text = text.replace("</settings>", insert + "</settings>", 1)
    settings_xml.write_text(text, encoding="utf-8")


def _suggestion_item(label: str, info_path: str) -> str:
    helper = "plugin://plugin.video.8nime.bingie.helper/?info="
    return (
        "\t\t\t<item>\n"
        f"\t\t\t\t<label>{label}</label>\n"
        f'\t\t\t\t<property name="path">{helper}{info_path}'
        "&amp;widget=true&amp;nextpage=false</property>\n"
        "\t\t\t\t<visible>String.IsEmpty(Skin.String(CustomSearchTerm))</visible>\n"
        "\t\t\t</item>"
    )


ANILIST_SEARCH_SUGGESTIONS = (
    '<include name="Search_Suggestions_Content_2">\n'
    "\t\t<content>\n"
    + "\n".join(
        _suggestion_item(label, info_path)
        for label, info_path in (
            ("Trending Anime", "trakt_trending&amp;tmdb_type=tv"),
            ("Popular Anime", "trakt_popular&amp;tmdb_type=tv"),
            ("Top Rated Anime", "trakt_userlist&amp;list_slug=imdb-top-rated-tv-shows"),
            ("Airing This Season", "trakt_userlist&amp;list_slug=latest-tv-shows"),
            ("Upcoming Anime", "anilist_upcoming&amp;tmdb_type=tv"),
            ("Trending Movies", "trakt_trending&amp;tmdb_type=movie"),
            ("Popular Movies", "trakt_popular&amp;tmdb_type=movie"),
        )
    )
    + "\n\t\t</content>\n\t</include>"
)


def patch_includes_bingie_search(kodi_home: Path) -> bool:
    """Route the Bingie search window (1109) to the AniList helper instead of TMDb/Trakt.

    Both the library and no-library search result paths resolve through the
    SearchTMDB* variables in IncludesBingieSearch.xml, so repointing those (plus
    the trending suggestion rows) covers the whole search UI.
    """
    path = kodi_home / "addons" / "skin.bingie" / "1080i" / "IncludesBingieSearch.xml"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    original = text

    helper = "plugin://plugin.video.8nime.bingie.helper/?info=search&amp;widget=true"
    # All / Collections / People -> anime TV search (AniList has no collections/people media search)
    text = re.sub(
        r"plugin://plugin\.video\.tmdb\.bingie\.helper\?info=search&amp;tmdb_type=(?:both|collection|person)",
        f"{helper}&amp;tmdb_type=tv",
        text,
    )
    text = text.replace(
        "plugin://plugin.video.tmdb.bingie.helper?info=search&amp;tmdb_type=movie",
        f"{helper}&amp;tmdb_type=movie",
    )
    text = text.replace(
        "plugin://plugin.video.tmdb.bingie.helper?info=search&amp;tmdb_type=tv",
        f"{helper}&amp;tmdb_type=tv",
    )

    # Trending/popular suggestion rows -> AniList helper equivalents.
    text = re.sub(
        r"plugin://plugin\.video\.tmdb\.bingie\.helper\?info=(?:trending_day|trending_week|trakt_mostplayed|trakt_mostviewers|trakt_trending)",
        "plugin://plugin.video.8nime.bingie.helper/?info=trakt_trending",
        text,
    )
    text = re.sub(
        r"plugin://plugin\.video\.tmdb\.bingie\.helper\?info=(?:popular|top_rated|revenue_movies|most_voted|trakt_popular)",
        "plugin://plugin.video.8nime.bingie.helper/?info=trakt_popular",
        text,
    )

    if "plugin.video.tmdb.bingie.helper" in text:
        leftover = re.findall(r"plugin://plugin\.video\.tmdb\.bingie\.helper[^\"<&]*", text)
        raise SystemExit(
            "IncludesBingieSearch still references TMDb helper after patch: "
            + ", ".join(sorted(set(leftover))[:5])
        )

    # The unified "Results" list is driven by SearchTMDBAll; make it span every anime
    # format (TV + movies + ONA/OVA) instead of TV-only. Scoped to that one variable so
    # SearchTMDBShows/SearchTMDBMovies keep their format-specific filters.
    text = re.sub(
        r'(<variable name="SearchTMDBAll">.*?tmdb_type=)tv(.*?</variable>)',
        r"\1both\2",
        text,
        flags=re.DOTALL,
    )

    # Empty-state hint: "Search by TMDb Movies, Shows or People" -> AniList-neutral.
    text = text.replace("$LOCALIZE[31186]", "Search Anime")

    # Replace the TMDb-labelled static suggestion rows (shown before typing) with a
    # short, AniList-branded browse list. The dynamic per-keystroke autocomplete lives
    # on container 1007 in Custom_1109 and is unaffected by this block.
    text = re.sub(
        r'<include name="Search_Suggestions_Content_2">.*?</include>',
        ANILIST_SEARCH_SUGGESTIONS,
        text,
        flags=re.DOTALL,
    )

    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


SEARCH_RESULTS_BLOCK = (
    '\t\t\t<!-- ANIME: single AniList "Results" list (replaces TMDb/Otaku skinshortcuts search templates) -->\n'
    '\t\t\t<include content="Object_SearchList_Template">\n'
    '\t\t\t\t<param name="id" value="5041" />\n'
    '\t\t\t\t<param name="groupid" value="7541" />\n'
    '\t\t\t\t<param name="path" value="$VAR[SearchTMDBAll]" />\n'
    '\t\t\t\t<param name="path2" value="" />\n'
    '\t\t\t\t<param name="label" value="Results" />\n'
    '\t\t\t\t<param name="widgetLimit" value="$INFO[Skin.String(WidgetsGlobalLimit)]" />\n'
    '\t\t\t\t<param name="layout" value="PosterPanelBingie" />\n'
    '\t\t\t\t<param name="layoutwidth" value="295" />\n'
    '\t\t\t\t<param name="layoutheight" value="420" />\n'
    '\t\t\t\t<param name="height" value="975" />\n'
    '\t\t\t\t<param name="widgetTags" value="WidgetTagOverlayDisable" />\n'
    '\t\t\t\t<param name="widgetTarget" value="videos" />\n'
    "\t\t\t</include>"
)


def patch_custom_search_window(kodi_home: Path) -> bool:
    """Force the search window (1109) to render a single AniList "Results" list.

    Stock Bingie swaps between two skinshortcuts templates based on Library.HasContent:
    `skinshortcuts-template-search` (3 sections -> plugin.video.otaku/search as an
    ActivateWindow action, so it never renders inline results) and
    `skinshortcuts-template-tmdbsearch` (the TMDb path). Both are dropped here for one
    inline Object_SearchList_Template bound to SearchTMDBAll (the AniList helper). Also
    repoints autocomplete suggestions from Google (plugin.program.autocompletion) to the
    AniList helper, so every search surface hits AniList; Otaku is playback-only.
    """
    path = kodi_home / "addons" / "skin.bingie" / "1080i" / "Custom_1109_BingieSearch.xml"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    original = text

    tpl_re = re.compile(
        r'[ \t]*<include condition="Library\.HasContent\(Movies\)[^>]*>'
        r"skinshortcuts-template-search</include>\s*"
        r'[ \t]*<include condition="!Library\.HasContent\(Movies\)[^>]*>'
        r"skinshortcuts-template-tmdbsearch</include>"
    )
    text = tpl_re.sub(SEARCH_RESULTS_BLOCK, text)

    text = re.sub(
        r"<content>plugin://plugin\.program\.autocompletion\?info=autocomplete[^<]*</content>",
        "<content>plugin://plugin.video.8nime.bingie.helper/?info=autocomplete"
        "&amp;query=$INFO[Skin.String(CustomSearchTerm)]</content>",
        text,
    )

    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def patch_includes_bingie(kodi_home: Path) -> bool:
    """Strip legacy mal_id guards from IncludesBingie hub fallbacks."""
    path = kodi_home / "addons" / "skin.bingie" / "1080i" / "IncludesBingie.xml"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    id_guard_re = re.compile(
        r" \+ \[String\.IsEqual\(ListItem\.Property\(mal_id\),Container\(17195\)\.ListItem\.Property\(mal_id\)\)"
        r" \| String\.IsEqual\(ListItem\.Property\(tmdb_id\),Container\(17195\)\.ListItem\.Property\(tmdb_id\)\)\]"
    )
    old_mal_guard = " + String.IsEqual(ListItem.Property(mal_id),Container(17195).ListItem.Property(mal_id))"
    new_text = id_guard_re.sub("", text)
    if old_mal_guard in new_text:
        new_text = new_text.replace(old_mal_guard, "")
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def patch_episode_sort_order(kodi_home: Path) -> bool:
    """Show the seasons-view episode list newest-first.

    View_527_Bingie_Seasons.xml renders the focused season's episodes in a skin
    <content> container (id 5027) bound to Container(527).ListItem.FolderPath. That
    container hardcodes `sortby="episode" sortorder="ascending"`, so it ignores both
    Kodi's sort drawer and the helper's emit order -- the episode list always showed
    oldest-first while the seasons list itself is newest-first. Flip it to descending
    so the episode list matches. Idempotent (no-op once descending).
    """
    path = kodi_home / "addons" / "skin.bingie" / "1080i" / "View_527_Bingie_Seasons.xml"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    old = (
        '<content target="videos" sortby="episode" sortorder="ascending">'
        "$INFO[Container(527).ListItem.FolderPath]</content>"
    )
    new = old.replace('sortorder="ascending"', 'sortorder="descending"')
    if old not in text:
        return False
    path.write_text(text.replace(old, new), encoding="utf-8")
    return True


def patch_change_provider_blade(kodi_home: Path) -> bool:
    """Add a 'Change provider' button to the Videos side-blade options drawer.

    Surfaces the helper's playback-provider picker (Addon.OpenSettings) directly in
    Kodi's options drawer while browsing our episode/seasons lists, so switching
    providers doesn't require leaving for the home menu. Inserted into the
    SideBlade grouplist (id 9000) after the Sort buttons; visible only for our
    plugin's episode/seasons content. Idempotent (skips if id 8801 already present).
    """
    path = kodi_home / "addons" / "skin.bingie" / "1080i" / "MyVideoNav.xml"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if 'id="8801"' in text:
        return False
    anchor = (
        "\t\t\t\t\t<usealttexture>Container.SortDirection(Ascending)</usealttexture>\n"
        "\t\t\t\t</control>\n"
    )
    if anchor not in text:
        return False
    button = (
        '\t\t\t\t<control type="button" id="8801">\n'
        "\t\t\t\t\t<!-- 8nime: Change playback provider (opens helper settings) -->\n"
        "\t\t\t\t\t<include>SideBladeMenuButton</include>\n"
        "\t\t\t\t\t<label>Change provider</label>\n"
        "\t\t\t\t\t<visible>String.StartsWith(Container.FolderPath,plugin://plugin.video.8nime.bingie.helper)"
        " + [Container.Content(episodes) | Container.Content(seasons)]</visible>\n"
        "\t\t\t\t\t<onclick>ClearProperty(ShowViewSubMenu,Home)</onclick>\n"
        "\t\t\t\t\t<onclick>Addon.OpenSettings(plugin.video.8nime.bingie.helper)</onclick>\n"
        "\t\t\t\t</control>\n\n"
    )
    path.write_text(text.replace(anchor, anchor + button, 1), encoding="utf-8")
    return True


def patch_tmdbbingie_loader(kodi_home: Path) -> bool:
    """Bind the hidden Container(17195) to a request-backed details path.

    The 350 ms background monitor that used to populate 17195 was removed in the
    AniList helper rehaul; without a content path the info-dialog header (which
    reads Container(17195).ListItem.*) goes blank. Point the loader list at the
    helper's `details` route keyed on the focused item, so the header is
    request-backed and follows focus with no polling -- the single request returns
    the full header bundle (genre/studio/cast/creator/ratings + season totals).
    Idempotent: once a <content> is present the anchoring regex no longer matches.
    """
    path = kodi_home / "addons" / "skin.bingie" / "1080i" / "Includes.xml"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    content = (
        "            <content>plugin://plugin.video.8nime.bingie.helper/"
        "?info=details&amp;mal_id=$INFO[ListItem.Property(mal_id)]"
        "&amp;tmdb_id=$INFO[ListItem.Property(tmdb_id)]"
        "&amp;season=$INFO[ListItem.Season]&amp;cacheonly=true"
        "&amp;reload=$INFO[Window(Home).Property(TMDbBingieHelper.Widgets.Reload)]</content>\n"
    )
    loader_re = re.compile(
        r'(<control type="list" id="17195">.*?<left>-1920</left>\s*)(</control>)',
        re.DOTALL,
    )
    new_text, n = loader_re.subn(
        lambda m: m.group(1) + content + "        " + m.group(2), text
    )
    if not n or new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


PROFILE_AVATAR_OVERRIDE = "special://skin/extras/media/defaultuser.png"


def patch_profile_avatar(kodi_home: Path) -> bool:
    """Show the staged defaultuser.png as the profile avatar.

    The home profile picture renders $INFO[System.ProfileThumb] with no fallback.
    When the profile has no custom thumbnail, that infolabel resolves to Kodi's
    built-in DefaultUser.png (packed in Textures.xbt), so the staged avatar in
    extras/media/ is never seen. Split the single image control into two: our
    branded avatar when the thumb is empty/default, the real thumbnail otherwise.
    Also repoints the defaultuser.png fallbacks in the profiles settings screen.
    Idempotent (skips if our override path is already present). Scripted + verified.
    """
    changed = False
    skin = kodi_home / "addons" / "skin.bingie" / "1080i"

    bingie = skin / "IncludesBingie.xml"
    if bingie.exists():
        text = bingie.read_text(encoding="utf-8")
        if PROFILE_AVATAR_OVERRIDE not in text:
            pattern = re.compile(
                r'(?P<head><!--Profile Picture-->\s*<control type="image">)'
                r"(?P<geo>.*?)"
                r'<texture background="true">\$INFO\[System\.ProfileThumb\]</texture>'
                r"(?P<tail>\s*</control>)",
                re.DOTALL,
            )

            def _repl(m: "re.Match[str]") -> str:
                geo = m.group("geo")
                return (
                    m.group("head")
                    + "\n\t\t\t\t\t\t<visible>String.IsEmpty(System.ProfileThumb) | "
                    "String.IsEqual(System.ProfileThumb,DefaultUser.png)</visible>"
                    + geo
                    + f'<texture background="true">{PROFILE_AVATAR_OVERRIDE}</texture>'
                    + m.group("tail")
                    + '\n\t\t\t\t\t<!--Profile Picture (custom thumb)-->\n\t\t\t\t\t<control type="image">'
                    + "\n\t\t\t\t\t\t<visible>!String.IsEmpty(System.ProfileThumb) + "
                    "!String.IsEqual(System.ProfileThumb,DefaultUser.png)</visible>"
                    + geo
                    + '<texture background="true">$INFO[System.ProfileThumb]</texture>'
                    + m.group("tail")
                )

            new_text, n = pattern.subn(_repl, text, count=1)
            if n != 1:
                raise SystemExit("patch_profile_avatar: profile picture control not found in IncludesBingie.xml")
            bingie.write_text(new_text, encoding="utf-8")
            changed = True

    profile_settings = skin / "SettingsProfile.xml"
    if profile_settings.exists():
        ptext = profile_settings.read_text(encoding="utf-8")
        new_ptext = ptext.replace(
            'fallback="defaultuser.png"',
            f'fallback="{PROFILE_AVATAR_OVERRIDE}"',
        )
        if new_ptext != ptext:
            profile_settings.write_text(new_ptext, encoding="utf-8")
            changed = True

    return changed


def ensure_anilist_title_language(kodi_home: Path) -> bool:
    """Keep helper title_language on english (widgets/info labels)."""
    settings_xml = kodi_home / "userdata" / "addon_data" / ANILIST_HELPER_ID / "settings.xml"
    if not settings_xml.exists():
        return False
    text = settings_xml.read_text(encoding="utf-8")
    pattern = r'(<setting id="title_language"[^>]*>)([^<]*)(</setting>)'
    match = re.search(pattern, text)
    if match:
        if match.group(2).strip() == "english":
            return False
        text, n = re.subn(pattern, r"\g<1>english\g<3>", text, count=1)
        if not n:
            return False
    else:
        text = text.replace(
            "</settings>",
            '    <setting id="title_language" default="true">english</setting>\n</settings>',
            1,
        )
    settings_xml.write_text(text, encoding="utf-8")
    return True


def apply_file_patches(kodi_home: Path) -> list[str]:
    skin = kodi_home / "addons" / "skin.bingie"
    applied = []

    copies = [
        (PATCHES / "IncludesPaths.xml", skin / "1080i" / "IncludesPaths.xml"),
        (PATCHES / "IncludesDialogVideoInfo.xml", skin / "1080i" / "IncludesDialogVideoInfo.xml"),
        # Info-dialog plot OSD carrying the 8nime "See Episodes" button (red accent)
        # that opens the clicked entry's All-Seasons view.
        (PATCHES / "Custom_1122_CustomPlotOSD.xml", skin / "1080i" / "Custom_1122_CustomPlotOSD.xml"),
        # Spotlight hero next-up episode resolves via the 8nime helper for plugin
        # items (no library DBID) so the spotlight "Play" has a playable episode.
        (PATCHES / "IncludesBingie.xml", skin / "1080i" / "IncludesBingie.xml"),
        (PATCHES / "IncludesDefaultSkinSettings.xml", skin / "1080i" / "IncludesDefaultSkinSettings.xml"),
        (PATCHES / "Custom_1119_Category2_Hub.xml", skin / "1080i" / "Custom_1119_Category2_Hub.xml"),
        (PATCHES / "Custom_1117_Categories_Hub.xml", skin / "1080i" / "Custom_1117_Categories_Hub.xml"),
        (PATCHES / "shortcuts" / "movies.DATA.xml", skin / "shortcuts" / "movies.DATA.xml"),
        (PATCHES / "shortcuts" / "shows.DATA.xml", skin / "shortcuts" / "shows.DATA.xml"),
        (PATCHES / "shortcuts" / "searchmenu.DATA.xml", skin / "shortcuts" / "searchmenu.DATA.xml"),
        (PATCHES / "shortcuts" / "mainmenu.DATA.xml", skin / "shortcuts" / "mainmenu.DATA.xml"),
        (PATCHES / "shortcuts" / "moviehub.DATA.xml", skin / "shortcuts" / "moviehub.DATA.xml"),
        # Power menu: "Exit" (not "Exit Bingie") + a "Change provider" entry that
        # opens the 8nime Bingie Helper settings (playback provider selector).
        (PATCHES / "shortcuts" / "powermenu.DATA.xml", skin / "shortcuts" / "powermenu.DATA.xml"),
        (PATCHES / "IncludesHomeBingie.xml", skin / "1080i" / "IncludesHomeBingie.xml"),
        (PATCHES / "Custom_1101_StartUp.xml", skin / "1080i" / "Custom_1101_StartUp.xml"),
        (PATCHES / "Custom_1102_StartUp2.xml", skin / "1080i" / "Custom_1102_StartUp2.xml"),
        (PATCHES / "screensaver-bingie.xml", skin / "1080i" / "screensaver-bingie.xml"),
    ]
    for src, dest in copies:
        if not src.exists():
            raise SystemExit(f"Missing patch file: {src}")
        shutil.copy2(src, dest)
        applied.append(dest.relative_to(kodi_home))

    generated = skin / "1080i" / "script-skinshortcuts-includes.xml"
    if generated.exists():
        generated.unlink()
        print("  removed script-skinshortcuts-includes.xml (regenerated on Kodi start)")

    return [str(p) for p in applied]


def verify_patches(kodi_home: Path) -> None:
    paths_xml = kodi_home / "addons" / "skin.bingie" / "1080i" / "IncludesPaths.xml"
    text = paths_xml.read_text(encoding="utf-8")
    info_section, hub_section = text.split("ActionAdvantureMoviesWidget", 1)
    if "plugin.video.tmdb.bingie.helper" in info_section:
        raise SystemExit("Verification failed: TMDb helper still in info Path_* section")
    if ANILIST_HELPER_ID not in info_section:
        raise SystemExit("Verification failed: AniList helper missing from info Path_* section")
    if re.search(r"tmdb\.bingie\.helper.*info=(?:discover|trakt_|random_)", hub_section):
        raise SystemExit("Verification failed: TMDb helper widgets still in hub/category section")
    if ANILIST_HELPER_ID not in hub_section:
        raise SystemExit("Verification failed: AniList helper paths missing from hub/category section")


def verify_live_profile(kodi_home: Path) -> list[str]:
    """Automated checks on the live Kodi profile (run before manual UI testing)."""
    skin = kodi_home / "addons" / "skin.bingie"
    addons = kodi_home / "addons"
    checks: list[tuple[str, bool]] = []

    def ok(label: str, passed: bool) -> None:
        checks.append((label, passed))

    ok("plugin.video.otaku installed", (addons / "plugin.video.otaku" / "addon.xml").exists())
    ok("context.otaku installed", (addons / "context.otaku" / "addon.xml").exists())
    ok(f"{ANILIST_HELPER_ID} installed", (addons / ANILIST_HELPER_ID / "addon.xml").exists())
    ok(f"{OPTIKLEAN_ID} installed", (addons / OPTIKLEAN_ID / "addon.xml").exists())
    ok(f"{DEXE_REPO_ID} installed", (addons / DEXE_REPO_ID / "addon.xml").exists())

    import sqlite3

    db_path = kodi_home / "userdata" / "Database" / "Addons33.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        rows = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT addonID, enabled FROM installed WHERE addonID IN (?, ?, ?, ?)",
                ("plugin.video.otaku", "context.otaku", ANILIST_HELPER_ID, OPTIKLEAN_ID),
            )
        }
        conn.close()
        ok("context.otaku enabled in Addons33.db", rows.get("context.otaku") == 1)
        ok("plugin.video.otaku enabled in Addons33.db", rows.get("plugin.video.otaku") == 1)
        ok(f"{ANILIST_HELPER_ID} enabled in Addons33.db", rows.get(ANILIST_HELPER_ID) == 1)
        ok(f"{OPTIKLEAN_ID} enabled in Addons33.db", rows.get(OPTIKLEAN_ID) == 1)

        # Every shipped addon (incl. script.module.* deps + skin.bingie) must be
        # enabled, else Kodi can't resolve `import requests` or load the skin.
        conn = sqlite3.connect(db_path)
        state = dict(conn.execute("SELECT addonID, enabled FROM installed").fetchall())
        conn.close()
        shipped = {
            f.name
            for f in addons.iterdir()
            if f.is_dir() and f.name != "packages" and (f / "addon.xml").exists()
        }
        disabled = sorted(a for a in shipped if state.get(a, 0) != 1)
        ok(
            "all shipped addons enabled (deps + skin)"
            + (f" [disabled: {', '.join(disabled)}]" if disabled else ""),
            not disabled,
        )
        ok("skin.bingie enabled in Addons33.db", state.get("skin.bingie") == 1)
        ok("script.module.requests enabled in Addons33.db", state.get("script.module.requests") == 1)
    else:
        ok("Addons33.db present", False)

    paths = (skin / "1080i" / "IncludesPaths.xml").read_text(encoding="utf-8")
    info_paths, hub = paths.split("ActionAdvantureMoviesWidget", 1)
    ok("info Path_* section uses AniList helper", ANILIST_HELPER_ID in info_paths)
    ok("info Path_* section has no TMDb helper", "plugin.video.tmdb.bingie.helper" not in info_paths)
    ok("Path_Cast uses AniList helper", "info=cast" in info_paths and ANILIST_HELPER_ID in info_paths)
    ok("hub/category section uses AniList helper", ANILIST_HELPER_ID in hub)
    ok("Path_MyList → trakt_favorites shape", "info=trakt_favorites" in paths)
    ok("DefWidget1 → trakt_trending tv", "info=trakt_trending" in paths and "tmdb_type=tv" in paths)
    ok("hub labels avoid Trakt LOCALIZE ids", "$LOCALIZE[31337]" not in hub and "$LOCALIZE[31326]" not in hub)
    ok("hub labels avoid IMDB LOCALIZE ids", "$LOCALIZE[31277]" not in hub and "$LOCALIZE[31443]" not in hub)
    ok("Home hub: Trending row global (not season-locked)", "Trending Now" in paths)
    ok(
        "Home hub: Trending != Popular, Top Rated != Top 100 (distinct pools)",
        "list_slug=all-time-popular-tv" in paths
        and "Top 100 Anime" not in paths
        and "list_slug=last-season-tv" in paths,
    )
    ok(
        "TV hub rows = Airing Now / Last Season / Popular",
        bool(re.search(r'DefTVShowHubName">\s*<value>Airing Now<', paths))
        and bool(re.search(r'DefTVShowHub1Name">\s*<value>Last Season<', paths))
        and bool(re.search(r'DefTVShowHub2Name">\s*<value>Popular<', paths)),
    )
    ok(
        "Movies hub rows = New Movies / Popular",
        bool(re.search(r'DefMovieHubName">\s*<value>New Movies<', paths))
        and bool(re.search(r'DefMovieHub1Name">\s*<value>Popular<', paths)),
    )
    ok(
        "TV 'Last Season' uses previous-season cohort",
        "list_slug=last-season-tv" in paths,
    )
    ok(
        "TV/Movie 'Popular' is all-time (not season-locked trakt_popular)",
        "list_slug=all-time-popular-tv" in paths
        and "list_slug=all-time-popular-movies" in paths,
    )
    ok(
        "Hubs no longer use season-locked trakt_popular",
        not re.search(r'Def(?:TVShow|Movie)Hub\d?Content">\s*<value>[^<]*info=trakt_popular', paths),
    )
    ok(
        "Shows/Movies hubs dropped Trending rows",
        not re.search(r'Def(?:TVShow|Movie)Hub\d?Content">\s*<value>[^<]*info=trakt_trending', paths),
    )

    moviehub_data = (skin / "shortcuts" / "moviehub.DATA.xml").read_text(encoding="utf-8")
    ok(
        "moviehub.DATA.xml is 2 rows (no DefMovieHub2 shortcut)",
        moviehub_data.count("<shortcut>") == 2 and "DefMovieHub2" not in moviehub_data,
    )

    power_data = (skin / "shortcuts" / "powermenu.DATA.xml").read_text(encoding="utf-8")
    ok(
        "powermenu.DATA.xml: 'Exit' label (not 'Exit Bingie' #31160)",
        "<label>Exit</label>" in power_data and "$LOCALIZE[31160]" not in power_data,
    )
    ok(
        "powermenu.DATA.xml: 'Change provider' opens helper settings",
        "Change provider" in power_data
        and "Addon.OpenSettings(%s)" % ANILIST_HELPER_ID in power_data,
    )

    movies_data = (skin / "shortcuts" / "movies.DATA.xml").read_text(encoding="utf-8")
    shows_data = (skin / "shortcuts" / "shows.DATA.xml").read_text(encoding="utf-8")
    search_data = (skin / "shortcuts" / "searchmenu.DATA.xml").read_text(encoding="utf-8")
    ok("movies.DATA.xml browse via helper", ANILIST_HELPER_ID in movies_data)
    ok("shows.DATA.xml browse via helper", ANILIST_HELPER_ID in shows_data)
    ok(
        "shows/movies submenus have NO Otaku links",
        "plugin.video.otaku" not in movies_data and "plugin.video.otaku" not in shows_data,
    )
    ok(
        "submenus drop redundant Genres->Categories (1119 only on main menu)",
        "ActivateWindow(1119" not in movies_data
        and "ActivateWindow(1119" not in shows_data,
    )
    ok(
        "Shows submenu = All shows + Specials (no Genres, no empty In Progress)",
        "info=dir_tv" in shows_data
        and "info=dir_ova" in shows_data
        and "info=anilist_nextup" not in shows_data
        and shows_data.count("<shortcut>") == 2,
    )
    ok(
        "Movies submenu = All movies only (no Genres, no series-like OVA)",
        "info=dir_movie" in movies_data
        and "info=dir_ova" not in movies_data
        and movies_data.count("<shortcut>") == 1,
    )
    ok(
        "searchmenu.DATA.xml routes to AniList search window (no Otaku search)",
        "plugin.video.otaku/search" not in search_data
        and "ActivateWindow(1109)" in search_data,
    )

    search_inc = skin / "1080i" / "IncludesBingieSearch.xml"
    if search_inc.exists():
        search_text = search_inc.read_text(encoding="utf-8")
        ok(
            "search window uses AniList helper",
            "plugin.video.8nime.bingie.helper/?info=search" in search_text,
        )
        ok(
            "search window has no TMDb helper",
            "plugin.video.tmdb.bingie.helper" not in search_text,
        )
        ok(
            "SearchTMDBAll spans all formats (tmdb_type=both)",
            bool(
                re.search(
                    r'<variable name="SearchTMDBAll">.*?tmdb_type=both',
                    search_text,
                    re.DOTALL,
                )
            ),
        )
        ok(
            "search hint is AniList-neutral (no TMDb branding)",
            "$LOCALIZE[31186]" not in search_text and "Search Anime" in search_text,
        )
        ok(
            "static suggestions use AniList labels",
            ">Trending Anime<" in search_text and ">Popular Anime<" in search_text,
        )
        ok(
            "static suggestions dropped TMDb LOCALIZE labels",
            "$LOCALIZE[31432]" not in search_text and "$LOCALIZE[31453]" not in search_text,
        )
    else:
        ok("IncludesBingieSearch.xml present", False)

    search_win = skin / "1080i" / "Custom_1109_BingieSearch.xml"
    if search_win.exists():
        win_text = search_win.read_text(encoding="utf-8")
        ok(
            "search window renders single AniList Results list",
            'value="$VAR[SearchTMDBAll]"' in win_text
            and 'value="Results"' in win_text,
        )
        ok(
            "search window dropped Otaku/TMDb skinshortcuts templates",
            "skinshortcuts-template-search</include>" not in win_text
            and "skinshortcuts-template-tmdbsearch</include>" not in win_text,
        )
        ok(
            "autocomplete uses AniList helper (not Google)",
            "plugin.video.8nime.bingie.helper/?info=autocomplete" in win_text
            and "plugin.program.autocompletion" not in win_text,
        )
    else:
        ok("Custom_1109_BingieSearch.xml present", False)

    cat_hub = (skin / "1080i" / "Custom_1119_Category2_Hub.xml").read_text(encoding="utf-8")
    ok("category hub has 15 genre tiles", cat_hub.count('<item id="') == 15)
    ok(
        "category tiles stash AniList path (categorypath) for 1117",
        cat_hub.count("SetProperty(categorypath,") == 15
        and "plugin.video.otaku" not in cat_hub,
    )
    cat_browse = (skin / "1080i" / "Custom_1117_Categories_Hub.xml").read_text(encoding="utf-8")
    ok(
        "1117 browse is single AniList-driven container (no stale category soup)",
        "Window(Home).Property(categorypath)" in cat_browse
        and "String.IsEqual(Window(Home).Property(category)," not in cat_browse,
    )
    ok(
        "1117 browse uses AniList helper (not TMDb/Otaku)",
        "plugin.video.otaku" not in cat_browse
        and "plugin.video.tmdb.bingie.helper" not in cat_browse,
    )

    if MEDIA_SRC.is_dir():
        media_root = skin / "extras" / "media"
        srcs = [p for p in MEDIA_SRC.rglob("*") if p.is_file()]
        mismatched = [
            p.relative_to(MEDIA_SRC).as_posix()
            for p in srcs
            if not (media_root / p.relative_to(MEDIA_SRC)).exists()
            or (media_root / p.relative_to(MEDIA_SRC)).stat().st_size != p.stat().st_size
        ]
        ok(
            f"skin media mirrored to extras/media ({len(srcs)} file(s))",
            bool(srcs) and not mismatched,
        )
        # NOTE: the logo override is verified via the generator-repointed <texture>
        # (see "Home logo repointed outside Textures.xbt" below). Loose drops into
        # media/ are intentionally NOT done - the xbt wins over them.
        if (MEDIA_SRC / "bingie_splash.png").is_file():
            mask = skin / "1080i" / "Custom_1103_StartUpMask.xml"
            ok(
                "boot splash points to bingie_splash.png",
                mask.exists() and "extras/media/bingie_splash.png" in mask.read_text(encoding="utf-8"),
            )

    otaku_settings = kodi_home / "userdata" / "addon_data" / "plugin.video.otaku" / "settings.xml"
    if otaku_settings.exists():
        otaku_text = otaku_settings.read_text(encoding="utf-8")
        ok("Otaku settings use version 2", 'version="2"' in otaku_text)
        ok("Otaku browser.api=anilist", "browser.api" in otaku_text and ">anilist<" in otaku_text)
        ok("Otaku changelog suppressed", "showchangelog" in otaku_text and ">1<" in otaku_text)
    else:
        ok("Otaku settings present", False)

    skin_settings = kodi_home / "userdata" / "addon_data" / "skin.bingie" / "settings.xml"
    if skin_settings.exists():
        skin_text = skin_settings.read_text(encoding="utf-8")
        ok(
            "Bingie info dialog enabled",
            bool(
                re.search(
                    r'<setting id="usebingieinfodialog"[^>]*>true</setting>',
                    skin_text,
                )
            ),
        )
        ok(
            "Trakt Manager button disabled (skin setting)",
            bool(re.search(r'<setting id="videoinfo_button_trakt"[^>]*>false</setting>', skin_text)),
        )
    else:
        ok("skin.bingie settings present", False)

    defaults = skin / "1080i" / "IncludesDefaultSkinSettings.xml"
    if defaults.exists():
        dtext = defaults.read_text(encoding="utf-8")
        ok(
            "skin first-run defaults no longer force-enable Trakt UI",
            "Skin.SetBool(videoinfo_button_trakt)" not in dtext
            and "Skin.SetBool(ratings_Trakt)" not in dtext,
        )
        ok(
            "skin first-run defaults keep Cast/MoreInfo buttons",
            "Skin.SetBool(videoinfo_button_moreinfo)" in dtext
            and "Skin.SetBool(videoinfo_button_cast)" in dtext,
        )
    else:
        ok("IncludesDefaultSkinSettings.xml present", False)

    dialog_live = skin / "1080i" / "IncludesDialogVideoInfo.xml"
    if dialog_live.exists():
        dlg = dialog_live.read_text(encoding="utf-8")
        ok(
            "Trakt Manager buttons hard-disabled (no setting gate left)",
            "Skin.HasSetting(videoinfo_button_trakt)</visible>" not in dlg,
        )
    else:
        ok("IncludesDialogVideoInfo.xml present", False)

    home_live = skin / "1080i" / "IncludesHomeBingie.xml"
    if home_live.exists():
        htext = home_live.read_text(encoding="utf-8")
        ok(
            "Home logo repointed outside Textures.xbt (extras/media)",
            "<texture>special://skin/extras/media/bingie_logo.png</texture>" in htext
            and "<texture>home/bingie_logo.png</texture>" not in htext,
        )
    else:
        ok("IncludesHomeBingie.xml present", False)

    ok(
        "logo image staged in extras/media",
        (skin / "extras" / "media" / "bingie_logo.png").is_file(),
    )

    bingie_live = skin / "1080i" / "IncludesBingie.xml"
    if bingie_live.exists():
        btext = bingie_live.read_text(encoding="utf-8")
        ok(
            "profile avatar uses staged defaultuser (custom + thumb fallback)",
            PROFILE_AVATAR_OVERRIDE in btext
            and "String.IsEqual(System.ProfileThumb,DefaultUser.png)" in btext,
        )
    else:
        ok("IncludesBingie.xml present", False)

    ok(
        "avatar image staged in extras/media",
        (skin / "extras" / "media" / "defaultuser.png").is_file(),
    )

    ok(
        "skinshortcuts cache cleared",
        not (skin / "1080i" / "script-skinshortcuts-includes.xml").exists(),
    )

    failed = [label for label, passed in checks if not passed]
    print("\n  Live profile checks:")
    for label, passed in checks:
        print(f"    [{'ok' if passed else 'FAIL'}] {label}")
    if failed:
        raise SystemExit(f"Live profile verification failed: {', '.join(failed)}")
    return [label for label, _ in checks]


def _newest_existing(candidates: list[Path]) -> Path | None:
    """Return the existing dir with the newest kodi.log (i.e. the active profile)."""
    best: Path | None = None
    best_mtime = -1.0
    for path in candidates:
        try:
            if not path.is_dir():
                continue
        except OSError:
            continue
        log = path / "kodi.log"
        try:
            mtime = log.stat().st_mtime if log.exists() else path.stat().st_mtime
        except OSError:
            continue
        if mtime > best_mtime:
            best_mtime = mtime
            best = path
    return best


def _platform_kodi_candidates() -> list[Path]:
    """Standard Kodi data dirs per OS (Windows / macOS / Linux / Android)."""
    home = Path.home()
    candidates: list[Path] = []
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            packages = Path(local) / "Packages"
            if packages.is_dir():
                for pkg in packages.glob("XBMCFoundation.Kodi_*"):
                    candidates.append(pkg / "LocalCache" / "Roaming" / "Kodi")
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.append(Path(appdata) / "Kodi")
    elif sys.platform == "darwin":
        candidates.append(home / "Library" / "Application Support" / "Kodi")
    else:
        # Android reports as linux; its app-data paths are tried first (only used
        # if they exist), then desktop-Linux native / snap / flatpak locations.
        candidates += [
            Path("/sdcard/Android/data/org.xbmc.kodi/files/.kodi"),
            Path("/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi"),
            home / ".kodi",
            home / "snap" / "kodi" / "common" / ".kodi",
            home / ".var" / "app" / "tv.kodi.Kodi" / "data" / ".kodi",
        ]
    return candidates


def resolve_kodi_home() -> Path | None:
    """Locate the Kodi profile across Windows, macOS, Linux and Android TV.

    Order: explicit $KODI_HOME -> repo WSL/Windows resolver (deploy.find_kodi_home,
    handles the /mnt/c Store + Roaming layout) -> native per-OS locations. When more
    than one exists, the profile with the newest kodi.log wins.
    """
    env = os.environ.get("KODI_HOME")
    if env and Path(env).is_dir():
        return Path(env)
    try:
        via_deploy = deploy.find_kodi_home()
    except Exception:
        via_deploy = None
    native = _newest_existing(_platform_kodi_candidates())
    options = [p for p in (via_deploy, native) if p]
    if not options:
        return None
    return _newest_existing(options) or options[0]


# NOTE: dropping loose PNGs into skin.bingie/media/** does NOT override the logo.
# Kodi reads the compiled Textures.xbt with PRIORITY over loose files (confirmed in
# Kodi's skinning manual and by the skin devs), so a media/bingie_logo.png next to a
# logo already baked into the xbt is simply ignored. The working override is done in
# the generator instead: it repoints the logo <texture> refs at extras/media/ (a path
# NOT inside the xbt), and copy_media mirrors the staged file there. Hence this map is
# empty - there are no skin/media/** drops worth doing.
MEDIA_OVERRIDE_TARGETS: dict[str, list[str]] = {}
# The boot splash texture (Custom_1103) loads this exact file; repoint it at the
# user's splash so the staged image actually shows on startup.
SPLASH_SOURCE = "bingie_splash.png"
SPLASH_TEXTURE = "special://skin/extras/media/bingie_splash.png"


def copy_media(kodi_home: Path) -> list[str]:
    """Copy bundled skin media (config/branding/**) into skin.bingie/extras/media/**.

    extras/media/ is a loose dir NOT packed into Textures.xbt, so the skin XML
    (logo textures repointed by the generator, plus the splash mask) loads these
    files directly. pathlib + shutil keep this byte-identical on every platform.
    """
    if not MEDIA_SRC.is_dir():
        return []
    skin_root = kodi_home / "addons" / "skin.bingie"
    target_root = skin_root / "extras" / "media"
    copied: list[str] = []
    by_name: dict[str, Path] = {}
    for src in sorted(MEDIA_SRC.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(MEDIA_SRC)
        dest = target_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(rel.as_posix())
        by_name[src.name] = src

    for name, targets in MEDIA_OVERRIDE_TARGETS.items():
        src = by_name.get(name)
        if not src:
            continue
        for target in targets:
            dest = skin_root / target
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied.append(target)

    # Remove dead loose overrides left by the earlier (wrong) approach: files dropped
    # into media/** are shadowed by Textures.xbt, so they never displayed and only add
    # confusion. None of these existed in the stock skin (the logo/avatar live in the
    # xbt), so deleting our leftovers is safe.
    for stale in ("media/bingie_logo.png", "media/home/bingie_logo.png", "media/defaultuser.png"):
        sp = skin_root / stale
        if sp.is_file():
            sp.unlink()
    home_dir = skin_root / "media" / "home"
    if home_dir.is_dir() and not any(home_dir.iterdir()):
        home_dir.rmdir()
    return copied


def patch_splash_mask(kodi_home: Path) -> bool:
    """Point the startup splash (Custom_1103) at the staged bingie_splash.png and fix duration."""
    mask = kodi_home / "addons" / "skin.bingie" / "1080i" / "Custom_1103_StartUpMask.xml"
    if not mask.exists():
        return False
    text = mask.read_text(encoding="utf-8")
    new_text = re.sub(
        r'(<texture background="true">)[^<]+(</texture>)',
        rf"\g<1>{SPLASH_TEXTURE}\g<2>",
        text,
        count=1,
    )
    new_text = re.sub(
        r'AlarmClock\(startup,ClearProperty\(StartupMask,home\),00:\d+,silent\)',
        'AlarmClock(startup,ClearProperty(StartupMask,home),00:03,silent)',
        new_text,
    )
    if new_text != text:
        mask.write_text(new_text, encoding="utf-8")
        return True
    return False


def write_wizard_settings(kodi_home: Path) -> bool:
    """Pre-populate wizard state so first-run prompts are skipped."""
    addon_data = kodi_home / "userdata" / "addon_data" / WIZARD_ID
    settings = addon_data / "settings.xml"
    content = (
        "<settings>\n"
        '    <setting id="first_install" type="bool">false</setting>\n'
        '    <setting id="installed" type="text">true</setting>\n'
        '    <setting id="buildname" type="text">8nime</setting>\n'
        '    <setting id="buildversion" type="text">1.0.0</setting>\n'
        '    <setting id="disableupdate" type="bool">true</setting>\n'
        '    <setting id="autoclean" type="bool">false</setting>\n'
        '    <setting id="wizardlog" type="bool">false</setting>\n'
        "</settings>\n"
    )
    if settings.exists() and settings.read_text(encoding="utf-8") == content:
        return False
    addon_data.mkdir(parents=True, exist_ok=True)
    settings.write_text(content, encoding="utf-8")
    return True


def apply(kodi_home: Path | None = None, verify_live: bool = True) -> None:
    # verify_live=False skips the checks that read a live Kodi profile
    # (Addons33.db enable-state + active-profile assertions). The headless build
    # assembler has no Addons33.db — Kodi rebuilds it and enables addons on first
    # scan after the wizard extracts the build — so only the file-based
    # verify_patches applies there.
    ensure_patches_built()
    kodi_home = kodi_home or resolve_kodi_home()
    if not kodi_home:
        raise SystemExit("Kodi profile not found.")

    print(f"Kodi profile: {kodi_home}")
    ensure_otaku_stack(kodi_home)
    ensure_optiklean(kodi_home)
    ensure_anilist_helper(kodi_home)

    applied = apply_file_patches(kodi_home)
    print(f"  applied {len(applied)} skin patch files")
    media = copy_media(kodi_home)
    if media:
        print(f"  copied {len(media)} skin media file(s): {', '.join(media)}")
    if patch_splash_mask(kodi_home):
        print(f"  repointed boot splash -> {SPLASH_TEXTURE}")
    if patch_includes_bingie(kodi_home):
        print("  patched IncludesBingie.xml (removed legacy id_guard)")
    if patch_tmdbbingie_loader(kodi_home):
        print("  patched Includes.xml (Container 17195 -> request-backed details)")
    if patch_episode_sort_order(kodi_home):
        print("  patched View_527_Bingie_Seasons.xml (episode list -> newest-first)")
    if patch_change_provider_blade(kodi_home):
        print("  patched MyVideoNav.xml (added Change provider to options drawer)")
    if patch_profile_avatar(kodi_home):
        print(f"  patched profile avatar -> {PROFILE_AVATAR_OVERRIDE}")
    if patch_includes_bingie_search(kodi_home):
        print("  patched IncludesBingieSearch.xml (search -> AniList helper)")
    if patch_custom_search_window(kodi_home):
        print("  patched Custom_1109_BingieSearch.xml (single AniList Results + autocomplete)")
    if ensure_anilist_title_language(kodi_home):
        print("  set AniList helper title_language to english")

    skin_settings = kodi_home / "userdata" / "addon_data" / "skin.bingie" / "settings.xml"
    otaku_settings = kodi_home / "userdata" / "addon_data" / "plugin.video.otaku" / "settings.xml"
    skin_changes = merge_settings_snippet(
        skin_settings, PATCHES / "skin.bingie.settings.snippet.xml"
    )
    otaku_changes = merge_otaku_settings(
        otaku_settings, PATCHES / "otaku.settings.snippet.xml", kodi_home
    )
    finalize_otaku_settings(otaku_settings, kodi_home)
    print(f"  merged skin settings ({skin_changes} values)")
    print(f"  merged Otaku settings ({otaku_changes} values)")

    if write_wizard_settings(kodi_home):
        print("  wrote wizard settings (first-run bypassed)")

    verify_patches(kodi_home)
    print("  patch file verification passed")
    if verify_live:
        verify_live_profile(kodi_home)
        print("  live profile verification passed")
    else:
        print("  skipping live-profile verification (headless build)")


MANUAL_CHECKLIST = """
Manual checks (after fully quitting and reopening Kodi):
  1. Sidebar → Search opens AniList search window (1109)
  2. Home widgets show anime posters
  3. TV hub: Airing Now / Last Season / Popular (3 distinct pools, little overlap)
  4. Movies hub: New Movies / Popular (2 rows)
  5. Anime hub submenus: Shows = All shows + Specials; Movies = All movies (genre browse lives on the main-menu Categories tile)
  6. Main-menu Categories shows anime genres; each tile opens window 1117
  7. My List shows AniList planning list (after AniList login via helper Settings -> Log in with AniList)
  8. Selecting a widget item opens Bingie More Info (cast, similar, plot from AniList); Play goes to Otaku
  9. kodi.log has no repeated Otaku import / dependency errors
"""


def main() -> int:
    apply()
    print("\nAnime Bingie patches applied. Fully quit and reopen Kodi.")
    print("Log into AniList via the helper: Settings -> Log in with AniList (scan the QR) for My List / Continue Watching.")
    print(MANUAL_CHECKLIST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
