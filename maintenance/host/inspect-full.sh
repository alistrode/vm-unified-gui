#!/bin/bash
python3 - <<'PY'
import xpra,pathlib
print('XPRA_ROOT',xpra.__path__)
for base in xpra.__path__:
 for p in pathlib.Path(base).rglob('*monitor*.py'):
  if 'server' in str(p):print(p)
PY
systemctl show unified-real-apps-build -p ActiveState -p SubState -p ExecMainStatus
journalctl -u unified-real-apps-build -n 8 --no-pager
pgrep -a xfce4-session
pgrep -a xfwm4
uptime
free -m
