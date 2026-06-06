# Research: Kodi, OpenWizard, Bingie — Anime Build

## Kodi

Kodi is an open-source media center (v21 Omega current). It supports skins, video addons, and build wizards that snapshot a configured setup into a distributable zip.

**Relevant for anime:**
- Video addons scrape/stream from web sources
- Skins control the home screen UX
- `guisettings.xml` stores skin layout; `advancedsettings.xml` tunes buffering/cache
- Builds bundle addons + skin + settings into one install

## OpenWizard

**Status: Archived (Oct 2022).** Still functional but unmaintained.

| Aspect | Detail |
|--------|--------|
| Repo | https://github.com/a4k-openproject/plugin.program.openwizard |
| Type | Program addon / maintenance wizard |
| Features | Build install, backup/restore, cache clear, Trakt/debrid data save, addon installer |
| Customization | `uservar.py`, `addon.xml`, hosted text files (`builds.txt`, `addons.json`, `advanced.json`) |

**Build install flow:**
1. Wizard reads `builds.txt` from hosted URL
2. User picks a build → downloads zip
3. Installs addons, applies `guisettings.xml`, sets skin
4. Optionally preserves Trakt/debrid/login data

**Why we still use it:** You asked for OpenWizard specifically. It remains the most transparent, forkable wizard for custom builds. Alternatives (Chef Omega, Doomzday) are closed-ecosystem wizards tied to specific repos.

**Our fork:** `plugin.program.animewizard` — branded AnimeWizard, anime-specific hosted configs.

## Bingie Skin

**Status: Active (last update Jan 2026).**

| Aspect | Detail |
|--------|--------|
| Repo | https://github.com/matke-84/skin.bingie |
| Install | https://matke-84.github.io/repository.bingie/repository.bingie-1.0.0.zip |
| Style | Netflix-like: poster rows, left sidebar, hubs |
| Dependencies | TMDb Bingie Helper (widgets, Trakt, ratings) |

**Why Bingie for anime:**
- Lightweight vs Arctic Fuse / Bingie Mod — runs on Firestick
- Widget-driven home screen — ideal for Otaku/Trakt content rows
- TMDb Helper fallback when no local library exists
- 10 widget slots per hub — enough for Trending, Airing, Movies, Continue Watching, etc.

**Required post-install:**
- Authenticate Trakt in TMDb Bingie Helper
- Optional: OMDb + MDbList API keys for ratings
- Configure sidebar shortcuts to Otaku sections

## Anime Addons

### Primary: Otaku (Hooty Repository)

| Aspect | Detail |
|--------|--------|
| Repo | https://goldenfreddy0703.github.io/repository.hooty/ |
| Kodi | 20+ only |
| Content | Anime movies, TV series, airing calendar |
| Features | Sub/dub, skip intro, next episode, watchlists, debrid support |
| Free links | Yes (quality varies) |
| Debrid | Real-Debrid, Premiumize, AllDebrid, TorBox |

**Otaku sections for the build menu:**
- Airing Anime Calendar
- Airing This/Last/Next Season
- Movies / TV Shows
- Trending, Popular, Voted, Top 100
- Genres & Tags, Search

### Secondary (Debrid build): Fen Light, Seren

- **Fen Light** — general VOD with anime category; debrid-only HD
- **Seren** — Otaku's architectural ancestor; premium debrid streaming

## Build Variants

| Build | Target User | Addons | Debrid |
|-------|-------------|--------|--------|
| AnimeVault Free | Casual / no subscription | Bingie, Otaku | Optional |
| AnimeVault Debrid | Quality-focused | Bingie, Otaku, Fen Light, Seren | Required for HD |

## Known Limitations

1. **OpenWizard is archived** — no upstream bug fixes; we own maintenance
2. **Build zips must be created on a real Kodi install** — cannot be generated headlessly
3. **guisettings.xml is machine-generated** — must export from configured reference install
4. **Third-party addon stability** — repos can go offline; Otaku/Hooty is actively maintained (last push Apr 2026)
5. **Legal** — streaming addons access third-party sources; user responsibility

## Alternatives Considered

| Option | Why Not Primary |
|--------|-----------------|
| Diggz Xenon | General-purpose, not anime-focused |
| Chef Omega Wizard | Closed wizard, not forkable |
| Arctic Fuse skin | Heavier, worse on low-end devices |
| GoGoAnime / Fanime | Less maintained than Otaku |
| Aniyomi | Android app, not a Kodi addon |
