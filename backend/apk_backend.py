#!/usr/bin/env python3
"""Unprivileged package browser; APK writes go through the authenticated helper."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

FIELDS='name,version,description,repositories,origin,license'

def query(*args,fields=FIELDS):
    p=subprocess.run(['apk','--network=no','--logfile=no','query','--format','json','--fields',fields,*args],capture_output=True,text=True,timeout=30)
    if p.returncode:raise RuntimeError(p.stderr.strip() or 'APK query failed')
    if len(p.stdout)>64*1024*1024:raise RuntimeError('APK response exceeds catalog limit')
    data=json.loads(p.stdout)
    if not isinstance(data,list):raise RuntimeError('Unexpected APK query format')
    return data

def catalog():
    installed={p['name']:p for p in query('--from','installed','*')}
    candidates={p['name']:p for p in query('--from','repositories','*')}
    upgrades={p['name'] for p in query('--upgradable','*',fields='name')}
    rows=[]
    for name in sorted(installed.keys()|candidates.keys()):
        p=candidates.get(name,installed.get(name)); old=installed.get(name)
        repos=[r for r in p.get('repositories',[]) if '://' in r or r.startswith('/')]
        rows.append(dict(name=name,installed=old['version'] if old else '—',candidate=candidates[name]['version'] if name in candidates else '—',description=p.get('description',''),repository=', '.join(repos) or 'Installed only',origin=p.get('origin',''),license=p.get('license',''),upgradable=name in upgrades))
    return rows

def details(name):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9+_.-]*',name):raise ValueError('Invalid package name')
    found=query(name,fields='all')
    if not found:raise ValueError('Package no longer available')
    p=found[0]
    lines=[f"{p['name']} — {p['version']}",'',p.get('description',''),'',f"Source package: {p.get('origin','Unavailable')}",f"License: {p.get('license','Unavailable')}",f"Project: {p.get('url','Unavailable')}",f"Architecture: {p.get('arch','Unavailable')}",f"Installed size: {p.get('installed-size','Unavailable')} bytes",f"Download size: {p.get('file-size','Unavailable')} bytes",'', 'Repositories:',*p.get('repositories',['Unavailable']),'','Dependencies:',*p.get('depends',['None recorded']),'','Reverse dependencies:',*p.get('reverse-depends',['None recorded'])]
    installed=query('--from','installed',name,fields='name,version,contents')
    lines+=['','Installed files:']
    if installed:
        files=installed[0].get('contents',[])
        lines+=files[:256] or ['No file list supplied by APK']
        if len(files)>256:lines.append(f'… showing first 256 of {len(files)} paths')
    else:lines.append('Not installed; an installed file list is unavailable.')
    return '\n'.join(lines)

def clean(value):return str(value).replace('\t',' ').replace('\r',' ').replace('\n',' ')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['catalog','details','repositories','plan','apply','reload','source','trust','flatpak-details']);parser.add_argument('name',nargs='?');args=parser.parse_args()
    try:
        if args.action=='catalog':
            import flatpak_backend
            apk_rows=catalog()
            for row in apk_rows:row.update(provider='APK',identity=row['name'],scope='system')
            flatpak_rows,warnings=flatpak_backend.catalog()
            for warning in warnings:print(warning,file=sys.stderr)
            for row in apk_rows+flatpak_rows:print('\t'.join(clean(row[key]) for key in ['name','installed','candidate','description','repository','origin','license','upgradable','provider','identity','scope']))
        elif args.action=='flatpak-details':
            import flatpak_backend
            print(flatpak_backend.details(args.name or ''))
        elif args.action=='details':print(details(args.name or ''))
        elif args.action=='plan':
            import planner
            request=json.loads(Path(args.name).read_text());result=planner.preview(request)
            review=dict(request=request,fingerprint=result['fingerprint'],identity=result.get('identity',''));Path(args.name).write_text(json.dumps(review))
            for change in result['changes']:
                print('CHANGE\t'+'\t'.join(clean(change[k]) for k in ['name','old','new','action','reason']))
            print('TEXT')
            print(planner.text(result))
        elif args.action=='repositories':
            import sources
            result=sources.listing()
            print('DIGEST\t'+result['digest'])
            for row in result['rows']:print('SOURCE\t'+str(row['index'])+'\t'+str(int(row['enabled']))+'\t'+clean(row['url']))
            for row in result['known']:print('KNOWN\t'+row['id']+'\t'+clean(row['name'])+'\t'+row['url']+'\t'+clean(row['note']))
            print('TEXT');print('Alpine '+result['branch']+' software sources. Select a source to enable, disable or remove it. Add a known compatible source or enter an HTTPS URL. Source activation and signing-key trust are separate.\n\nTrusted key fingerprints:')
            for key in result['keys']:print(key['name']+'  SHA256 '+key['sha256'])
            for path,text in result['additional'].items():print('\nAdditional configuration (inspect only): '+path+'\n'+text)
        else:
            payload=None if args.action=='reload' else json.loads(Path(args.name).read_text())
            command=['pkexec','/usr/libexec/enaptic/enaptic-helper']
            process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            process.stdin.write(json.dumps(dict(operation=args.action,payload=payload)).encode());process.stdin.close()
            for line in iter(process.stdout.readline,b''):
                sys.stdout.buffer.write(line);sys.stdout.flush()
            if process.wait():raise RuntimeError('Authenticated operation failed; see the log above.')
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as e:print(str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__':sys.exit(main())
