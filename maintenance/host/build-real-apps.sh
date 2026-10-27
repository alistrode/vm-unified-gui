#!/bin/bash
set -euo pipefail
root=/srv/unified/rootfs
test -f "$root/etc/debian_version"
cp /etc/apt/sources.list.d/ubuntu.sources "$root/etc/apt/sources.list.d/ubuntu.sources"
cp -a /var/lib/apt/lists/. "$root/var/lib/apt/lists/"
printf '#!/bin/sh\nexit 101\n' > "$root/usr/sbin/policy-rc.d"
chmod 755 "$root/usr/sbin/policy-rc.d"
PACKAGE_ROOT="$root" python3 -u /home/workspace/download-packages.py xterm mousepad thunar dbus-x11
tar -C "$root" -c . | docker import - unified-real-apps:24.04
docker image inspect unified-real-apps:24.04 --format '{{.Id}}'
