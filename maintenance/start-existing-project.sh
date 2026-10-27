#!/bin/bash
# Consolidates the project's existing service-start commands. No VM power operation.
set -euo pipefail
[ "$(hostname)" = unified-gui ] || { echo 'Only the captured Ubuntu-MultiContainer-GUI guest is supported.' >&2; exit 1; }
[ -f /srv/unified/compose.yaml ]
systemctl start unified-display unified-status unified-mode-status
systemctl start unified-apps
systemctl start unified-desktop-a unified-desktop-b unified-desktop-c
systemctl start unified-modes
