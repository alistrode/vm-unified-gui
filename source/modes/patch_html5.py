#!/usr/bin/python3
"""Stock HTML5 v21: relay timeouts and a parent-frame readiness handle."""
from pathlib import Path
import datetime,gzip
p=Path('/usr/share/xpra/www/index.html')
s=p.read_text();old='client.scale = scale;'
marker='// VM Unified GUI relay timeouts'
changed=False
if marker not in s:
 if s.count(old)!=1:raise RuntimeError('Unrecognized HTML5 client; no changes applied')
 s=s.replace(old,old+'\n'+marker+'\nclient.OPEN_TIMEOUT=90000; client.HELLO_TIMEOUT=90000; client.PING_TIMEOUT=120000; client.PING_GRACE=90000;');changed=True
if 'window.client=client;' not in s:
 if s.count(old)!=1:raise RuntimeError('Unrecognized HTML5 initializer; no changes applied')
 s=s.replace(old,old+' window.client=client;');changed=True
if 'js/Client.js?unified-ping-grace=1' not in s:
 old_client='src="js/Client.js"'
 if s.count(old_client)!=1:raise RuntimeError('Unrecognized HTML5 client script; no changes applied')
 s=s.replace(old_client,'src="js/Client.js?unified-ping-grace=1"');changed=True
if changed:
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
 backup=Path('/srv/unified/backups')/('html5-index-'+stamp+'.html')
 with backup.open('xb') as f:f.write(p.read_bytes())
 backup.chmod(0o600);p.write_text(s)
 for suffix in ['.gz','.br']:
  f=Path(str(p)+suffix)
  if not f.exists():continue
  dest=Path('/srv/unified/backups')/('html5-index-'+stamp+'.html'+suffix)
  with dest.open('xb') as out:out.write(f.read_bytes())
  dest.chmod(0o600)
  if suffix=='.gz':f.write_bytes(gzip.compress(s.encode(),mtime=0))
  else:
   try:
    import brotli
    f.write_bytes(brotli.compress(s.encode()))
   except ImportError:f.unlink()
 print('Stock HTML5 relay integration updated; backup '+str(backup))
else:print('Stock HTML5 relay integration already present')
