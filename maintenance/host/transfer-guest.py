import paramiko,pathlib,sys
base=pathlib.Path(r'E:\VM-Unified-GUI')
p=(base/'guest-password.txt').read_text().strip()
c=paramiko.SSHClient();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());c.connect('127.0.0.1',port=45625,username='workspace',password=p,timeout=20)
def run(cmd):
 i,o,e=c.exec_command(cmd);return o.read().decode()+e.read().decode()
run('mkdir -p /home/workspace/unified-source')
s=c.open_sftp()
for f in (base/'source').iterdir():
 if f.is_file():s.put(str(f),'/home/workspace/unified-source/'+f.name)
s.close()
if len(sys.argv)>1 and sys.argv[1]=='only':c.close();sys.exit(0)
i,o,e=c.exec_command("sudo -S -p '' bash -c 'nohup bash /home/workspace/unified-source/bootstrap.sh > /home/workspace/bootstrap.log 2>&1 < /dev/null &'")
i.write(p+'\n');i.flush();print(o.read().decode().replace(p,'[REDACTED]'));print(e.read().decode().replace(p,'[REDACTED]'))
c.close()
