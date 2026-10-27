# Manual diagnostic: obtain user approval under the main-branch skill before running.
set -eu
python3 - <<'PY'
import sys,os,io,base64
sys.path.insert(0,'/srv/unified/modes');import desktops
from PIL import ImageGrab
for cid in 'abc':
 os.environ.update(desktops.environment(cid))
 im=ImageGrab.grab(xdisplay=os.environ['DISPLAY']);out=io.BytesIO();im.save(out,format='WEBP',lossless=True,method=4)
 print('NATIVE_'+cid+':'+base64.b64encode(out.getvalue()).decode())
PY
