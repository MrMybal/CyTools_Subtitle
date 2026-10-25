"""Optional NVIDIA native diarization. No neural or graphical imports here."""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid
import wave
import zipfile

CATALOG=json.loads(Path(__file__).with_name('nemotron-catalog.json').read_text('utf-8'))
MODEL=CATALOG['model']['id']
GEOMETRY={'chunk':340,'right_context':40,'left_context':-1,'fifo':40,'spkcache':264,'update_period':300}
SEGMENTATION={'onset':.641,'offset':.561,'pad_onset':.229,'pad_offset':.079,'min_duration_on':.511,'min_duration_off':.296}
OPTION_KEYS=('nemotron_device','nemotron_mode','nemotron_preset',*[f'nemotron_{k}' for k in GEOMETRY],*[f'nemotron_{k}' for k in SEGMENTATION])


def read(path):
    try:
        value=json.loads(Path(path).read_text('utf-8'))
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):return {}


def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.'+uuid.uuid4().hex+'.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n','utf-8');temporary.replace(path)


def digest(path,cancellation=None):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while data:=f.read(1024**2):
            if cancellation:cancellation.check()
            h.update(data)
    return h.hexdigest()


def active_runtime(root,backend,verify=False):
    if backend not in CATALOG['runtimes']:raise ValueError('Expected cpu or cuda')
    base=(Path(root)/'runtime/components/nemotron'/backend).resolve();marker=read(base/'active.json')
    try:
        directory=(base/marker['directory']).resolve();reference=CATALOG['runtimes'][backend]
        if marker.get('schemaVersion')!=1 or marker.get('archiveSha256')!=reference['sha256'] or directory==base or not directory.is_relative_to(base):return None
        executable=(directory/reference['executable']).resolve()
        if not executable.is_file() or not executable.is_relative_to(directory) or not isinstance(marker.get('files'),dict) or not marker['files']:return None
        if any(not isinstance(name,str) or not isinstance(expected,str) for name,expected in marker['files'].items()):return None
        if verify:
            for name,expected in marker['files'].items():
                path=(directory/name).resolve()
                if not path.is_relative_to(directory) or digest(path)!=expected:raise ValueError('NVIDIA runtime checksum mismatch; repair it from Installation')
        return executable
    except (KeyError,TypeError,OSError):return None


def model_record(root):return read(Path(root)/'data/settings/nemotron.json')


def verify_model(path,cancellation=None):
    path=Path(path).resolve();reference=CATALOG['model']
    if not path.is_file() or path.stat().st_size!=reference['size'] or digest(path,cancellation)!=reference['sha256']:raise ValueError('Expected the official pinned Nemotron 3 Q8_0 GGUF; file size or checksum mismatch')
    return {'path':str(path),'model':MODEL,'revision':reference['revision'],'sha256':reference['sha256'],'license':reference['license']}


def status(root):
    record=model_record(root);path=record.get('path','');model_ready=False
    try:model_ready=bool(isinstance(path,str) and path and Path(path).is_file() and Path(path).stat().st_size==CATALOG['model']['size'] and record.get('sha256')==CATALOG['model']['sha256'])
    except OSError:pass
    cpu=active_runtime(root,'cpu');cuda=active_runtime(root,'cuda')
    return {'model':MODEL,'revision':CATALOG['model']['revision'],'quantization':'Q8_0','license':CATALOG['model']['license'],'source':CATALOG['model']['source'],'runtimeVersion':CATALOG['runtimeVersion'],'cpuReady':cpu is not None,'cudaReady':cuda is not None,'modelReady':model_ready,'ready':model_ready and (cpu is not None or cuda is not None),'modelPath':path if isinstance(path,str) else '', 'cpuRuntimePath':str(cpu or ''),'cudaRuntimePath':str(cuda or ''),'state':'Installed' if model_ready and (cpu or cuda) else 'Missing'}


def clean_environment(root):
    env={k:v for k,v in os.environ.items() if not k.upper().startswith('NEMO_SPEECH_')}
    env['NEMO_SPEECH_MODEL_DIR']=str(Path(root)/'data/models/nemotron');env['NO_COLOR']='1'
    return env


def command(executable,args,root,timeout=120):
    return subprocess.run([str(executable),*args],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,creationflags=0x08000000 if os.name=='nt' else 0,env=clean_environment(root))


def probe(root,backend):
    executable=active_runtime(root,backend)
    if executable is None:raise RuntimeError('Install the selected NVIDIA runtime from Installation')
    result=command(executable,['--json','doctor'],root,15)
    if result.returncode:raise RuntimeError('NVIDIA runtime could not start: '+result.stderr[-2000:])
    value=json.loads(result.stdout)
    return {'version':value.get('version',''),'cudaAvailable':bool(value.get('accelerator_available') and value.get('features',{}).get('backend_cuda') and value.get('driver_runtime_compatible')),'devices':[{'name':d.get('name',''),'description':d.get('description',''),'type':d.get('type',''),'index':d.get('index',0),'memoryTotalBytes':d.get('memory_total',0)} for d in value.get('devices',[])],'warnings':value.get('runtime_warnings',[])}


def download(root,reference,license_accepted):
    if license_accepted is not True:raise ValueError('Explicit license acceptance is required for this installation')
    from cytools_core.shared_installation import InstallationStorage
    result=InstallationStorage(root).download(reference['url'],sha256=reference['sha256'],size=reference['size'],license_accepted=license_accepted)
    if result['state']!='Completed':raise RuntimeError('NVIDIA download incomplete: '+result['state'])
    return Path(result['path'])


def extract_verified(archive,destination):
    destination=Path(destination).resolve()
    with zipfile.ZipFile(archive) as bundle:
        entries=bundle.infolist()
        if len(entries)>2000 or sum(e.file_size for e in entries)>1024**3:raise ValueError('Unexpected NVIDIA archive size')
        for entry in entries:
            path=(destination/entry.filename).resolve()
            if not path.is_relative_to(destination) or stat.S_ISLNK(entry.external_attr>>16):raise ValueError('Unsafe NVIDIA archive path')
        bundle.extractall(destination)


def install_runtime(root,backend,license_accepted=False):
    if sys.platform!='win32' or sys.maxsize<=2**32:raise RuntimeError('Guided NVIDIA installation supports Windows x64 only')
    root=Path(root).resolve();reference=CATALOG['runtimes'][backend];archive=download(root,reference,license_accepted)
    base=root/'runtime/components/nemotron'/backend;base.mkdir(parents=True,exist_ok=True)
    destination=base/uuid.uuid4().hex;destination.mkdir()
    extract_verified(archive,destination)
    executable=destination/reference['executable'];result=command(executable,['--version'],root,15)
    if result.returncode or result.stdout.strip()!='nemo-speech '+CATALOG['runtimeVersion']:raise RuntimeError('NVIDIA candidate runtime verification failed')
    doctor=command(executable,['--json','doctor'],root,15)
    if doctor.returncode or not json.loads(doctor.stdout).get('features',{}).get('diarization'):raise RuntimeError('NVIDIA candidate does not expose diarization')
    marker={'schemaVersion':1,'directory':destination.name,'archiveSha256':reference['sha256'],'files':{p.relative_to(destination).as_posix():digest(p) for p in destination.rglob('*') if p.is_file()}}
    atomic(base/'active.json',marker)
    return status(root)


def install_model(root,license_accepted=False):
    root=Path(root).resolve();reference=CATALOG['model'];cached=download(root,reference,license_accepted)
    destination=root/'data/models/nemotron'/uuid.uuid4().hex;destination.mkdir(parents=True)
    path=destination/reference['filename'];shutil.copyfile(cached,path);record=verify_model(path)
    atomic(root/'data/settings/nemotron.json',record)
    return status(root)


def options(parameters):
    p=parameters
    inactive={'speaker_count':0,'min_speakers':1,'max_speakers':16,'segmentation_batch_size':1,'embedding_batch_size':8}
    for key,default in inactive.items():
        if p.get(key,default)!=default:raise ValueError(key+' is a Community-1 setting; leave its default for Nemotron (automatic, up to eight voices)')
    result={key:p[key] for key in OPTION_KEYS};result['threads']=p['threads'];result['max_seconds']=p['diarization_max_seconds']
    if result['nemotron_mode']=='full' and result['nemotron_preset']!='v3-offline':raise ValueError('Full attention does not use a streaming preset; leave v3-offline selected')
    if result['nemotron_preset']!='custom' or result['nemotron_mode']=='full':
        for key,default in GEOMETRY.items():
            if result['nemotron_'+key]!=default:raise ValueError('Custom geometry requires the custom chunked preset')
    return result


def limit_cpu(threads):
    """Limit this one-shot worker; its native child inherits the CPU affinity."""
    if sys.platform!='win32':raise RuntimeError('NVIDIA native integration is currently validated on Windows only')
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.GetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
    kernel.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
    process=kernel.GetCurrentProcess();allowed=ctypes.c_size_t();system=ctypes.c_size_t()
    if not kernel.GetProcessAffinityMask(process,ctypes.byref(allowed),ctypes.byref(system)):raise ctypes.WinError(ctypes.get_last_error())
    bits=[1<<i for i in range(ctypes.sizeof(ctypes.c_size_t)*8) if allowed.value&(1<<i)][:threads]
    if not bits or not kernel.SetProcessAffinityMask(process,sum(bits)):raise ctypes.WinError(ctypes.get_last_error())
    return len(bits)


def exclusive_timeline(turns):
    # NeMo emits overlapping activity. Derive a single-caption timeline while
    # retaining its original intervals separately for review.
    events={}
    for index,turn in enumerate(turns):
        events.setdefault(turn['start'],[]).append((True,index));events.setdefault(turn['end'],[]).append((False,index))
    active=set();previous=None;current=None;result=[]
    for time in sorted(events):
        if previous is not None and time>previous and current is not None:
            speaker=turns[current]['speaker']
            if result and result[-1]['speaker']==speaker and abs(result[-1]['end']-previous)<1e-6:result[-1]['end']=time
            else:result.append({'start':previous,'end':time,'speaker':speaker})
        for entering,index in events[time]:
            if entering:active.add(index)
            else:active.discard(index)
        if current not in active:current=min(active,key=lambda i:(turns[i]['start'],i)) if active else None
        previous=time
    return result


def normalize_segments(value,duration):
    if not isinstance(value,dict) or not isinstance(value.get('segments'),list) or len(value['segments'])>200000:raise ValueError('Invalid NVIDIA speaker result')
    turns=[]
    for turn in value['segments']:
        if not isinstance(turn,dict):raise ValueError('Invalid NVIDIA speaker segment')
        start,end,speaker=turn.get('start'),turn.get('end'),turn.get('speaker')
        if not all(isinstance(t,(int,float)) and not isinstance(t,bool) and math.isfinite(t) for t in (start,end)) or end<=start or not isinstance(speaker,int) or isinstance(speaker,bool) or not 1<=speaker<=8:raise ValueError('Invalid NVIDIA speaker timing or identity')
        start,end=round(max(0.,start),6),round(min(duration,end),6)
        if end>start:turns.append({'start':start,'end':end,'nativeSpeaker':speaker})
    turns.sort(key=lambda t:(t['start'],t['end'],t['nativeSpeaker']))
    labels=list(dict.fromkeys(t['nativeSpeaker'] for t in turns));ids={label:f'speaker-{i+1}' for i,label in enumerate(labels)}
    segments=[{'start':t['start'],'end':t['end'],'speaker':ids[t['nativeSpeaker']]} for t in turns]
    return [{'id':ids[label],'name':f'Person {i+1}'} for i,label in enumerate(labels)],segments,exclusive_timeline(segments)


def infer(root,audio,options,scratch):
    root=Path(root).resolve();device=options['nemotron_device'];executable=active_runtime(root,device,verify=True)
    if executable is None:raise RuntimeError('Install the selected NVIDIA runtime from Installation')
    record=model_record(root);verify_model(record.get('path',''));hardware=probe(root,device)
    if device=='cuda' and not hardware['cudaAvailable']:raise RuntimeError('Selected CUDA runtime has no compatible NVIDIA GPU/driver; choose CPU or check Installation diagnostics')
    with wave.open(str(audio),'rb') as stream:
        if (stream.getframerate(),stream.getnchannels(),stream.getsampwidth())!=(16000,1,2):raise ValueError('Expected 16 kHz mono PCM16')
        duration=stream.getnframes()/16000
    if duration<=0 or duration>options['max_seconds']:raise ValueError('Audio exceeds the configured diarization duration limit or is empty')
    if options['nemotron_mode']=='full' and duration>360:raise ValueError('Full attention is limited to 360 seconds; select chunked for longer recordings')
    args=['diarize',str(audio),'--model',record['path'],'--device','cuda:0' if device=='cuda' else 'cpu','--format','json','--output',str(scratch),'--concurrency','1','--no-batching']
    if options['nemotron_mode']=='full':args+=['--offline']
    elif options['nemotron_preset']=='custom':
        for key in GEOMETRY:args+=['--diar.'+key,str(options['nemotron_'+key])]
    else:args+=['--preset',options['nemotron_preset']]
    for key in SEGMENTATION:args+=['--'+key.replace('_','-'),str(options['nemotron_'+key])]
    cpu_limit=limit_cpu(options['threads'])
    try:
        result=command(executable,args,root,7200)
        if result.stderr:sys.stderr.write(result.stderr)
        if result.returncode:raise RuntimeError('NVIDIA diarization failed: '+result.stderr[-4000:])
        path=Path(scratch)
        if not path.is_file() or path.stat().st_size>64*1024**2:raise ValueError('Missing or oversized NVIDIA result')
        speakers,segments,exclusive=normalize_segments(json.loads(path.read_text('utf-8')),duration)
        return {'engine':'nemotron3','model':MODEL,'revision':CATALOG['model']['revision'],'runtimeVersion':CATALOG['runtimeVersion'],'quantization':'Q8_0','device':'cuda:0' if device=='cuda' else 'cpu','cpuLimit':cpu_limit,'durationSeconds':duration,'parameters':options,'speakers':speakers,'segments':segments,'exclusiveSegments':exclusive,'exclusivePolicy':'previous-active-then-earliest'}
    finally:Path(scratch).unlink(missing_ok=True)
