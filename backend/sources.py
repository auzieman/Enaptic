"""Source discovery/validation; editing and trust are separate helper operations."""
import hashlib
from pathlib import Path
import re
from urllib.parse import urlsplit

REPOSITORIES=Path('/etc/apk/repositories')
COMPANION_KEY='builder-6acd560b.rsa.pub'
COMPANION_SHA='f308145bc1a64270e85f58d8af810015a5e2605a5bba1ddbeb2f86da65a42bd4'

def release():
    value=Path('/etc/alpine-release').read_text().strip()
    match=re.match(r'^(\d+\.\d+)\.',value)
    return 'v'+match[1] if match else 'edge'

def known():
    branch=release()
    items=[dict(id=section,name='Alpine '+section,url=f'https://dl-cdn.alpinelinux.org/alpine/{branch}/{section}',note='Official Alpine; uses installed Alpine signing keys.') for section in ['main','community']]
    if branch=='v3.24':items.append(dict(id='companion',name='AlpinE companion apps',url='https://auzix.auzietek.com/alpine/repo/apps/v3.24',note='Third-party AlpinE feed; separately review its signing key.',key=COMPANION_KEY,sha256=COMPANION_SHA,key_url='https://auzix.auzietek.com/alpine/repo/apps/v3.24/'+COMPANION_KEY))
    return items

def valid_url(url):
    if not isinstance(url,str) or len(url)>2048 or any(c.isspace() for c in url):raise ValueError('A repository must be one HTTPS URL without whitespace.')
    p=urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.query or p.fragment:raise ValueError('Use an HTTPS repository URL without credentials, query or fragment.')
    return url.rstrip('/')

def source_digest(text):return hashlib.sha256(text.encode()).hexdigest()

def entries(text):
    rows=[]
    for index,line in enumerate(text.splitlines()):
        stripped=line.strip();enabled=not stripped.startswith('#');body=stripped if enabled else stripped.lstrip('#').strip()
        if not body or body.startswith('#'):continue
        parts=body.split()
        if parts[0].startswith('@'):parts=parts[1:]
        if not parts or not parts[0].startswith(('https://','http://','/')):continue
        rows.append(dict(index=index,enabled=enabled,url=parts[0],line=line))
    return rows

def edit(text,operation):
    action=operation.get('action');lines=text.splitlines(keepends=True)
    if action=='add':
        url=valid_url(operation['url'])
        if any(r['url'].rstrip('/')==url for r in entries(text)):raise ValueError('Source already configured; enable the existing entry.')
        return text+('' if not text or text.endswith('\n') else '\n')+url+'\n'
    if action not in ('enable','disable','remove'):raise ValueError('Unsupported source operation')
    index=operation.get('index')
    if not isinstance(index,int) or isinstance(index,bool) or index<0 or index>=len(lines):raise ValueError('Invalid source selection')
    row=next((r for r in entries(text) if r['index']==index),None)
    if not row:raise ValueError('Selected line is not a repository')
    if action=='remove':del lines[index]
    elif action=='enable' and not row['enabled']:
        prefix=len(lines[index])-len(lines[index].lstrip());lines[index]=lines[index][:prefix]+lines[index][prefix:].lstrip('#').lstrip()
    elif action=='disable' and row['enabled']:lines[index]='# '+lines[index]
    return ''.join(lines)

def listing():
    text=REPOSITORIES.read_text();rows=entries(text);catalog=known();keys=[]
    for p in sorted(Path('/etc/apk/keys').glob('*')):
        if p.is_file():keys.append(dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    additional={str(p):p.read_text() for p in sorted(Path('/etc/apk/repositories.d').glob('*')) if p.is_file()}
    return dict(digest=source_digest(text),rows=rows,known=catalog,keys=keys,additional=additional,branch=release())
