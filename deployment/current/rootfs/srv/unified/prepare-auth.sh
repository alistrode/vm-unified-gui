#!/bin/bash
set -euo pipefail
export XAUTHORITY=/srv/unified/state/auth/host DISPLAY=:100
for i in {1..60}; do
 if xdpyinfo >/dev/null 2>&1;then
  target=$(mktemp /srv/unified/state/auth/container-next.XXXXXX)
  # FamilyWild permits the same UID's containers with different hostnames.
  xauth -f "$XAUTHORITY" nlist | sed 's/^..../ffff/' | xauth -f "$target" nmerge -
  chmod 600 "$target"
  mv "$target" /srv/unified/state/auth/container
  exit 0
 fi
 sleep 1
done
echo 'Display authorization not ready' >&2
exit 1
