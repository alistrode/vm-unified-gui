import json,time,sys
from pathlib import Path
sys.path.insert(0,'/srv/unified/modes');import desktops
out=Path('/srv/unified/state/browser-acceptance/focus.json');last={};events=[]
for _ in range(300):
 for cid in 'abc':
  pointer=desktops.run(cid,['xdotool','getmouselocation','--shell'],False)
  focus=desktops.run(cid,['xprop','-root','_NET_ACTIVE_WINDOW'],False)
  value={'pointer':pointer,'active_window':focus}
  if value!=last.get(cid):
   last[cid]=value;events.append({'desktop':cid,'time':time.time(),**value})
   out.write_text(json.dumps({'latest':last,'events':events[-100:]},indent=2))
 time.sleep(1)
