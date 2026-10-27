#!/usr/bin/python3
"""Use ordinary Xfce menus and shortcuts; no custom desktop shell."""
import json,sys
from pathlib import Path
sys.path.insert(0,'/srv/unified/modes')
import controller
import dbus
apps=Path.home()/'.local/share/applications'
apps.mkdir(parents=True,exist_ok=True)
for app,name,icon in [('terminal','容器终端','org.xfce.terminal'),('files','容器文件管理器','org.xfce.filemanager'),('editor','容器编辑器','org.xfce.mousepad')]:
 (apps/('unified-container-'+app+'.desktop')).write_text('[Desktop Entry]\nType=Application\nName='+name+'\nExec=/usr/bin/python3 /srv/unified/modes/controller.py launch auto '+app+'\nIcon='+icon+'\nCategories=Utility;\nTerminal=false\n')
i=controller.xfconf()
props=i.GetAllProperties('xfce4-keyboard-shortcuts','/')
keys={}
for mode in [1,2]:
 command='/usr/bin/python3 /srv/unified/modes/controller.py mode '+str(mode)
 for key in ['<Super>F'+str(mode),'<Super><Alt>'+str(mode)]:
  path='/commands/custom/'+key
  if path not in props or str(props[path])==command:
   i.SetProperty('xfce4-keyboard-shortcuts',path,dbus.String(command));keys[str(mode)]=key;break
Path('/srv/unified/modes/shortcuts.json').write_text(json.dumps(keys,indent=2))
print('NATIVE_SHORTCUTS',json.dumps(keys))
