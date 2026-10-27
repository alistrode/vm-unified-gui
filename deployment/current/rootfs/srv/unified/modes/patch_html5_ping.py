#!/usr/bin/python3
"""Xpra HTML5 v21: honor configured ping grace instead of a hard-coded 2s."""
from pathlib import Path
import datetime,gzip
p=Path('/usr/share/xpra/www/js/Client.js')
s=p.read_text()
old='this.ping_grace_timer=setTimeout(()=>this._check_server_echo(now_ms),2e3)'
new='this.ping_grace_timer=setTimeout(()=>this._check_server_echo(now_ms),this.PING_GRACE)'
if new in s:print('HTML5 configured ping grace already honored')
else:
 if s.count(old)!=1:raise RuntimeError('Unrecognized HTML5 ping scheduler; no changes applied')
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
 backup=Path('/srv/unified/backups')/('html5-client-'+stamp+'.js')
 with backup.open('xb') as f:f.write(p.read_bytes())
 backup.chmod(0o600)
 updated=s.replace(old,new);p.write_text(updated)
 for suffix in ['.gz','.br']:
  compressed=Path(str(p)+suffix)
  if not compressed.exists():continue
  copy=Path(str(backup)+suffix)
  with copy.open('xb') as f:f.write(compressed.read_bytes())
  copy.chmod(0o600)
  if suffix=='.gz':compressed.write_bytes(gzip.compress(updated.encode(),mtime=0))
  else:
   try:
    import brotli
    compressed.write_bytes(brotli.compress(updated.encode()))
   except ImportError:compressed.unlink()
 print('HTML5 ping scheduler now honors PING_GRACE; backup '+str(backup))
