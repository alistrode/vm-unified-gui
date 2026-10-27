#!/bin/bash
# Only temporary units created by this project's diagnostics; does not stop project desktops.
set -euo pipefail
for unit in unified-browser-observer-v2 unified-focus-observer unified-browser-dependencies; do
 if systemctl cat "$unit" >/dev/null 2>&1; then systemctl stop "$unit"; fi
done
