# Manual diagnostic: obtain user approval under the main-branch skill before running.
set -eu
export DISPLAY=:100 XAUTHORITY=/srv/unified/state/auth/host
python3 -u - <<'PY'
import sys,time,json,uuid,subprocess
from pathlib import Path
sys.path.insert(0,'/srv/unified/modes');import desktops as d,controller as c
report={};c.setmode(1)
def keys(cid,wid,*keys):
 d.run(cid,['xdotool','windowactivate','--sync',wid]);d.run(cid,['xdotool','key','--clearmodifiers',*keys]);time.sleep(.4)
def text(cid,value):d.run(cid,['xdotool','type','--clearmodifiers','--delay','15',value]);time.sleep(.3)
def app_window(cid):
 for line in d.windows(cid).splitlines():
  if d.HOSTS[cid] in line:return line.split()[0]
 raise RuntimeError('Missing application '+cid)
def current_workspace(cid):return next(int(line.split()[0]) for line in d.run(cid,['wmctrl','-d']).splitlines() if line.split()[1]=='*')
for cid in 'abc':
 d.ready(cid);d.run(cid,['wmctrl','-s','0']);assert 'Desktop' in d.windows(cid) and 'xfce4-panel' in d.windows(cid)
 report[cid]={'display':d.environment(cid)['DISPLAY'],'native_desktop_and_panels':True,'workspaces':len(d.run(cid,['wmctrl','-d']).splitlines())}
ids={cid:app_window(cid) for cid in 'abc'}
d.run('a',['wmctrl','-s','1']);time.sleep(.5)
assert [current_workspace(cid) for cid in 'abc']==[1,0,0]
d.run('a',['wmctrl','-s','0']);report['independent_workspaces']=True
for cid in 'abc':
 d.run(cid,['xdotool','key','--clearmodifiers','alt+F2']);time.sleep(.7)
 listing=d.run(cid,['wmctrl','-l']);assert 'Application Finder' in listing,(cid,listing)
 finder=next(line.split()[0] for line in listing.splitlines() if 'Application Finder' in line)
 keys(cid,finder,'ctrl+a');text(cid,'xfce4-settings-manager');d.run(cid,['xdotool','key','Return']);time.sleep(1)
 listing=d.run(cid,['wmctrl','-l']);settings=[line.split()[0] for line in listing.splitlines() if line.endswith(' Settings') or line.endswith(' Settings Manager')]
 assert settings,(cid,listing)
 for wid in settings:d.run(cid,['wmctrl','-ic',wid])
 report[cid]['native_application_finder_and_settings']=True
 print('DESKTOP_SETTINGS_OK',cid,flush=True)
# Actual container A shell execution through its desktop terminal.
name='.unified-desktop-'+uuid.uuid4().hex[:8]
keys('a',ids['a'],'ctrl+u');text('a','printf DESKTOP_A_OK > /homes/a/'+name);keys('a',ids['a'],'Return');time.sleep(.5)
assert c.run(['docker','exec','unified-a','cat','/homes/a/'+name])=='DESKTOP_A_OK'
c.run(['docker','exec','unified-a','rm','/homes/a/'+name]);keys('a',ids['a'],'ctrl+u');text('a','clear');keys('a',ids['a'],'Return');report['a']['terminal_inside_container']=True
marker='INDEPENDENT_DESKTOP_'+uuid.uuid4().hex[:8]
keys('b',ids['b'],'ctrl+a');text('b',marker);keys('b',ids['b'],'ctrl+a','ctrl+c');assert d.run('b',['xclip','-o','-selection','clipboard'])==marker
report['b']['editor_and_clipboard']=True
folder='unified-desktop-'+uuid.uuid4().hex[:8]
keys('c',ids['c'],'ctrl+l');text('c','/homes/c');keys('c',ids['c'],'Return');keys('c',ids['c'],'ctrl+shift+n');text('c',folder);d.run('c',['xdotool','key','Return']);time.sleep(.8)
c.run(['docker','exec','unified-c','test','-d','/homes/c/'+folder]);c.run(['docker','exec','unified-c','rmdir','/homes/c/'+folder]);keys('c',ids['c'],'ctrl+l');text('c','/');keys('c',ids['c'],'Return');report['c']['file_manager_create_folder_inside_container']=True
for cid in 'abc':
 d.run(cid,['wmctrl','-ir',ids[cid],'-b','add,maximized_vert,maximized_horz']);time.sleep(.3)
 assert 'MAXIMIZED_HORZ' in d.run(cid,['xprop','-id',ids[cid],'_NET_WM_STATE'])
 d.run(cid,['wmctrl','-ir',ids[cid],'-b','remove,maximized_vert,maximized_horz'])
 d.run(cid,['xdotool','windowminimize',ids[cid]]);time.sleep(.3)
 assert 'Iconic' in d.run(cid,['xprop','-id',ids[cid],'WM_STATE'])
 d.run(cid,['xdotool','windowmap',ids[cid]]);report[cid]['maximize_and_minimize']=True
c.setmode(2);c.setmode(1)
assert {cid:app_window(cid) for cid in 'abc'}==ids
keys('b',ids['b'],'ctrl+a','ctrl+c');assert d.run('b',['xclip','-o','-selection','clipboard'])==marker
keys('b',ids['b'],'ctrl+a','BackSpace');report['mode_roundtrip_keeps_desktop_windows_and_editor_content']=True
print('INDEPENDENT_DESKTOP_REPORT='+json.dumps(report),flush=True)
print('DESKTOPS='+json.dumps(d.status()),flush=True)
PY
