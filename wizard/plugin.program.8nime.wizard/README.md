# plugin.program.8nime.wizard

**8nime Wizard** — the companion installer and maintenance tool for the 8nime anime build for Kodi 21 (Omega).

It is intentionally minimal: a build installer plus a small set of maintenance tools. No debrid managers, no Trakt/login backups, no themed dashboards — just what's needed to install and look after an 8nime build.

## Menu

The wizard opens as a plain list with three entries:

- **Current Build** — shows the build you're running (or *None*), and flags when an update is available.
- **Builds** — browse and install the available 8nime builds.
- **Maintenance** — housekeeping tools:
  - **Cleaning Tools** — clear cache, packages, thumbnails, crash logs, total cleanup, fresh start.
  - **Addon Tools** — enable/disable addons, remove addons and their data, force update checks.
  - **Logging Tools** — view/upload the Kodi and wizard logs, check for errors.
  - **System Tweaks/Fixes** — system info, scan sources/repositories, convert special paths, non-ASCII scan, reload skin/profile.

The view is a list by default, with no icons or background images.

## Data preservation

Applying a build does **not** wipe your personal data. Before a build installs, the wizard preserves the items you've opted to keep via the `keep*` settings (Settings → Save Data), including:

- `sources.xml`, `favourites.xml`, `profiles.xml`
- `advancedsettings.xml`, `guisettings.xml`, `playercorefactory.xml`
- installed repositories
- Super Favourites

So you won't lose your stuff after applying a build.

## Installation

Install from the **8nime Repository**, which keeps the wizard updated automatically. The repository can be added from the 8nime file source.

## Credits

Originally derived from drinfernoo's OpenWizard, since stripped down and ported to Kodi 21 / Python 3 for the 8nime build.
