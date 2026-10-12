#!/usr/bin/python3
"""Root-owned, narrow privileged entrypoint. No caller commands or paths."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import re
import subprocess
import sys
import tempfile
import urllib.request

# Installed sibling modules must be root-owned and not group/world writable.
HERE=Path(__file__).resolve().parent
if os.geteuid()!=0:raise SystemExit('Administrator authentication required')
for p in [HERE,*HERE.glob('*.py'),HERE/'enaptic-transaction']:
    info=p.stat()
    if info.st_uid or info.st_mode&0o022:raise SystemExit('Unsafe helper installation')
sys.path.insert(0,str(HERE))
import planner
import native_bridge
import sources

ENV={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LC_ALL':'C','LANG':'C','HOME':'/root'}
os.environ.clear();os.environ.update(ENV)

def atomic(path,data):
    info=path.lstat() if path.exists() else None
    if info and (not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_mode&0o022):raise RuntimeError('Unsafe system configuration file')
    fd,name=tempfile.mkstemp(prefix='.enaptic-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),stat.S_IMODE(info.st_mode) if info else 0o644)
        os.replace(name,path)
        parent=os.open(path.parent,os.O_DIRECTORY);os.fsync(parent);os.close(parent)
    finally:
        if os.path.exists(name):os.unlink(name)

def emit(line):
    try:sys.stdout.buffer.write(line);sys.stdout.flush()
    except BrokenPipeError:pass

def apply(review):
    if not isinstance(review,dict) or set(review)!={'request','fingerprint','identity'}:raise ValueError('Invalid reviewed transaction')
    planner.validate_request(review['request'])
    version=subprocess.check_output(['/sbin/apk','--version'],env=ENV,text=True)
    if not version.startswith('apk-tools 3.0.8-'):raise RuntimeError('This native bridge requires APK 3.0.8; rebuild before applying with another APK version.')
    if not isinstance(review['fingerprint'],str) or not re.fullmatch('[0-9a-f]{64}',review['fingerprint']) or not isinstance(review['identity'],str) or len(review['identity'])>1024*1024:raise ValueError('Invalid transaction binding')
    if planner.fingerprint()!=review['fingerprint']:raise RuntimeError('STALE: package state or sources changed. Preview again.')
    process=subprocess.Popen([str(HERE/'enaptic-transaction'),'apply'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=ENV,bufsize=0)
    try:
        line=process.stdout.readline()
        while line and line!=b'LOCKED\n':
            emit(line);line=process.stdout.readline()
        if line!=b'LOCKED\n':raise RuntimeError('APK could not acquire its native database lock')
        if planner.fingerprint()!=review['fingerprint']:
            process.stdin.close();process.wait(timeout=10);raise RuntimeError('STALE: package state changed while acquiring the lock. Preview again.')
        world=planner.edited_world(Path('/etc/apk/world').read_text(),review['request'].get('marks',[]))
        process.stdin.write(native_bridge.protocol(review['request'],world,review['identity']));process.stdin.close()
        # The bridge compares exact old/new versions, digests, tags and reinstall
        # state, then commits that same changeset with the native lock held.
        for line in iter(process.stdout.readline,b''):
            emit(line)
        code=process.wait()
        if code:raise RuntimeError('APK transaction failed. Review the log and current package state; partial changes may have occurred.')
        print('Completed. Modified configuration files may have .apk-new companions; review APK messages above.')
    finally:
        if process.poll() is None:
            # Never close/kill a transaction after it has started committing.
            if not process.stdin.closed:process.stdin.close()
            process.wait()

def modify_source(operation):
    if not isinstance(operation,dict) or set(operation)-{'action','index','url','digest','allow_cross_release'}:raise ValueError('Invalid repository request')
    path=sources.REPOSITORIES;text=path.read_text()
    if sources.source_digest(text)!=operation.get('digest'):raise RuntimeError('STALE: repository file changed. Reopen Repositories.')
    if operation['action']=='add':
        url=sources.valid_url(operation['url']);branch=sources.release()
        branches=re.findall(r'/(edge|v\d+\.\d+)(?:/|$)',url+'/')
        if any(b!=branch for b in branches):
            if operation.get('allow_cross_release') is not True:raise ValueError('Cross-release source requires explicit override; stable/edge mixing is not enabled by this UI.')
    updated=sources.edit(text,operation)
    backup=Path('/var/lib/enaptic');backup.mkdir(mode=0o700,parents=True,exist_ok=True)
    atomic(backup/('repositories-'+sources.source_digest(text)+'.bak'),text.encode())
    atomic(path,updated.encode());print('Repository configuration saved. Reload to fetch indexes. Signing-key trust was not changed.')

def trust_key(identifier):
    record=next((r for r in sources.known() if r['id']==identifier and 'sha256' in r),None)
    if not record:raise ValueError('No vetted signing key for this source')
    with urllib.request.urlopen(record['key_url'],timeout=20) as response:data=response.read(16385)
    if len(data)>16384 or hashlib.sha256(data).hexdigest()!=record['sha256']:raise RuntimeError('Signing key fingerprint mismatch; trust unchanged')
    if b'BEGIN PUBLIC KEY' not in data:raise RuntimeError('Unexpected signing key format')
    path=Path('/etc/apk/keys')/record['key']
    if path.exists() and path.read_bytes()!=data:raise RuntimeError('Existing signing key differs; refusing replacement')
    atomic(path,data);print('Trusted '+record['key']+' SHA256 '+record['sha256'])

def main():
    raw=sys.stdin.buffer.read(2*1024*1024+1)
    if len(raw)>2*1024*1024:raise ValueError('Request too large')
    request=json.loads(raw)
    if not isinstance(request,dict) or set(request)!={'operation','payload'}:raise ValueError('Invalid helper request')
    op=request['operation']
    if op=='apply':apply(request['payload']);return
    if op not in ('reload','source','trust'):raise ValueError('Unsupported helper operation')
    with open('/lib/apk/db/lock','a') as lock:
        # Repository/key edits coordinate with native APK. Update obtains its
        # own native lock, so do not retain our extra lock around that child.
        if op=='reload':
            if request['payload'] is not None:raise ValueError('Reload does not accept options')
            result=subprocess.run(['/sbin/apk','--wait','10','--progress=no','--pretty-print=no','update'],env=ENV)
            if result.returncode:raise RuntimeError('Index refresh was incomplete; review the source errors above.')
        else:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            if op=='source':modify_source(request['payload'])
            else:trust_key(request['payload'])

if __name__=='__main__':
    try:main()
    except (ValueError,TypeError,KeyError,RuntimeError,OSError,subprocess.SubprocessError) as e:print(str(e),file=sys.stderr);sys.exit(1)
