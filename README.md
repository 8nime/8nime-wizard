# 8nime Wizard

A minimal Kodi 21 (Omega) build installer and maintenance addon for the 8nime anime build.

## Overview

8nime Wizard is a lightweight Kodi program addon with three menus:

- **Current Build** — shows the build and version currently installed (if any).
- **Builds** — installs the 8nime build: it installs the required repositories, then the addons, then applies the Bingie skin.
- **Maintenance** — housekeeping tools, grouped into:
  - **Cleaning Tools** — clear cache, packages, thumbnails, and addon cache databases.
  - **Addon Tools** — manage and update installed addons.
  - **Logging Tools** — view and clean Kodi and wizard logs.
  - **System Tweaks/Fixes** — common Kodi configuration fixes.

The 8nime build is free to use — no debrid service or paid subscription required.

## Data Preservation

Installing a build does **not** wipe your personal data. The wizard's save-data selection (shown on first run, and configurable in settings) lets you keep your existing:

- Sources (`sources.xml`)
- Favourites and Super Favourites
- Profiles (`profiles.xml`)
- `guisettings.xml` and `advancedsettings.xml`
- `playercorefactory.xml`
- Installed repositories

Anything you choose to keep is preserved across a build install, so you won't lose your setup.

## What's Installed

| Addon | Purpose |
|---|---|
| Bingie | Netflix-style home screen with anime widgets |
| 8nime Bingie Helper | AniList and TMDb metadata provider for Bingie |
| Otaku | Primary anime source — subbed and dubbed movies and series |
| Otaku Context Menu | Right-click actions for Otaku items |
| WatchNixtoons2 | Free anime streaming — broad catalogue, no account required |
| Fanime F | Additional anime source |

## Installing on Kodi

These steps install 8nime Wizard from the 8nime repository.

1. Open Kodi. Go to **Settings → System → Add-ons** and enable **Unknown Sources**.
2. Go to **Settings → File Manager → Add Source**. Enter the URL:
   ```
   https://8nime.github.io/
   ```
   Name it `8nime` and press OK.
3. Go to **Add-ons → Install from zip file**, select the `8nime` source, and install `repository.8nime-1.0.0.zip`.
4. Go to **Add-ons → Install from repository → 8nime Repository → Program add-ons** and install **8nime Wizard**.
5. Open 8nime Wizard from the Program add-ons list, choose **Builds**, select the **8nime** build, and follow the prompts. Kodi will restart when the install is complete.

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
