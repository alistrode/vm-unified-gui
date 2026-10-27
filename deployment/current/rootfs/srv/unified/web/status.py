import http.server,subprocess,json,threading,time,urllib.parse
data=[]
def refresh():
 global data
 while True:
  try:
   p=subprocess.run(['docker','stats','--no-stream','--format','{{json .}}','unified-a','unified-b','unified-c'],capture_output=True,text=True,timeout=10)
   data=[json.loads(line) for line in p.stdout.splitlines()]
  except Exception:data=[]
  time.sleep(3)
class Handler(http.server.BaseHTTPRequestHandler):
 def do_POST(self):
  if self.path!='/api/launch':self.send_error(404);return
  origin=self.headers.get('Origin','')
  if origin and urllib.parse.urlparse(origin).netloc!=self.headers.get('Host'):self.send_error(403);return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size<1 or size>1024:raise ValueError('Invalid payload')
   request=json.loads(self.rfile.read(size)); cid=request['container']; app=request['app']
   if cid not in ['A','B','C'] or app not in ['editor','terminal','files']:raise ValueError('Unknown application')
   subprocess.run(['docker','exec','-d','unified-'+cid.lower(),'python3','/app/demo.py','--app',app],check=True,timeout=8)
   self.send_response(202);self.end_headers();self.wfile.write(b'{"launched":true}')
  except Exception as e:self.send_error(400,str(e))
 def do_GET(self):
  if self.path!='/api/status':self.send_error(404);return
  payload=json.dumps(data).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(payload)
threading.Thread(target=refresh,daemon=True).start()
http.server.HTTPServer(('127.0.0.1',8090),Handler).serve_forever()
