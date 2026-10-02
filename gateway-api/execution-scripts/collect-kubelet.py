#!/usr/bin/env python3
import datetime,json,subprocess,time
from pathlib import Path
out=Path('/opt/benchmark/kubelet-samples.jsonl')
with out.open('a',buffering=1) as stream:
    while True:
        started=time.monotonic()
        row={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        try:
            result=subprocess.run(['kubectl','get','--raw','/api/v1/nodes/agw-praxis-control-plane/proxy/stats/summary'],capture_output=True,text=True,timeout=15)
            row['exit_code']=result.returncode
            if result.returncode==0:row['stats']=json.loads(result.stdout)
            else:row['error']=result.stderr
        except Exception as exc:row['error']=repr(exc)
        stream.write(json.dumps(row,separators=(',',':'))+'\n')
        time.sleep(max(0,5-(time.monotonic()-started)))
