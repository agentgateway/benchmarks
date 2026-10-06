#!/usr/bin/env python3
"""Premeasurement readiness using fresh connections; never count as load samples."""
import json,sys,time,urllib.request
v=json.loads(sys.stdin.read());start=time.monotonic();attempts=[];successes=0
while time.monotonic()-start<60:
 row={'seconds':time.monotonic()-start}
 try:
  with urllib.request.urlopen(v['url']+'/healthz',timeout=2) as r:
   body=r.read();ok=r.status==200 and body==b'ok';row.update(status=r.status,expected_body=body==b'ok')
 except Exception as e:ok=False;row['error']=repr(e)
 row['passed']=ok;attempts.append(row);successes=successes+1 if ok else 0
 if successes>=3:
  v['readiness']={'elapsed_seconds':time.monotonic()-start,'required_consecutive_successes':3,'attempts':attempts};print(json.dumps(v));break
 time.sleep(.25)
else:
 print(json.dumps({'readiness_failed':True,'url':v['url'],'attempts':attempts}),file=sys.stderr);raise SystemExit(1)
