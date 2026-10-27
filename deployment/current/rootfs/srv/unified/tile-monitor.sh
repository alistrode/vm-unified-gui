#!/bin/bash
set -euo pipefail
export DISPLAY=:100 XAUTHORITY=/srv/unified/state/auth/host
# Tile the three real container windows inside one XFCE desktop.
wmctrl -r 'Container A' -b remove,maximized_vert,maximized_horz || true
wmctrl -r 'Mousepad' -b remove,maximized_vert,maximized_horz || true
wmctrl -r 'File System' -b remove,maximized_vert,maximized_horz || true
sleep 1
wmctrl -r 'Container A' -e 0,0,28,420,720 || true
wmctrl -r 'Mousepad' -e 0,428,28,420,720 || true
wmctrl -r 'File System' -e 0,856,28,420,720 || true
