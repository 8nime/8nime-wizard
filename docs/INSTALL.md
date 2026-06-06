# 8nime Installation Guide

## Windows (Microsoft Store Kodi)

Your Kodi install uses the Store package path:

```
C:\Users\bruno\AppData\Local\Packages\XBMCFoundation.Kodi_4n2hpmxwrvr6p\LocalCache\Roaming\Kodi
```

Deploy from WSL:

```bash
python3 /home/devil/kodi-build/scripts/deploy-windows.py
```

Then **fully quit Kodi** (not just minimize) and reopen it.

## Prerequisites

- Kodi 21 Omega (or 20 Nexus minimum)
- Unknown sources enabled
- GitHub Pages hosting (for remote wizard configs) OR local file source

## Option A: Full install via repository

### Step 1 — Host the project

```bash
cd kodi-build
./scripts/replace-base-url.sh YOUR_GITHUB_USERNAME
./scripts/package-repo.sh
git init && git add . && git commit -m "Initial 8nime build"
# Push to GitHub, enable Pages on main branch
```

### Step 2 — Add repository in Kodi

1. Settings → File manager → Add source
2. URL: `https://YOUR_GITHUB_USERNAME.github.io/kodi-build/repo/`
3. Name: `8nime`
4. Settings → Add-ons → Install from zip
5. Select `repository.8nime-1.0.0.zip`
6. Install from repository → 8nime Repository → Program add-ons → 8nimeWizard

### Step 3 — Install a build

1. Add-ons → Program add-ons → 8nimeWizard
2. Choose **8nime Free** or **8nime Debrid**
3. Confirm fresh install (wipe recommended on first install)
4. Wait for download and skin switch to Bingie

### Step 4 — Configure

| Task | Path |
|------|------|
| Trakt sync | Skin Settings → Supported addons → TMDb Bingie Helper → Trakt |
| Ratings | Same menu → API Keys → OMDb + MDbList |
| Real-Debrid | Otaku → Tools → Accounts → Real-Debrid |
| Buffering | 8nimeWizard → System Tweaks → Anime Streaming preset |

## Option B: Manual addon install (no build zip)

If build zips are not yet created:

1. Install 8nimeWizard from zip: `repo/zips/plugin.program.8nime.wizard/`
2. Use 8nimeWizard → Addon Installer to install:
   - Bingie Repository → Bingie Skin → TMDb Bingie Helper
   - Hooty Repository → Otaku → Context Menu
3. Set Bingie as default skin
4. Configure menu per `config/guisettings/README.md`

## Bingie anime home screen

After install, verify these sidebar items exist:

- **Anime Series** → Otaku TV Shows
- **Anime Movies** → Otaku Movies
- **Airing Now** → Otaku Airing Anime
- **Calendar** → Otaku Airing Calendar
- **My List** → Trakt Watchlist

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Wizard shows no builds | Check `hosted/builds.txt` URL is reachable; run `replace-base-url.sh` |
| Bingie widgets empty | Authenticate Trakt; ensure Otaku is installed |
| Buffering on Firestick | Apply "Anime Low-End Device" advancedsettings preset |
| Otaku no HD links | Authorize Real-Debrid in Otaku → Tools → Accounts |
| Skin reverts after restart | Reinstall build; ensure guisettings.xml is in build zip |
