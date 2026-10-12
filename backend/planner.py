"""Native APK simulations against private metadata snapshots; never apply."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

NAME=re.compile(r'[A-Za-z0-9][A-Za-z0-9+_.-]*\Z')
CHANGE=re.compile(r'^\(\d+/\d+\) (Installing|Purging|Upgrading|Downgrading|Reinstalling) ([A-Za-z0-9+_.-]+) \(([^)]+)\)$')

def validate_request(request):
    if not isinstance(request,dict) or set(request)-{'marks','upgrade_all'}:raise ValueError('Invalid preview request')
    marks=request.get('marks',[])
    if not isinstance(marks,list) or len(marks)>1000:raise ValueError('Invalid mark list')
    if not isinstance(request.get('upgrade_all',False),bool):raise ValueError('Invalid upgrade flag')
    seen=set()
    for mark in marks:
        if not isinstance(mark,dict) or set(mark)!={'name','action'}:raise ValueError('Invalid package mark')
        if not isinstance(mark['name'],str) or len(mark['name'])>255 or not NAME.fullmatch(mark['name']):raise ValueError('Invalid package name')
        if mark['action'] not in ('install','remove','upgrade'):raise ValueError('Unsupported action')
        if mark['name'] in seen:raise ValueError('Duplicate package mark')
        seen.add(mark['name'])
    return marks

def parse_changes(output):
    changes=[]
    for line in output.splitlines():
        match=CHANGE.fullmatch(line)
        if not match:
            if re.match(r'^\(\d+/\d+\)',line):raise RuntimeError('Unrecognized APK transaction output; review cannot be trusted')
            continue
        action,name,versions=match.groups()
        if action=='Installing':old,new='—',versions
        elif action=='Purging':old,new=versions,'—'
        elif action=='Reinstalling':old=new=versions
        else:
            if ' -> ' not in versions:raise RuntimeError('Missing APK version transition')
            old,new=versions.split(' -> ',1)
        changes.append(dict(name=name,old=old,new=new,action=action))
    return changes

def world_name(line):
    match=re.match(r'^!?([A-Za-z0-9+_.-]+)',line)
    return match.group(1) if match else None

def edited_world(text,marks):
    lines=text.splitlines()
    for mark in marks:
        name=mark['name'];present=any(world_name(line)==name for line in lines)
        if mark['action']=='remove':lines=[line for line in lines if world_name(line)!=name]
        elif not present:lines.append(name)
    return '\n'.join(lines)+'\n'

def input_files():
    files=[p for p in Path('/lib/apk/db').glob('*') if p.is_file() and p.name!='lock']+[Path('/etc/apk/world'),Path('/etc/apk/repositories')]
    files.extend(p for p in [Path('/etc/apk/arch'),Path('/etc/apk/config')] if p.is_file())
    for directory,pattern in [('/etc/apk/keys','*'),('/etc/apk/repositories.d','*'),('/var/cache/apk','APKINDEX*')]:
        files.extend(p for p in Path(directory).glob(pattern) if p.is_file())
    return sorted(set(files))

def fingerprint():
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_files()}
    return hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()

def preview(request):
    marks=validate_request(request)
    if not marks and not request.get('upgrade_all'):return dict(changes=[],retained=[],fingerprint=fingerprint(),output='No packages marked.',totals=None)
    before=fingerprint()
    with tempfile.TemporaryDirectory(prefix='enaptic-plan-') as temporary:
        root=Path(temporary);cache=root/'var/cache/apk';cache.mkdir(parents=True)
        for source in input_files():
            if str(source).startswith('/etc/apk/keys/'):continue
            destination=root/str(source).lstrip('/');destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)
        world=root/'etc/apk/world';original=world.read_text();world.write_text(edited_world(original,marks))
        from native_bridge import solve
        changes,identity,totals,output=solve(request,root,world.read_text())
        if fingerprint()!=before:raise RuntimeError('Live package state changed during preview. Read Cache and retry.')
        installed_process=subprocess.run(['apk','--network=no','--logfile=no','query','--from','installed','--format','json','--fields','name,version','*'],capture_output=True,text=True,timeout=30)
        if installed_process.returncode:raise RuntimeError(installed_process.stderr.strip())
        installed={p['name'] for p in json.loads(installed_process.stdout)}
        removed={c['name'] for c in changes if c['action']=='Purging'}
        retained=[m['name'] for m in marks if m['action']=='remove' and m['name'] in installed and m['name'] not in removed]
        explicit={m['name'] for m in marks}
        for c in changes:c['reason']='Requested' if c['name'] in explicit else 'Native upgrade' if request.get('upgrade_all') and c['action'] in ('Upgrading','Downgrading') else 'Dependency / native cleanup'
        if fingerprint()!=before:raise RuntimeError('Live package state changed during preview. Read Cache and retry.')
        return dict(changes=changes,retained=retained,fingerprint=before,output=output,totals=totals,identity=identity,request=request)

def text(result):
    lines=['Transaction preview — no changes applied','',f"{len(result['changes'])} proposed package changes",'']
    for mark in result.get('request',{}).get('marks',[]):lines.append(f"Requested world change: {mark['action']} {mark['name']}")
    for change in result['changes']:lines.append(f"{change['action']}: {change['name']}  {change['old']} → {change['new']}  [{change['reason']}]")
    for name in result['retained']:lines.append(f'NOT REMOVED: {name} is still required by the selected world / dependency graph.')
    lines+=['',f"Download estimate: {(result.get('totals') or {}).get('download','Unavailable')} bytes; disk change: {(result.get('totals') or {}).get('disk','Unavailable')} bytes",'Apply will revalidate this state and exact native package identities under APK’s database lock.']
    return '\n'.join(lines)
