#!/bin/bash
# Equivalent entry points for the installed, source-guarded display fixes.
set -euo pipefail
[ "$(hostname)" = unified-gui ]
python3 /srv/unified/modes/patch_xpra.py
python3 /srv/unified/modes/patch_html5_ping.py
python3 /srv/unified/modes/patch_html5.py
python3 /srv/unified/modes/install-desktops.py
install -m 644 /srv/unified/modes/index.html /srv/unified/web/index.html
