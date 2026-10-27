ls -l /run/user/1000/xpra/100/xauthority /home/workspace/.Xauthority
grep -n 'XAUTHORITY\|xauthority' /usr/lib/python3/dist-packages/xpra/x11/vfb_util.py | head -30
grep -n 'XAUTHORITY\|xauthority' /usr/lib/python3/dist-packages/xpra/scripts/server.py | head -30
