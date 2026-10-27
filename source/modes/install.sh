#!/bin/bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)
test -f /srv/unified/compose.yaml
test -f /etc/systemd/system/unified-display.service
for command in cvt xdotool wmctrl xauth; do command -v "$command" >/dev/null; done
mkdir -p /srv/unified/backups
backup=/srv/unified/backups/modes-install-$(date -u +%Y%m%d_%H%M%S).tar.gz
tar -czf "$backup" /etc/systemd/system/unified-display.service /etc/systemd/system/unified-apps.service /etc/nginx/sites-available/unified /srv/unified/compose.yaml /srv/unified/web/index.html /home/workspace/.config/xfce4
chmod 600 "$backup"
install -d -o workspace -g workspace /srv/unified/modes /home/workspace/.local/share/applications
if [ "$source_dir" != /srv/unified/modes ]; then
 for file in controller.py native_core.py desktops.py install-desktops.py prepare-desktop-auth.sh native-integration.py status_server.py index.html patch_xpra.py patch_html5.py patch_html5_ping.py README.md install.sh; do
  install -m 644 "$source_dir/$file" "/srv/unified/modes/$file.next"
  mv -f "/srv/unified/modes/$file.next" "/srv/unified/modes/$file"
 done
fi
chown -R workspace:workspace /srv/unified/modes
python3 /srv/unified/modes/patch_xpra.py
python3 /srv/unified/modes/patch_html5_ping.py
python3 /srv/unified/modes/patch_html5.py
python3 /srv/unified/modes/install-desktops.py
python3 - <<'PY'
from pathlib import Path
base=Path('/home/workspace/.config/xfce4/panel')
for plugin,app in [(17,'terminal'),(18,'files')]:
 for p in (base/('launcher-'+str(plugin))).glob('*.desktop'):
  p.write_text('\n'.join('Exec=/usr/bin/python3 /srv/unified/modes/controller.py launch auto '+app if line.startswith('Exec=') else line for line in p.read_text().splitlines())+'\n')
apps=Path('/home/workspace/.local/share/applications')
for mode,name in [(1,'模式一：三个独立完整桌面'),(2,'模式二：统一完整桌面')]:
 (apps/f'unified-mode-{mode}.desktop').write_text(f'[Desktop Entry]\nType=Application\nName={name}\nExec=/usr/bin/python3 /srv/unified/modes/controller.py mode {mode}\nIcon=preferences-desktop-display\nCategories=Utility;\nTerminal=false\n')
p=Path('/etc/nginx/sites-available/unified');s=p.read_text()
if 'location = /api/mode' not in s:
 i=s.rfind('}');s=s[:i]+' location = /api/mode { proxy_set_header Host $http_host; proxy_pass http://127.0.0.1:8091; }\n'+s[i:];p.write_text(s)
service=Path('/etc/systemd/system/unified-display.service').read_text()
line=next(v for v in service.splitlines() if v.startswith('ExecStart='))
line=line.replace('--resize-display=1280x800','--resize-display=off:1280x800@50')
line+=' --encoding=png --encodings=png --speed=100 --min-speed=100 --quality=100 --min-quality=100 --auto-refresh-delay=0 --keyboard-sync=no --bandwidth-limit=1000000 --bandwidth-detection=no'
drop=Path('/etc/systemd/system/unified-display.service.d');drop.mkdir(exist_ok=True)
(drop/'modes.conf').write_text('[Service]\nEnvironment=XPRA_BATCH_MIN_DELAY=100\nEnvironment=XPRA_BATCH_START_DELAY=100\nExecStart=\n'+line+'\n')
PY
chown -R workspace:workspace /home/workspace/.config/xfce4/panel /home/workspace/.local/share/applications
install -m 644 /srv/unified/modes/index.html /srv/unified/web/index.html
cat > /etc/systemd/system/unified-modes.service <<'UNIT'
[Unit]
Description=Independent host desktops and original unified desktop
After=unified-display.service unified-apps.service unified-desktop-a.service unified-desktop-b.service unified-desktop-c.service
Requires=unified-display.service unified-apps.service
Wants=unified-desktop-a.service unified-desktop-b.service unified-desktop-c.service
[Service]
Type=oneshot
User=workspace
Environment=DISPLAY=:100
Environment=XAUTHORITY=/srv/unified/state/auth/host
ExecStart=/usr/bin/python3 /srv/unified/modes/controller.py start
RemainAfterExit=yes
TimeoutStartSec=180
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
UNIT
cat > /etc/systemd/system/unified-mode-status.service <<'UNIT'
[Unit]
Description=Controlled shared desktop viewport geometry
After=network.target
[Service]
User=workspace
ExecStart=/usr/bin/python3 /srv/unified/modes/status_server.py
Restart=on-failure
RestartSec=3
[Install]
WantedBy=multi-user.target
UNIT
nginx -t
systemctl daemon-reload
systemctl enable unified-modes unified-mode-status unified-desktop-a unified-desktop-b unified-desktop-c
systemctl restart unified-display
systemctl restart unified-apps
systemctl start unified-desktop-a unified-desktop-b unified-desktop-c
systemctl restart unified-modes
systemctl restart unified-mode-status
systemctl reload nginx
runuser -u workspace -- env DISPLAY=:100 XAUTHORITY=/srv/unified/state/auth/host python3 /srv/unified/modes/native-integration.py
printf 'Deployment backup: %s\n' "$backup"
