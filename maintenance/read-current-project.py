import json,pathlib,os
r=pathlib.Path('/srv/unified')
paths=list((r/'modes').glob('*'))+[r/'web/index.html',pathlib.Path('/etc/nginx/sites-available/unified')]+list(pathlib.Path('/etc/systemd/system').glob('unified-*.service'))+list(pathlib.Path('/etc/systemd/system/unified-display.service.d').glob('*'))
print(json.dumps({'hostname':os.uname().nodename,'files':[{'path':str(p),'size':p.stat().st_size,'content':p.read_text()} for p in paths if p.is_file()]}))
