import time,json,subprocess,os,sys
from pathlib import Path
sys.path.insert(0,'/srv/unified/modes');import desktops,controller
root=Path('/srv/unified/state/browser-acceptance');root.mkdir(exist_ok=True)
marker=sys.argv[1];result={'marker':marker,'terminal_a':False,'clipboard_b':False,'files_c':False,'mode_two':False,'mode_one_returned':False}
def output():
 tmp=root/'report.next';tmp.write_text(json.dumps(result,indent=2));tmp.replace(root/'report.json')
output()
end=time.monotonic()+1200
while time.monotonic()<end:
 try:
  if not result['terminal_a']:
   p=subprocess.run(['docker','exec','unified-a','cat','/homes/a/'+marker],text=True,capture_output=True,timeout=5)
   if p.returncode==0 and p.stdout=='BROWSER_A_OK':result['terminal_a']=True
  if not result['clipboard_b']:
   p=subprocess.run(['xclip','-o','-selection','clipboard'],env=desktops.environment('b'),text=True,capture_output=True,timeout=3)
   if p.returncode==0 and p.stdout=='BROWSER_DESKTOP_B_OK':result['clipboard_b']=True
  if not result['files_c'] and ' c - Thunar' in desktops.run('c',['wmctrl','-l'],False):result['files_c']=True
  mode=controller.state()['mode']
  if mode==2:result['mode_two']=True
  elif result['mode_two'] and mode==1:result['mode_one_returned']=True
  output()
  if all(result[k] for k in ['terminal_a','clipboard_b','files_c','mode_two','mode_one_returned']):break
 except (OSError,subprocess.TimeoutExpired,RuntimeError):pass
 time.sleep(1)
print(json.dumps(result),flush=True)
