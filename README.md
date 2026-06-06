# 8nimeWizard

Anime-focused Kodi build wizard — installs and maintains the 8nime build on Kodi 21 Omega.

## Overview

8nimeWizard is a Kodi program addon that handles the full lifecycle of the 8nime build. On first run it installs the complete addon suite, applies the Bingie skin with anime-specific layout patches, and walks through initial configuration. After install it provides build updates, backup and restore of Kodi userdata, and routine maintenance (cache clearing, package cleanup). Auto-update and auto-repo-install run silently on Kodi startup.

The 8nime build is free-to-use — no debrid service or paid subscription required.

## What's Installed

| Addon | Purpose |
|---|---|
| Bingie (skin.bingie) | Netflix-style home screen with anime widgets, skip-intro dialog, next-episode prompt |
| 8nime Bingie Helper | AniList and TMDb metadata provider for Bingie; Trakt integration |
| Otaku | Primary anime source — subbed and dubbed movies and series via multiple providers |
| Otaku Context Menu | Right-click actions for Otaku items (mark watched, add to list, etc.) |
| WatchNixtoons2 | Free anime streaming — broad catalogue, no account required |
| Fanime F | Additional anime source for titles not covered by Otaku or WatchNixtoons2 |

## Installing on Kodi

These steps install 8nimeWizard from the 8nime repository.

1. Open Kodi. Go to **Settings → System → Add-ons** and enable **Unknown Sources**.
2. Go to **Settings → File Manager → Add Source**. Enter the URL:
   ```
   https://8nime.github.io/8nime-repo/repo/
   ```
   Name it `8nime` and press OK.
3. Go to **Add-ons → Install from zip file**, select the `8nime` source, and install `repository.8nime-1.0.0.zip`.
4. Go to **Add-ons → Install from repository → 8nime Repository → Program add-ons** and install **8nimeWizard**.
5. Open 8nimeWizard from the Program add-ons list, select the **8nime** build, and follow the prompts. Kodi will restart when the install is complete.

## Post-Install

After the build installs and Kodi restarts:

- **8nime Bingie Helper** — open the addon settings and link your Trakt account for watchlist sync. Optionally add an OMDb or MDbList API key to display ratings. Link your AniList account under the AniList section for list tracking.
- **Otaku** — open the addon settings to select your preferred providers and configure subtitle language preferences.

Browse content via the sidebar categories: Series, Movies, Airing Now, and Calendar.

## Project Structure

```
8nime-wizard/
├── wizard/
│   └── plugin.program.8nime.wizard/   # Kodi addon source
│       ├── addon.xml
│       ├── default.py
│       ├── startup.py
│       ├── uservar.py                  # Build configuration and branding vars
│       └── resources/
├── config/
│   ├── branding/                       # Splash screen, intro video, logo assets
│   ├── skin-patches/anime/             # XML patches applied to Bingie skin
│   └── advancedsettings/               # advancedsettings.xml presets
├── docs/
│   ├── build-info/8nime.txt            # Build manifest (addons, features, post-install)
│   ├── INSTALL.md
│   └── RESEARCH.md
├── scripts/
│   ├── package-wizard.sh               # Produces dist/<addon-id>-<version>.zip
│   ├── apply-anime-bingie.py
│   ├── enable-addons.py
│   ├── enable-bingie.py
│   └── reset-kodi-build.py
└── .github/workflows/release.yml       # Semantic-release CI
```

## Development and Packaging

To build the addon zip locally:

```bash
bash scripts/package-wizard.sh
```

The zip is written to `dist/plugin.program.8nime.wizard-<version>.zip`. This is the file that gets uploaded to the 8nime-repo releases and served by the repository addon.

Version numbers follow [Conventional Commits](https://www.conventionalcommits.org/). Use `fix:`, `feat:`, or `feat!:` / `BREAKING CHANGE:` commit prefixes and CI will determine the next version automatically.

## CI

The `release.yml` workflow triggers on any push to `main` that touches files under `wizard/plugin.program.8nime.wizard/**`. It:

1. Runs semantic-release to determine the next version and update `addon.xml`.
2. Calls `scripts/package-wizard.sh` to produce the zip.
3. Uploads the zip to the `8nime/8nime-repo` GitHub releases under the `plugin.program.8nime.wizard` release tag.
4. Dispatches an `addon-released` repository event to `8nime/8nime-repo` so the metadata index (`addons.xml`) is regenerated automatically.

Commits prefixed with `chore` or containing `[skip ci]` do not trigger a release.

## Related Repositories

| Repository | Purpose |
|---|---|
| [8nime/8nime-wizard](https://github.com/8nime/8nime-wizard) | This repo — wizard addon source, skin patches, build config |
| [8nime/8nime-bingie-helper](https://github.com/8nime/8nime-bingie-helper) | 8nime Bingie Helper — AniList and TMDb integration for the Bingie skin |
| [8nime/8nime-repo](https://github.com/8nime/8nime-repo) | Kodi repository addon and release hosting — serves `addons.xml` and zip files via GitHub Pages |

## License

See [wizard/plugin.program.8nime.wizard/LICENSE](wizard/plugin.program.8nime.wizard/LICENSE).
