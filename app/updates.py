"""Verified app-only GitHub releases; runtime ABI remains fixed, data is never replaced."""
from pathlib import Path
import json,os,re,sys,hashlib,zipfile,urllib.request,time
ROOT=Path(__file__).resolve().parents[1];SETTINGS=ROOT/'data/settings';UPDATES=ROOT/'runtime/updates';TOOL_ID='cy.tools.subtitle';ABI='py311-fermion0214-core0110-subtitle2'
def read(path,default=None):
    try:return json.loads(path.read_text('utf-8'))
    except FileNotFoundError:return {} if default is None else default

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2),encoding='utf-8');tmp.replace(path)
def read_settings():return read(SETTINGS/'updates.json')
def write_settings(settings):
    repo=settings.get('repository','').strip()
    if repo and not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Use owner/repository')
    write(SETTINGS/'updates.json',settings)
def request(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CyTools-Subtitle'}),timeout=60)
def check():
    settings=read_settings();repo=settings.get('repository','')
    if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Configure the Tool GitHub repository first. No public repository is assumed.')
    with request('https://api.github.com/repos/'+repo+'/releases/latest')as response:release=json.load(response)
    value={'repository':repo,'release':release,'installed':read(ROOT/'app/release.json').get('version','Unknown')};write(SETTINGS/'update-available.json',value);return value

def extract(archive,destination):
    destination=Path(destination).resolve()
    with zipfile.ZipFile(archive)as bundle:
        members=bundle.infolist()
        if len(members)>10000 or sum(m.file_size for m in members)>256*1024**2:raise ValueError('Oversized release archive')
        for info in members:
            name=info.filename;parts=Path(name).parts
            if not parts or parts[0]!='app' or chr(92) in name or ':'in name or '..'in parts:raise ValueError('Only confined app/ files are accepted')
            target=(destination/name).resolve()
            if not target.is_relative_to(destination) or (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe archive path or symbolic link')
        bundle.extractall(destination)
    if not (destination/'app/CyTool.json').is_file() or not (destination/'app/release.json').is_file():raise ValueError('Missing release metadata')
    from cytools_core import load_manifest
    manifest=load_manifest(destination/'app/CyTool.json');release=read(destination/'app/release.json')
    if manifest['id']!=TOOL_ID or release.get('runtime_abi')!=ABI or release.get('platform') not in ('any',sys.platform):raise ValueError('Tool identity, platform or runtime ABI mismatch')
    if not (destination/'app/desktop.py').is_file():raise ValueError('Missing desktop entry point')
    import ast
    for source in (destination/'app').rglob('*.py'):
        ast.parse(source.read_text('utf-8-sig'),filename=str(source))
    return destination/'app' 

def download():
    value=check();assets={a['name']:a for a in value['release']['assets']};name='cytools-app.zip'
    def url(name):
        result=assets[name]['browser_download_url']
        if not result.startswith('https://github.com/'+value['repository']+'/releases/download/'):raise ValueError('Unexpected release URL')
        return result
    with request(url(name+'.sha256'))as stream:digest=stream.read(512).decode('ascii').split()[0]
    if not re.fullmatch('[a-fA-F0-9]{64}',digest):raise ValueError('Invalid SHA256')
    from cytools_core.shared_installation import InstallationStorage
    result=InstallationStorage(ROOT).download(url(name),sha256=digest.lower(),size=assets[name]['size'])
    if result['state']!='Completed':raise RuntimeError(str(result))
    candidate=extract(result['path'],UPDATES/digest.lower())
    write(SETTINGS/'update-pending.json',{'app':str(candidate.relative_to(ROOT))});return {'state':'Staged; restart to activate','app':str(candidate)}

def idle():
    import psutil
    for process in psutil.process_iter(['pid','cmdline']):
        if process.pid==os.getpid():continue
        command=process.info['cmdline'] or []
        for arg in command:
            try:
                path=Path(arg).resolve()
                if path.is_relative_to(ROOT/'app') and path.name in ('worker.py','desktop.py','tool.py','install_models.py'):raise RuntimeError('Close other Tool windows and finish active jobs before activation.')
            except (OSError,ValueError):pass

def apply():
    pending=read(SETTINGS/'update-pending.json')
    if not pending:return
    from filelock import FileLock
    UPDATES.mkdir(parents=True,exist_ok=True)
    with FileLock(str(UPDATES/'activation.lock'),timeout=1):
        idle();candidate=(ROOT/pending['app']).resolve()
        if not candidate.is_relative_to(UPDATES.resolve()) or not (candidate/'desktop.py').is_file():raise ValueError('Invalid staged app')
        from cytools_core import load_manifest
        if load_manifest(candidate/'CyTool.json')['id']!=TOOL_ID or read(candidate/'release.json').get('runtime_abi')!=ABI:raise ValueError('Invalid staged identity or ABI')
        backup=UPDATES/('previous-'+str(time.time_ns()));(ROOT/'app').rename(backup)
        try:candidate.rename(ROOT/'app')
        except Exception:backup.rename(ROOT/'app');raise
        write(SETTINGS/'update-previous.json',{'app':str(backup.relative_to(ROOT))});(SETTINGS/'update-pending.json').unlink()

def rollback():
    previous=read(SETTINGS/'update-previous.json')
    if not previous:raise ValueError('No previous app version')
    write(SETTINGS/'update-pending.json',previous);return {'state':'Rollback staged for next launch'}
if __name__=='__main__':
    try:print(json.dumps({'check':check,'download':download,'rollback':rollback,'apply':apply}[sys.argv[1]](),indent=2))
    except Exception as exc:print(str(exc),file=sys.stderr);sys.exit(1)
