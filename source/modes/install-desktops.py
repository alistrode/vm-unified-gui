#!/usr/bin/python3
"""Provision host-side profiles and units, without changing any container image."""
from pathlib import Path
import shutil,os,subprocess,xml.etree.ElementTree as ET
root=Path('/srv/unified')
for index,cid in enumerate('abc',101):
 home=root/'state/desktops'/cid/'home';config=home/'.config/xfce4'
 if not config.exists():
  config.parent.mkdir(parents=True,exist_ok=True);shutil.copytree('/home/workspace/.config/xfce4',config)
  xml=config/'xfconf/xfce-perchannel-xml/xfce4-panel.xml'
  shutil.copyfile('/etc/xdg/xfce4/panel/default.xml',xml)
  tree=ET.parse(xml);channel=tree.getroot();panels=channel.find("property[@name='panels']");panels.set('type','array')
  for element in list(panels):
   if element.tag=='value':panels.remove(element)
   elif element.tag=='property' and element.attrib.get('name','').startswith('panel-'):
    panel_id=int(element.attrib['name'].split('-')[1])
    if panel_id>2:panels.remove(element)
    else:
     for p in list(element):
      if p.attrib.get('name')=='output-name':p.set('value','DUMMY0')
      if p.attrib.get('name')=='position':p.set('value','p='+('6' if panel_id==1 else '10')+';x=0;y=0')
  for v in ['1','2']:ET.SubElement(panels,'value',{'type':'int','value':v})
  plugins=channel.find("property[@name='plugins']")
  for p in list(plugins):
   if int(p.attrib.get('name','plugin-0').split('-')[1])>=100:plugins.remove(p)
  tree.write(xml,encoding='UTF-8',xml_declaration=True)
  for name in ['xfce4-keyboard-shortcuts.xml']:
   p=config/'xfconf/xfce-perchannel-xml'/name
   if p.exists():
    text=p.read_text().replace('/usr/bin/python3 /srv/unified/modes/controller.py mode','env DISPLAY=:100 XAUTHORITY=/srv/unified/state/auth/host /usr/bin/python3 /srv/unified/modes/controller.py mode')
    p.write_text(text)
 # Repair an interrupted first profile creation without replacing user settings.
 panel_xml=config/'xfconf/xfce-perchannel-xml/xfce4-panel.xml'
 tree=ET.parse(panel_xml);panels=tree.getroot().find("property[@name='panels']")
 if panels is not None and panels.get('type')!='array':
  panels.set('type','array');tree.write(panel_xml,encoding='UTF-8',xml_declaration=True)
 displays=config/'xfconf/xfce-perchannel-xml/displays.xml'
 if not (home/'.native-profile-ready').exists():
  displays.write_text('<?xml version="1.0" encoding="UTF-8"?><channel name="displays" version="1.0"><property name="Notify" type="int" value="0"/></channel>')
  (home/'.native-profile-ready').touch()
 apps=home/'.local/share/applications';apps.mkdir(parents=True,exist_ok=True)
 for app,title,icon in [('terminal','容器终端','utilities-terminal'),('editor','容器编辑器','accessories-text-editor'),('files','容器文件管理器','system-file-manager')]:
  (apps/('unified-'+app+'.desktop')).write_text('[Desktop Entry]\nType=Application\nName='+title+'\nExec=/usr/bin/python3 /srv/unified/modes/desktops.py launch '+cid+' '+app+'\nIcon='+icon+'\nCategories=Utility;\nTerminal=false\n')
 for app,entry in [('terminal','xfce4-terminal-emulator.desktop'),('files','xfce4-file-manager.desktop')]:
  (apps/entry).write_text((apps/('unified-'+app+'.desktop')).read_text())
 for plugin,app,entry in [(17,'terminal','xfce4-terminal-emulator.desktop'),(18,'files','xfce4-file-manager.desktop')]:
  folder=config/'panel'/('launcher-'+str(plugin));folder.mkdir(parents=True,exist_ok=True)
  (folder/entry).write_text((apps/('unified-'+app+'.desktop')).read_text())
 for mode in [1,2]:
  (apps/('unified-mode-'+str(mode)+'.desktop')).write_text('[Desktop Entry]\nType=Application\nName=模式'+str(mode)+'\nExec=env DISPLAY=:100 XAUTHORITY=/srv/unified/state/auth/host /usr/bin/python3 /srv/unified/modes/controller.py mode '+str(mode)+'\nIcon=preferences-desktop-display\nCategories=Utility;\nTerminal=false\n')
 desktop=root/'state/desktops'/cid
 for path in [desktop,*desktop.rglob('*')]:os.chown(path,1000,1000)
 service=f'''[Unit]
Description=Native independent Xfce desktop {cid.upper()} outside containers
After=unified-apps.service
Requires=unified-apps.service
[Service]
User=workspace
Environment=HOME={home}
Environment=XDG_CONFIG_HOME={home}/.config
Environment=XDG_DATA_HOME={home}/.local/share
Environment=XDG_CACHE_HOME={home}/.cache
Environment=XAUTHORITY=/srv/unified/state/auth/desktop-{cid}-host
Environment=XPRA_BATCH_MIN_DELAY=100
ExecStart=/usr/bin/xpra start-desktop :{index} --daemon=no --bind-tcp=127.0.0.1:{8000+index} --sharing=yes --html=/usr/share/xpra/www --resize-display=off:1280x800@50 --xvfb="/usr/lib/xorg/Xorg -noreset -nolisten tcp -config /srv/unified/xorg-shared.conf -logfile /srv/unified/state/desktops/{cid}/xorg.log +extension RANDR +extension RENDER" --start-child="dbus-run-session xfce4-session" --mdns=no --pulseaudio=no --webcam=no --printing=no --notifications=yes --exit-with-children=no --encoding=png --encodings=png --speed=100 --min-speed=100 --quality=100 --min-quality=100 --auto-refresh-delay=0 --keyboard-sync=no --bandwidth-limit=250000 --bandwidth-detection=no
ExecStartPost=/bin/bash /srv/unified/modes/prepare-desktop-auth.sh {cid}
ExecStartPost=/usr/bin/python3 /srv/unified/modes/desktops.py start {cid}
TimeoutStartSec=180
Restart=on-failure
RestartSec=5
MemoryMax=1024M
Nice=5
[Install]
WantedBy=multi-user.target
'''
 Path('/etc/systemd/system/unified-desktop-'+cid+'.service').write_text(service)
nginx=Path('/etc/nginx/sites-available/unified');text=nginx.read_text()
for index,cid in enumerate('abc',101):
 marker='location /desktop/'+cid+'/'
 if marker not in text:
  i=text.rfind('}');text=text[:i]+f' {marker} {{ proxy_pass http://127.0.0.1:{8000+index}/; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_read_timeout 3600s; }}\n'+text[i:]
for folder in ['js','css','icons','images','fonts']:
 marker='location /display/'+folder+'/'
 if marker not in text:
  i=text.rfind('}');text=text[:i]+f' {marker} {{ alias /usr/share/xpra/www/{folder}/; gzip_static on; expires 1h; }}\n'+text[i:]
nginx.write_text(text)
subprocess.run(['nginx','-t'],check=True)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','reload','nginx'],check=True)
