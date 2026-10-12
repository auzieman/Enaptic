"""Bounded protocol for the pinned APK 3.0.8 solver bridge."""
import os
from pathlib import Path
import subprocess


def executable():
    installed=Path('/usr/libexec/enaptic/enaptic-transaction')
    return str(installed if installed.exists() else Path(__file__).resolve().parents[1]/'build/out/enaptic-transaction')


def protocol(request,world,identity=''):
    upgrades=[m['name'] for m in request.get('marks',[]) if m['action']=='upgrade']
    data=f"{int(request.get('upgrade_all',False))}\n".encode()
    encoded=world.encode();data+=f'{len(encoded)}\n'.encode()+encoded
    data+=f'{len(upgrades)}\n'.encode()+''.join(n+'\n' for n in upgrades).encode()
    encoded=identity.encode();return data+f'{len(encoded)}\n'.encode()+encoded


def solve(request,root,world):
    p=subprocess.run([executable(),'plan',str(root)],input=protocol(request,world),capture_output=True,timeout=60,env=os.environ|{'LC_ALL':'C','LANG':'C'})
    if p.returncode:raise RuntimeError((p.stderr+p.stdout).decode(errors='replace').strip() or 'Native APK solver failed')
    output=p.stdout.decode();before,rest=output.split('IDENTITY\n',1);identity,rest=rest.split('END_IDENTITY\n',1)
    changes=[];totals=None
    for line in rest.splitlines():
        if line.startswith('CHANGE\t'):
            _,name,old,new,action=line.split('\t');changes.append(dict(name=name,old=old,new=new,action=action))
        elif line.startswith('TOTAL\t'):
            _,download,disk=line.split('\t');totals=dict(download=int(download),disk=int(disk))
    if totals is None:raise RuntimeError('Incomplete native solver result')
    return changes,identity,totals,output
