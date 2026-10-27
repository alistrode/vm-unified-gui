set -eu
python3 - <<'PY'
import subprocess,json,tarfile,hashlib,os,base64,io,datetime
from pathlib import Path
files=[]
def add(path,archive_name=None):
 p=Path(path)
 if p.is_file():files.append((p,archive_name or str(p).lstrip('/')))
root=Path('/srv/unified')
for path in root.glob('*'):
 if path.is_file():add(path)
for folder in ['modes','web','console','shared/user/bin','shared/user/python','apps']:
 base=root/folder
 if base.exists():
  for p in base.rglob('*'):
   if p.is_file() and not (folder=='console' and 'electron' in p.relative_to(base).parts) and 'node_modules' not in p.parts and '__pycache__' not in p.parts and not p.name.endswith(('.pyc','.log')):add(p)
for p in Path('/etc/systemd/system').glob('unified-*.service'):add(p)
for p in Path('/etc/systemd/system/unified-display.service.d').glob('*'):add(p)
add('/etc/nginx/sites-available/unified')
for home in [Path('/home/workspace'),*[root/'state/desktops'/c/'home' for c in 'abc']]:
 for folder in ['.config/xfce4','.local/share/applications']:
  base=home/folder
  if base.exists():
   for p in base.rglob('*'):
    if p.is_file() and p.suffix in ['.xml','.desktop','.rc']:
     if folder=='.local/share/applications' and not (p.name.startswith('unified-') or p.name.startswith('xfce4-')):continue
     add(p)
for p in ['/usr/lib/python3/dist-packages/xpra/x11/desktop/model_base.py','/usr/share/xpra/www/index.html','/usr/share/xpra/www/js/Client.js','/usr/share/doc/xpra/copyright','/usr/share/doc/xpra-html5/copyright']:add(p)
for base in ['/usr/share/xpra/www/index.html','/usr/share/xpra/www/js/Client.js']:
 for suffix in ['.gz','.br']:add(base+suffix)
add(root/'state/modes.json')
add(root/'state/publisher/pyvenv.cfg')
for p in (root/'state/sharedkit-src').rglob('*'):
 if p.is_file() and ('build' not in p.parts) and not any(part.endswith('.egg-info') for part in p.parts) and '__pycache__' not in p.parts:add(p)
metadata={}
def cmd(args):return subprocess.check_output(args,text=True,timeout=30).strip()
metadata['os_release']=Path('/etc/os-release').read_text()
electron=root/'console/electron'
if electron.exists():
 version=(electron/'version').read_text().strip() if (electron/'version').exists() else 'unknown'
 metadata['external_electron']={'version':version,'official_download':'https://github.com/electron/electron/releases/download/v'+version+'/electron-v'+version+'-linux-x64.zip','files':[{'path':str(p.relative_to(electron)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(electron.rglob('*')) if p.is_file()]}
 for name in ['LICENSE','version']:add(electron/name)
metadata['project_runtime_packages']=cmd(['dpkg-query','-W','-f=${binary:Package}\t${Version}\t${Architecture}\n',*['adwaita-icon-theme', 'docker-compose-v2', 'docker.io', 'fonts-dejavu-core', 'nginx', 'nginx-common', 'python3', 'python3-dbus', 'python3-gi', 'thunar', 'x11-utils', 'x11-xserver-utils', 'xauth', 'xclip', 'xcvt', 'xdotool', 'xfce4', 'xfce4-panel', 'xfce4-session', 'xfce4-settings', 'xfdesktop4', 'xfwm4', 'xpra', 'xpra-html5', 'xpra-x11', 'xserver-xorg-core', 'xserver-xorg-video-dummy', 'xvfb']])
metadata['containers']=[]
for cid in 'abc':
 raw=json.loads(cmd(['docker','inspect','unified-'+cid]))[0]
 image=json.loads(cmd(['docker','image','inspect',raw['Image']]))[0]
 metadata['containers'].append({'name':raw['Name'],'hostname':raw['Config']['Hostname'],'image_id':raw['Image'],'repo_tags':image.get('RepoTags'),'repo_digests':image.get('RepoDigests'),'mounts':[{'source':x['Source'],'destination':x['Destination'],'read_write':x['RW']} for x in raw['Mounts']],'application_packages':cmd(['docker','exec','unified-'+cid,'dpkg-query','-W','-f=${binary:Package}\t${Version}\t${Architecture}\n'])})
metadata['effective_units']={}
for name in ['unified-display','unified-apps','unified-status','unified-modes','unified-mode-status','unified-desktop-a','unified-desktop-b','unified-desktop-c']:
 metadata['effective_units'][name]=cmd(['systemctl','cat',name])
records=[];out=io.BytesIO()
with tarfile.open(fileobj=out,mode='w:gz') as tar:
 for p,name in sorted(files,key=lambda pair:pair[1]):
  data=p.read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mode=p.stat().st_mode&0o777;info.uid=p.stat().st_uid;info.gid=p.stat().st_gid;tar.addfile(info,io.BytesIO(data));records.append({'path':name,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'mode':oct(info.mode),'uid':info.uid,'gid':info.gid})
 for name,value in [('deployment-metadata.json',metadata),('file-manifest.json',records)]:
  data=json.dumps(value,indent=2).encode();info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;tar.addfile(info,io.BytesIO(data))
blob=out.getvalue();target=root/'backups'/('compatible-complete-export-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')+'.tar.gz');target.write_bytes(blob);target.chmod(0o600)
print('SNAPSHOT_PATH:'+str(target))
print('SNAPSHOT_INFO:'+json.dumps({'files':len(records),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()}))
PY
