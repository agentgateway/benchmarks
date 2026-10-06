#!/usr/bin/env python3
"""Run one qualified common then native pass; does not approve any repeats."""
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('phase',choices=['pass1','pass2','pass3']);p.add_argument('--resume',action='store_true');a=p.parse_args();root=Path(__file__).resolve().parent
for runner,folder in [('run-common-pass.py','dispatch'),('run-native-pass.py','dispatch-native')]:
 done=root.parent/'evidence'/folder/a.phase/'COMPLETE'
 if a.resume and done.exists():continue
 cmd=[sys.executable,str(root/runner),a.phase]
 if a.resume:cmd.append('--resume')
 subprocess.run(cmd,check=True)
