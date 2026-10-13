"""Read-only cached Flatpak catalog; never installs, updates or edits remotes."""
import base64
import json
import os
import re
import shutil
import subprocess

SCOPES=('user','system')
REF=re.compile(r'(app|runtime)/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
REMOTE=re.compile(r'[A-Za-z0-9_.-]+\Z')

def run(scope,command,*args):
    if scope not in SCOPES:raise ValueError('Invalid Flatpak scope')
    process=subprocess.run(['flatpak',command,'--'+scope,*args],capture_output=True,text=True,timeout=35,env=os.environ|{'LC_ALL':'C','FLATPAK_FANCY_OUTPUT':'0','TERM':'dumb'})
    if process.returncode:raise RuntimeError(process.stderr.strip() or 'Flatpak query failed')
    if len(process.stdout)>32*1024*1024:raise RuntimeError('Flatpak response exceeds catalog limit')
    return process.stdout

def rows(output,count):
    result=[]
    for line in output.splitlines():
        if not line:continue
        fields=line.split('\t')
        if len(fields)!=count:raise RuntimeError('Unexpected Flatpak column format')
        result.append(fields)
    return result

def identity(scope,origin,ref):
    return 'fp_'+base64.urlsafe_b64encode(json.dumps(dict(scope=scope,origin=origin,ref=ref),sort_keys=True,separators=(',',':')).encode()).decode().rstrip('=')

def decode(token):
    if not isinstance(token,str) or not token.startswith('fp_') or len(token)>700:raise ValueError('Invalid Flatpak identity')
    try:value=json.loads(base64.b64decode(token[3:]+'='*((-len(token[3:]))%4),altchars=b'-_',validate=True))
    except (ValueError,UnicodeError):raise ValueError('Invalid Flatpak identity') from None
    if not isinstance(value,dict) or set(value)!={'scope','origin','ref'} or value['scope'] not in SCOPES or not isinstance(value['ref'],str) or not REF.fullmatch(value['ref']) or not isinstance(value['origin'],str) or not REMOTE.fullmatch(value['origin']):raise ValueError('Invalid Flatpak identity')
    return value

def normal_ref(ref,kind):
    value=ref if ref.startswith(('app/','runtime/')) else kind+'/'+ref
    if not REF.fullmatch(value):raise RuntimeError('Unsupported Flatpak reference')
    return value

def catalog():
    if not shutil.which('flatpak'):return [],['Flatpak is not installed; APK browsing is available.']
    result=[];warnings=[]
    for scope in SCOPES:
        for kind in ('app','runtime'):
            try:
                installed={};available={}
                for ref,name,version,origin,description,commit in rows(run(scope,'list','--'+kind,'--columns=ref:full,name:full,version:full,origin:full,description:full,active:full'),6):
                    installed[(normal_ref(ref,kind),origin)]=(name,version,description,commit)
                for ref,name,version,origin,description,commit in rows(run(scope,'remote-ls','--cached','--'+kind,'--columns=ref:full,name:full,version:full,origin:full,description:full,commit:full'),6):
                    available[(normal_ref(ref,kind),origin)]=(name,version,description,commit)
                updates=set((normal_ref(r[0],kind),r[1]) for r in rows(run(scope,'remote-ls','--cached','--updates','--'+kind,'--columns=ref:full,origin:full'),2))
                for key in sorted(installed.keys()|available.keys()):
                    ref,origin=key;full=ref if ref.startswith(('app/','runtime/')) else kind+'/'+ref
                    if not REF.fullmatch(full) or not REMOTE.fullmatch(origin):raise RuntimeError('Unsupported Flatpak identity from catalog')
                    old=installed.get(key);candidate=available.get(key);item=candidate or old;name,version,description,commit=item
                    result.append(dict(name=full.split('/')[1],installed=(old[1] or old[3][:12] or full.split('/')[-1]) if old else '—',candidate=(candidate[1] or candidate[3][:12] or full.split('/')[-1]) if candidate else '—',description=name+' — '+description,repository=origin,origin=kind,license='Unavailable',upgradable=key in updates,provider='Flatpak',identity=identity(scope,origin,full),scope=scope))
            except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as e:warnings.append(f'Flatpak {scope}/{kind}: {e}')
    return result,warnings

def details(token):
    item=decode(token);scope,origin,ref=item['scope'],item['origin'],item['ref']
    installed=run(scope,'list','--'+ref.split('/')[0],'--columns=ref:full,origin:full')
    short=ref.split('/',1)[1];present=any(r[0] in (ref,short) and r[1]==origin for r in rows(installed,2))
    if present:
        info=run(scope,'info',ref);metadata=run(scope,'info','--show-metadata',ref)
        permissions=run(scope,'info','--show-permissions',ref)
    else:
        info=run(scope,'remote-info','--cached',origin,ref);metadata=run(scope,'remote-info','--cached','--show-metadata',origin,ref);permissions='Installed permissions are unavailable; review the sandbox metadata below.'
    return f'Flatpak — {ref}\nInstallation: {scope}\nRemote: {origin}\n\nBrowsing only. Flatpak installation/update reviews are not implemented. Cached metadata may be stale; displayed versions can lag the actual remote commit.\n\n{info}\n\nPermissions:\n{permissions}\n\nMetadata:\n{metadata}'
