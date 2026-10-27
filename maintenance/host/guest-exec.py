import paramiko,pathlib,sys
p=pathlib.Path(r'E:\VM-Unified-GUI\guest-password.txt').read_text().strip()
c=paramiko.SSHClient();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());c.connect('127.0.0.1',port=45625,username='workspace',password=p,timeout=15)
if sys.argv[1]=='upload':
 s=c.open_sftp();s.put(sys.argv[2],sys.argv[3]);s.close()
else:
 command=sys.argv[2]
 if sys.argv[1]=='file':command='sudo -S -p "" bash -s'
 if sys.argv[1]=='sudo':command='sudo -S -p "" '+command
 i,o,e=c.exec_command(command,timeout=240)
 if sys.argv[1]=='sudo':i.write(p+'\n');i.flush()
 if sys.argv[1]=='file':i.write(p+'\n'+pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')+'\n');i.flush();i.channel.shutdown_write()
 print(o.read().decode(errors='replace').replace(p,'[REDACTED]'));print(e.read().decode(errors='replace').replace(p,'[REDACTED]'));sys.exit(o.channel.recv_exit_status())
c.close()
