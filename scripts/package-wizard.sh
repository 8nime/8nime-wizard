#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIZARD_SRC="$ROOT/wizard/plugin.program.8nime.wizard"
OUT_DIR="$ROOT/dist"
VERSION="$(grep '<addon ' "$WIZARD_SRC/addon.xml" | sed 's/.*version="\([^"]*\)".*/\1/')"
ZIP_NAME="plugin.program.8nime.wizard-${VERSION}.zip"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR/$ZIP_NAME"

# Kodi addon zips require the addon folder as the zip root
cd "$ROOT/wizard"
if command -v zip &>/dev/null; then
  zip -r "$OUT_DIR/$ZIP_NAME" plugin.program.8nime.wizard \
    -x "*.pyc" -x "*__pycache__*" -x "*.git*"
else
  python3 - "$OUT_DIR/$ZIP_NAME" plugin.program.8nime.wizard <<'PY'
import sys, zipfile, os
out, src = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in files:
            if f.endswith('.pyc'): continue
            path = os.path.join(root, f)
            zf.write(path, path)
PY
fi

echo "Created: $OUT_DIR/$ZIP_NAME"
echo "Install in Kodi via: Settings → Add-ons → Install from zip file"
