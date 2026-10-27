#!/usr/bin/python3
"""Select independent host desktops or the original unified desktop."""
import fcntl,json,time,sys
from pathlib import Path
import native_core as core
import desktops
run=core.run
windows=core.windows
state=core.state
xfconf=core.xfconf
bus_env=core.bus_env
geometry=core.geometry

def main_ready():
 for _ in range(90):
  if run(['wmctrl','-m'],False) and run(['wmctrl','-lG'],False):return
  time.sleep(1)
 raise RuntimeError('Unified desktop is not ready')
def launch(cid,app):
 if cid=='auto':cid={'terminal':'a','editor':'b','files':'c'}[app]
 if cid not in 'abc' or len(cid)!=1:raise ValueError('Invalid container')
 import subprocess,shlex
 apps={'terminal':['xterm','-T','Container '+cid.upper()+' Terminal'],'editor':['dbus-run-session','mousepad','--disable-server'],'files':['dbus-run-session','thunar','/']}
 if app not in apps:raise ValueError('Invalid application')
 cmd='unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS; exec '+shlex.join(apps[app])
 run(['docker','exec','-d','--user','1000:1000','-e','DISPLAY=:100','-e','XAUTHORITY=/run/auth/container','unified-'+cid,'sh','-c',cmd])
def ensure_apps():
 existing=windows()
 for cid,app in [('a','terminal'),('b','editor'),('c','files')]:
  if not any(w['container']==cid for w in existing):launch(cid,app)
 for _ in range(30):
  if len({w['container'] for w in windows()})==3:return
  time.sleep(1)
 raise RuntimeError('Unified desktop is missing an application')
def arrange_unified():
 # The reference belongs only to mode two. Never replace live applications.
 run(['wmctrl','-s','0'])
 for win in windows():
  geometry(win['id'],10+'abc'.index(win['container'])*425,85,410,714,0)
  if win['flags']['minimized']:run(['xdotool','windowmap',win['id']])
 editor=next((w for w in windows() if w['container']=='b'),None)
 if editor:run(['wmctrl','-ia',editor['id']])
def setmode(mode,height=None,width=None,only_if_current=None):
 if mode not in (1,2):raise ValueError('Invalid mode')
 with open('/srv/unified/state/modes.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  s=state()
  if s.get('schema_version')!=2:
   for key in ['saved','saved_flags','workspaces','server_epoch']:s.pop(key,None)
   s['schema_version']=2
  if only_if_current is not None and s['mode']!=only_if_current:return
  if mode==1:
   w=width//3 if width else s.get('mode1_monitor_width',800)
   h=height or s.get('mode1_height',1500)
   desktops.resize(w,h)
   s['mode1_monitor_width']=w;s['mode1_height']=h
  elif s.get('mode')!=2:arrange_unified()
  s['mode']=mode;s['architecture']='independent-host-xfce-sessions'
  core.save(s)
 print(json.dumps({'mode':mode,'independent_sessions':True}))
def input_ready(cid=None):
 if cid is None:run(['xset','r','off'])
 elif cid in ('a','b','c'):desktops.run(cid,['xset','r','off'])
 else:raise ValueError('Unknown desktop')
def start():
 main_ready();ensure_apps()
 run(['xrandr','--output','DUMMY1','--off','--output','DUMMY2','--off','--output','DUMMY0','--mode','1280x800','--pos','0x0','--primary','--fb','1280x800'])
 import dbus
 interface=xfconf()
 for panel in [1,2]:
  interface.SetProperty('xfce4-panel','/panels/panel-'+str(panel)+'/output-name',dbus.String('DUMMY0'))
 interface.SetProperty('xfce4-panel','/panels/panel-2/position',dbus.String('p=10;x=0;y=0'))
 interface.SetProperty('xfce4-panel','/panels/panel-2/autohide-behavior',dbus.UInt32(0))
 interface.SetProperty('xfce4-panel','/panels',dbus.Array([dbus.Int32(1),dbus.Int32(2)],signature='v'))
 interface.SetProperty('displays','/Notify',dbus.Int32(0))
 arrange_unified()
 for cid in 'abc':desktops.ready(cid)
 setmode(state().get('mode',2))
if __name__=='__main__':
 action=sys.argv[1]
 if action=='mode':setmode(int(sys.argv[2]))
 elif action=='launch':launch(sys.argv[2],sys.argv[3])
 elif action=='start':start()
 elif action=='status':print(json.dumps({'state':state(),'unified_windows':windows(),'desktops':desktops.status()}))
 else:raise ValueError('Unknown action')
