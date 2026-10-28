#!/usr/bin/env python3
"""Include the recorded B-machine Electron files in the deployment archive.
Usage: python3 maintenance/package-existing-runtime.py OFFICIAL_ELECTRON_ZIP
The official archive must match every entry in external-electron.json.
No Ubuntu disk or Docker image is collected. Existing project archives are replaced.
"""
import hashlib,json,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'deployment/current/external-electron.json').read_text())
source=zipfile.ZipFile(sys.argv[1])
for item in manifest['files']:
 data=source.read(item['path'])
 if len(data)!=item['size'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
  raise SystemExit('Recorded runtime mismatch: '+item['path'])
release=root/'release';target=release/'Ubuntu-MultiContainer-GUI-B-existing-files.zip'
files=[p for p in sorted(root.rglob('*')) if p.is_file() and p.name!='.git' and 'release' not in p.relative_to(root).parts and not str(p.relative_to(root)).startswith('deployment/current/rootfs/srv/unified/console/electron/')]
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for p in files:out.write(p,'Ubuntu-MultiContainer-GUI-B-compatible/'+str(p.relative_to(root)))
 for item in manifest['files']:
  name=item['path'];info=source.getinfo(name)
  new=zipfile.ZipInfo('Ubuntu-MultiContainer-GUI-B-compatible/deployment/current/rootfs/srv/unified/console/electron/'+name,info.date_time)
  new.external_attr=info.external_attr;new.compress_type=zipfile.ZIP_DEFLATED
  out.writestr(new,source.read(name))
part_size=60*1024*1024
with target.open('rb') as inp:
 part=1
 while data:=inp.read(part_size):
  target.with_name(target.name+f'.part{part:03}').write_bytes(data);part+=1
for name in ['Ubuntu-MultiContainer-GUI-B-compatible-complete-20261027.zip','Ubuntu-MultiContainer-GUI-B-compatible-complete-20261027.zip.sha256']:
 (release/name).unlink(missing_ok=True)
target.unlink()
print('Packaged',len(files),'project files and',len(manifest['files']),'runtime files into',part-1,'parts')
