#!/usr/bin/python3
"""Controlled display geometry endpoint; loopback only, standard library only."""
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import controller
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path!='/api/mode':self.send_error(404);return
  try:mode=int(json.loads(Path('/srv/unified/state/modes.json').read_text())['mode'])
  except (OSError,ValueError,KeyError):self.send_error(503);return
  if mode not in [1,2]:self.send_error(503);return
  body=json.dumps({'mode':mode,'width':controller.state().get('mode1_monitor_width',1280)*3 if mode==1 else 1280,'height':controller.state().get('mode1_height',800) if mode==1 else 800}).encode()
  self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_POST(self):
  if self.path!='/api/mode':self.send_error(404);return
  origin=self.headers.get('Origin')
  if origin and origin!='http://'+self.headers.get('Host',''):self.send_error(403);return
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=256:raise ValueError()
   request=json.loads(self.rfile.read(length))
   if request.get('inputReady') is True:
    targets=request.get('desktops',[request.get('desktop')])
    if not isinstance(targets,list) or not 1<=len(targets)<=4 or any(cid not in (None,'a','b','c') for cid in targets):raise ValueError()
    for cid in targets:controller.input_ready(cid)
    self.do_GET();return
   height=request['height'];width=request.get('width',3840)
   if type(width)!=int or not 2400<=width<=7680 or width%24:raise ValueError()
   if type(height)!=int or not 600<=height<=6000:raise ValueError()
  except (ValueError,KeyError):self.send_error(400);return
  try:
   controller.setmode(1,height=height,width=width,only_if_current=1)
  except Exception:self.send_error(503);return
  self.do_GET()
 def log_message(self,*args):pass
ThreadingHTTPServer(('127.0.0.1',8091),Handler).serve_forever()
