#!/bin/bash
set -euo pipefail
case "$1" in a) display=101;; b) display=102;; c) display=103;; *) exit 2;; esac
export DISPLAY=:$display XAUTHORITY=/srv/unified/state/auth/desktop-$1-host
for i in {1..90}; do
 if xdpyinfo >/dev/null 2>&1; then
  target=$(mktemp /srv/unified/state/auth/desktop-$1-next.XXXXXX)
  xauth -f "$XAUTHORITY" nlist | sed 's/^..../ffff/' | xauth -f "$target" nmerge -
  chmod 600 "$target"
  mv "$target" /srv/unified/state/auth/desktop-$1-container
  exit 0
 fi
 sleep 1
done
exit 1
