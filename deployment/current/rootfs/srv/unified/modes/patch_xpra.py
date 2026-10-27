#!/usr/bin/python3
"""Xpra 6.5.4: desktop resize must honor the existing can_resize flag."""
from pathlib import Path
import datetime,hashlib,json,subprocess
version=subprocess.check_output(['dpkg-query','-W','-f=${Version}','xpra'],text=True).strip()
if not version.startswith('6.5.4'):raise RuntimeError('This reviewed patch requires Xpra 6.5.4')
p=Path('/usr/lib/python3/dist-packages/xpra/x11/desktop/model_base.py')
s=p.read_text()
marker='# VM Unified GUI: honor --resize-display=no for client window requests.'
if marker not in s:
 old='    def resize(self, w: int, h: int) -> None:\n        geomlog("resize(%i, %i)", w, h)'
 if s.count(old)!=1:raise RuntimeError('Unrecognized Xpra source; no patch applied')
 backup=Path('/srv/unified/backups')/('xpra-model-base-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')+'.py')
 backup.write_bytes(p.read_bytes());backup.chmod(0o600)
 new='    def resize(self, w: int, h: int) -> None:\n        '+marker+'\n        if not getattr(self, "can_resize", True):\n            return\n        geomlog("resize(%i, %i)", w, h)'
 p.write_text(s.replace(old,new))
 print(json.dumps({'xpra_version':version,'backup':str(backup),'before_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
else:print('Xpra managed resize guard already present')
