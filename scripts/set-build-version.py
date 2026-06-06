#!/usr/bin/env python3
"""Stamp version= (and the static url=) on the 8nime *build* entry in builds.txt.

builds.txt holds several blank-line-separated blocks (the wizard addon entry and
the build entry both carry version=/url= lines). This updates ONLY the block
whose name="8nime", leaving the wizard entry untouched. The build zip is always
published under the same release tag + asset name, so url= is constant and the
workflow keeps it correct (self-healing) while bumping version= each run.

    set-build-version.py <path/to/builds.txt> <version>
"""

import re
import sys

# Fixed asset URL: build.yml uploads dist/8nime.zip to the 8nime-repo
# "8nime-build" release with --clobber, so this never changes.
BUILD_URL = "https://github.com/8nime/8nime-repo/releases/download/8nime-build/8nime.zip"


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: set-build-version.py <builds.txt> <version>")
    path, version = sys.argv[1], sys.argv[2]

    with open(path, encoding="utf-8") as f:
        text = f.read()

    blocks = text.split("\n\n")
    for i, block in enumerate(blocks):
        if re.search(r'^name="8nime"\s*$', block, re.M):
            block, n = re.subn(
                r'^version="[^"]*"\s*$',
                'version="{0}"'.format(version),
                block, count=1, flags=re.M,
            )
            if not n:
                raise SystemExit("8nime build entry has no version= line")
            block, n = re.subn(
                r'^url="[^"]*"\s*$',
                'url="{0}"'.format(BUILD_URL),
                block, count=1, flags=re.M,
            )
            if not n:
                raise SystemExit("8nime build entry has no url= line")
            blocks[i] = block
            break
    else:
        raise SystemExit('no name="8nime" build entry found in {0}'.format(path))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(blocks))
    print("set 8nime build version -> {0}, url -> {1}".format(version, BUILD_URL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
