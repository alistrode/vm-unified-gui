#!/bin/bash
set -euo pipefail
systemctl is-active unified-display unified-apps unified-status nginx docker
docker ps --format '{{.Names}} {{.Status}}'
for name in unified-a unified-b unified-c; do
 echo "CHECK $name"
 docker inspect --format '{{.Image}} {{.HostConfig.Privileged}} {{.HostConfig.ReadonlyRootfs}}' "$name"
 docker exec "$name" shared-info
 docker exec "$name" python3 -c 'import os; print("display_socket",os.path.exists("/tmp/.X11-unix/X100")); print("user",os.getuid()); import subprocess; p=subprocess.run(["dpkg-query","-W","xvfb","xserver-xorg-core","xfce4","gnome-shell"],capture_output=True,text=True); print("desktop_packages",p.stdout.strip() or "none")'
 docker top "$name"
done
curl -fsS http://127.0.0.1:8080/api/status
echo
journalctl -u unified-display --no-pager -n 8
