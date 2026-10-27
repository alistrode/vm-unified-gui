#!/usr/bin/python3
"""Independent native Xfce sessions outside application containers."""
import os,subprocess,time,json,shlex
from pathlib import Path
BASE=Path('/srv/unified/state/desktops')
HOSTS={'a':'00bfba7f6204','b':'6cc277422c90','c':'f49c530f5795'}
def number(cid):
 if cid not in HOSTS:raise ValueError('Unknown desktop')
 return 101+'abc'.index(cid)
def environment(cid):
 home=BASE/cid/'home';e=os.environ.copy()
 e.update(DISPLAY=':'+str(number(cid)),XAUTHORITY='/srv/unified/state/auth/desktop-'+cid+'-host',HOME=str(home),XDG_CONFIG_HOME=str(home/'.config'),XDG_DATA_HOME=str(home/'.local/share'),XDG_CACHE_HOME=str(home/'.cache'))
 e.pop('SESSION_MANAGER',None);e.pop('DBUS_SESSION_BUS_ADDRESS',None)
 return e
def run(cid,args,check=True):
 r=subprocess.run(args,env=environment(cid),text=True,capture_output=True,timeout=20)
 if check and r.returncode:raise RuntimeError(shlex.join(args)+': '+r.stderr.strip())
 return r.stdout.strip()
def windows(cid):return run(cid,['wmctrl','-lG'],False)
def ready(cid):
 for _ in range(90):
  if run(cid,['wmctrl','-m'],False) and run(cid,['wmctrl','-lG'],False):return
  time.sleep(1)
 raise RuntimeError('Native desktop '+cid+' is not ready')
def launch(cid,app):
 apps={'terminal':['xterm','-T','Container '+cid.upper()+' Terminal'],'editor':['dbus-run-session','mousepad','--disable-server'],'files':['dbus-run-session','thunar','/']}
 if app not in apps:raise ValueError('Unknown application')
 command='unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS; exec '+shlex.join(apps[app])
 result=subprocess.run(['docker','exec','-d','--user','1000:1000','-e','DISPLAY=:'+str(number(cid)),'-e','XAUTHORITY=/run/auth/desktop-'+cid+'-container','unified-'+cid,'sh','-c',command],text=True,capture_output=True,timeout=20)
 if result.returncode:raise RuntimeError(result.stderr.strip())
def start(cid):
 ready(cid)
 if HOSTS[cid] not in windows(cid):launch(cid,{'a':'terminal','b':'editor','c':'files'}[cid])
 for _ in range(30):
  if HOSTS[cid] in windows(cid):return
  time.sleep(1)
 raise RuntimeError('Container application did not appear on desktop '+cid)
def fit_windows(cid,width,height):
 for line in windows(cid).splitlines():
  parts=line.split(None,7)
  if len(parts)<8 or parts[1]=='-1':continue
  wid=parts[0]
  flags=run(cid,['xprop','-id',wid,'_NET_WM_STATE'],False)
  if 'MAXIMIZED' in flags or 'FULLSCREEN' in flags:continue
  import re
  info=run(cid,['xwininfo','-id',wid],False)
  ax=re.search(r'Absolute upper-left X:\s*(-?\d+)',info);ay=re.search(r'Absolute upper-left Y:\s*(-?\d+)',info)
  if not ax or not ay:continue
  ext=run(cid,['xprop','-id',wid,'_NET_FRAME_EXTENTS'],False)
  values=re.findall(r'\d+',ext.partition('=')[2]);left,top=(int(values[0]),int(values[2])) if len(values)>=4 else (0,0)
  w=min(int(parts[4]),width-20);h=min(int(parts[5]),height-80)
  x=max(5,min(int(ax[1])-left,width-w-10));y=max(30,min(int(ay[1])-top,height-h-55))
  run(cid,['wmctrl','-ir',wid,'-e',f'0,{x},{y},{w},{h}'],False)
def resize(width,height):
 if not 800<=width<=2560 or width%8 or not 600<=height<=6000:raise ValueError('Invalid desktop size')
 for cid in 'abc':
  text=run(cid,['xrandr','--current'])
  if 'current '+str(width)+' x '+str(height)+',' in text:continue
  model=next(v for v in run(cid,['cvt',str(width),str(height),'50']).splitlines() if v.strip().startswith('Modeline'))
  tokens=shlex.split(model.strip())[1:];name=tokens[0]
  run(cid,['xrandr','--newmode',*tokens],False);run(cid,['xrandr','--addmode','DUMMY0',name],False)
  run(cid,['xrandr','--output','DUMMY0','--mode',name,'--pos','0x0','--primary','--fb',str(width)+'x'+str(height)])
  fit_windows(cid,width,height)
def status():
 return {cid:{'display':':'+str(number(cid)),'windows':windows(cid),'screens':run(cid,['xrandr','--listmonitors'],False)} for cid in 'abc'}
if __name__=='__main__':
 import sys
 if sys.argv[1]=='start':start(sys.argv[2])
 elif sys.argv[1]=='launch':launch(sys.argv[2],sys.argv[3])
 elif sys.argv[1]=='status':print(json.dumps(status()))
