#!/usr/bin/python3
"""Native Xfce integration for the unified desktop."""
import json, os, subprocess, sys, time, re, fcntl, shlex
from pathlib import Path
ROOT=Path('/srv/unified/modes')
STATE=Path('/srv/unified/state/modes.json')
HOSTS={'00bfba7f6204':'a','6cc277422c90':'b','f49c530f5795':'c'}
os.environ.setdefault('DISPLAY',':100')
os.environ.setdefault('XAUTHORITY','/srv/unified/state/auth/host')
def run(args,check=True):
 return subprocess.run(args,check=check,text=True,capture_output=True,timeout=15).stdout.strip()
def bus_env():
 for path in Path('/proc').glob('[0-9]*/comm'):
  try:
   if path.read_text().strip()=='xfwm4' and path.stat().st_uid==os.getuid():
    env=dict(row.split(b'=',1) for row in (path.parent/'environ').read_bytes().split(b'\0') if b'=' in row)
    if env.get(b'DISPLAY',b'').decode().split('.')[0]!=os.environ.get('DISPLAY',':100').split('.')[0]:continue
    if b'DBUS_SESSION_BUS_ADDRESS' in env:
     os.environ['DBUS_SESSION_BUS_ADDRESS']=env[b'DBUS_SESSION_BUS_ADDRESS'].decode();return
  except (OSError,PermissionError):pass
def xfconf():
 bus_env()
 import dbus
 return dbus.Interface(dbus.SessionBus().get_object('org.xfce.Xfconf','/org/xfce/Xfconf'),'org.xfce.Xfconf')
def state():
 try:return json.loads(STATE.read_text())
 except (OSError,ValueError):return {'mode':2,'saved':{}}
def save(value):
 tmp=STATE.with_suffix('.next');tmp.write_text(json.dumps(value,indent=2));tmp.replace(STATE)
def windows():
 rows=[]
 # A native launcher may close a window while EWMH metadata is being read.
 listing=''
 for attempt in range(4):
  result=subprocess.run(['wmctrl','-lG'],text=True,capture_output=True,timeout=15)
  if result.returncode==0:listing=result.stdout;break
  if attempt==3:raise RuntimeError('Cannot read desktop windows: '+result.stderr.strip())
  time.sleep(.15)
 for line in listing.splitlines():
  p=line.split(None,7)
  if len(p)<8:continue
  wid,desktop,x,y,w,h,host,title=p
  cid=HOSTS.get(host.lower())
  if cid:
   info=run(['xwininfo','-id',wid],False)
   if not info:continue
   ext=run(['xprop','-id',wid,'_NET_FRAME_EXTENTS','_NET_WM_STATE'],False)
   if not ext or 'BadWindow' in ext:continue
   values=re.findall(r'\d+',ext.splitlines()[0].partition('=')[2]);left,top=(int(values[0]),int(values[2])) if len(values)>=4 else (0,0)
   ax=re.search(r'Absolute upper-left X:\s*(-?\d+)',info);ay=re.search(r'Absolute upper-left Y:\s*(-?\d+)',info)
   x=int(ax[1])-left if ax else int(x);y=int(ay[1])-top if ay else int(y)
   rows.append({'id':wid,'container':cid,'desktop':int(desktop),'x':x,'y':y,'w':int(w),'h':int(h),'title':title,'flags':{'maximized':all(v in ext for v in ['_NET_WM_STATE_MAXIMIZED_HORZ','_NET_WM_STATE_MAXIMIZED_VERT']),'minimized':'_NET_WM_STATE_HIDDEN' in ext,'fullscreen':'_NET_WM_STATE_FULLSCREEN' in ext,'above':'_NET_WM_STATE_ABOVE' in ext}})
 return rows
def geometry(wid,x,y,w,h,desktop=0):
 run(['wmctrl','-ir',wid,'-b','remove,fullscreen,above'])
 run(['wmctrl','-ir',wid,'-b','remove,maximized_vert,maximized_horz'])
 run(['wmctrl','-ir',wid,'-t',str(desktop)])
 run(['wmctrl','-ir',wid,'-e',f'0,{x},{y},{w},{h}'])
