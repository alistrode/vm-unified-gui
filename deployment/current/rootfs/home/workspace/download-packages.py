import subprocess,re,pathlib,time,urllib.request,hashlib,sys,os
root=os.environ.get('PACKAGE_ROOT','')
prefix=['chroot',root] if root else []
cache=pathlib.Path(root+'/var/cache/apt/archives')
args=['apt-get','--print-uris','--download-only','--no-install-recommends','install',*sys.argv[1:]]
out=subprocess.check_output(prefix+args,text=True)
mirrors=['https://mirrors.tuna.tsinghua.edu.cn/ubuntu/','https://mirrors.ustc.edu.cn/ubuntu/','https://mirrors.aliyun.com/ubuntu/']
for url,name,size,md5 in re.findall(r"'([^']+)' (\S+) (\d+) MD5Sum:(\w+)",out):
    dest=cache/name; size=int(size)
    if dest.exists() and hashlib.md5(dest.read_bytes()).hexdigest()==md5:continue
    suffix=url.split('/ubuntu/',1)[1]
    for mirror in mirrors:
        temporary=cache/(name+'.download')
        try:
            start=last=time.monotonic(); total=previous=0
            with urllib.request.urlopen(mirror+suffix,timeout=12) as response,temporary.open('wb') as f:
                while True:
                    block=response.read(256*1024)
                    if not block:break
                    f.write(block);total+=len(block);now=time.monotonic()
                    if now-last>=5:
                        speed=(total-previous)/(now-last)
                        print(f'DOWNLOAD {name} {total}/{size} {speed/1024:.0f} KiB/s {mirror}',flush=True)
                        if speed<800*1024:raise RuntimeError('below 800 KiB/s; switching mirror')
                        last=now;previous=total
            if total!=size or hashlib.md5(temporary.read_bytes()).hexdigest()!=md5:raise RuntimeError('package checksum mismatch')
            temporary.replace(dest)
            print(f'COMPLETE {name} {total/max(time.monotonic()-start,0.01)/1024:.0f} KiB/s',flush=True)
            break
        except Exception as e:
            print(f'MIRROR_SWITCH {mirror} {e}',flush=True)
            temporary.unlink(missing_ok=True)
    else:raise RuntimeError('all mirrors exhausted: '+name)
subprocess.run(prefix+['apt-get','-y','--no-download','--no-install-recommends','install']+args[5:],check=True)
