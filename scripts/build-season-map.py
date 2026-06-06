#!/usr/bin/env python3
"""Offline validator for the AniList -> TVDB season map.

The map is NOT bundled with the addon. At runtime the background service
downloads Fribb/anime-lists `anime-list-full.json` (gzip ~1.2 MB), distils the
compact lookup, and caches it under the addon profile dir -- gated by a TTL and
the GitHub commits-API SHA so the transfer is rarely paid (see
resources/lib/season_map.py).

This script reuses the SAME `build_compact` distiller (imported directly from the
addon module, so there is no second copy to drift) to verify, offline, that the
upstream data still yields the expected season counts.

    python3 scripts/build-season-map.py                 # download + validate
    python3 scripts/build-season-map.py path/to/full.json
    python3 scripts/build-season-map.py path/to/full.json --dump out.json
"""
from __future__ import annotations

import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEASON_MAP_PY = (
    REPO / "addons" / "plugin.video.8nime.bingie.helper" / "resources" / "lib" / "season_map.py"
)
SOURCE_URL = "https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-list-full.json"

# (label, tvdb_id, expected aired+announced TV season numbers present in data)
EXPECT = [
    ("Mushoku Tensei", 371310, {1, 2}),
    ("Jujutsu Kaisen", 377543, {1, 2, 3}),  # S3 announced -> present in map, filtered live by status
]


def _load_build_compact():
    spec = importlib.util.spec_from_file_location("season_map", SEASON_MAP_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_compact


def _load_source(arg: str | None):
    if arg:
        return json.loads(Path(arg).read_text(encoding="utf-8"))
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "kodi-build/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dump = None
    if "--dump" in sys.argv:
        idx = sys.argv.index("--dump")
        dump = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "season_map.dump.json"

    build_compact = _load_build_compact()
    data = _load_source(args[0] if args else None)
    compact = build_compact(data)

    members = compact["tvdb_members"]
    print(
        f"distilled: anilist_keys={len(compact['by_anilist'])} "
        f"mal_keys={len(compact['by_mal'])} tvdb_series={len(members)}"
    )

    ok = True
    for label, tvdb_id, expected in EXPECT:
        recs = members.get(str(tvdb_id)) or []
        tv_seasons = sorted({r[2] for r in recs if r[3] == 1 and r[2] >= 1})
        status = "OK" if set(tv_seasons) == expected else "MISMATCH"
        if status != "OK":
            ok = False
        print(f"  [{status}] {label} (tvdb {tvdb_id}): TV seasons {tv_seasons} (expect {sorted(expected)})")

    if dump:
        Path(dump).write_text(json.dumps(compact, separators=(",", ":")), encoding="utf-8")
        print(f"dumped compact map -> {dump}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
