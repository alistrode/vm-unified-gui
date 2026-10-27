# Manual diagnostic: obtain user approval under the main-branch skill before running.
set -eu
export DISPLAY=:100 XAUTHORITY=/srv/unified/state/auth/host
python3 - <<'PY'
import io,base64,os
from PIL import ImageGrab
image=ImageGrab.grab(xdisplay=os.environ['DISPLAY']);out=io.BytesIO();image.save(out,format='WEBP',lossless=True,method=4)
print('IMAGE_WEBP:'+base64.b64encode(out.getvalue()).decode())
PY
