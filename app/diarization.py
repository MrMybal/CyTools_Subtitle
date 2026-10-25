"""Optional local Community-1 integration. No ML imports at module import time."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

MODEL="pyannote/speaker-diarization-community-1"
REVISION="3533c8cf8e369892e6b79ff1bf80f7b0286a54ee"
MODEL_URL="https://huggingface.co/"+MODEL
FILES=("config.yaml","embedding/pytorch_model.bin","segmentation/pytorch_model.bin","plda/plda.npz","plda/xvec_transform.npz")
CREDENTIAL="CyTools_Subtitle:pyannote-huggingface"


def credential():
    if sys.platform=="win32":
        try:
            import win32cred
            blob=win32cred.CredRead(CREDENTIAL,win32cred.CRED_TYPE_GENERIC)["CredentialBlob"]
            token=blob.decode("utf-8") if isinstance(blob,bytes) else blob
            if token:return token
        except Exception:pass
    from huggingface_hub import get_token
    return get_token()


def save_credential(token):
    if not isinstance(token,str) or not token.strip():raise ValueError("Enter a Hugging Face access token")
    if sys.platform!="win32":raise ValueError("Use HF_TOKEN or the Hugging Face CLI login on this platform")
    import win32cred
    win32cred.CredWrite({"Type":win32cred.CRED_TYPE_GENERIC,"TargetName":CREDENTIAL,"UserName":"huggingface","CredentialBlob":token.strip().encode("utf-8"),"Persist":win32cred.CRED_PERSIST_LOCAL_MACHINE},0)
    return {"credentialSaved":True}


def active_runtime(root):
    base=(Path(root)/"runtime/components/diarization").resolve()
    try:
        marker=json.loads((base/"active.json").read_text("utf-8"))
        if not isinstance(marker,dict):return None
        target=(base/marker["directory"]).resolve()
        lock=Path(root)/"app/diarization-runtime-lock.json"
        if marker.get("schemaVersion")!=1 or not target.is_relative_to(base) or marker.get("lockSha256")!=hashlib.sha256(lock.read_bytes()).hexdigest() or not (target/"pyannote/audio/__init__.py").is_file():return None
        return target
    except (OSError,ValueError,TypeError,KeyError):return None


def activate(root):
    target=active_runtime(root)
    if target is None:raise RuntimeError("Install the optional diarization runtime from Installation")
    sys.path.insert(0,str(target))
    os.environ["PYANNOTE_METRICS_ENABLED"]="0"
    os.environ["HF_HUB_OFFLINE"]="1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"]="1"
    return target


def model_record(root):
    try:
        value=json.loads((Path(root)/"data/settings/diarization.json").read_text("utf-8"))
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):return {}


def status(root):
    runtime=active_runtime(root);record=model_record(root);path=Path(record.get("path","") if isinstance(record.get("path",""),str) else "")
    ready=bool(isinstance(record.get("path"),str) and record.get("path") and all((path/name).is_file() for name in FILES) and (record.get("files") or (path/"cytools-model.json").is_file()))
    return {"model":MODEL,"revision":record.get("revision",REVISION),"runtimeReady":runtime is not None,"modelReady":ready,"ready":runtime is not None and ready,"runtimePath":str(runtime or ""),"modelPath":str(path) if record.get("path") else "","state":"Installed" if runtime is not None and ready else "Missing","credentialAvailable":bool(credential()),"source":MODEL_URL,"license":"CC-BY-4.0","device":"cpu"}


def hash_file(path,cancellation=None):
    digest=hashlib.sha256()
    with Path(path).open("rb") as f:
        while chunk:=f.read(1024**2):
            if cancellation:cancellation.check()
            digest.update(chunk)
    return digest.hexdigest()


def verify_model(path,cancellation=None,metadata=None):
    import yaml
    path=Path(path).resolve();config=yaml.safe_load((path/"config.yaml").read_text("utf-8"))
    if config.get("pipeline",{}).get("name")!="pyannote.audio.pipelines.SpeakerDiarization":raise ValueError("Expected the Community-1 SpeakerDiarization pipeline")
    if config.get("device") not in (None,"cpu"):raise ValueError("This Tool supports CPU diarization only")
    if config.get("preprocessors"):raise ValueError("Custom pipeline preprocessors are not supported")
    params=config.get('pipeline',{}).get('params',{})
    for key in ('embedding','segmentation','plda'):
        value=params.get(key)
        if value is not None and value!='$model/'+key:raise ValueError('Community-1 assets must be contained in the model directory')
    def inspect(value):
        if isinstance(value,dict):
            for item in value.values():inspect(item)
        elif isinstance(value,list):
            for item in value:inspect(item)
        elif isinstance(value,str) and value.startswith("$model/"):
            resolved=(path/value[len("$model/"):]).resolve()
            if not resolved.is_relative_to(path):raise ValueError("Model path escapes its directory")
    inspect(config)
    manifest=metadata if metadata is not None else json.loads((path/"cytools-model.json").read_text("utf-8"))
    if manifest.get("model")!=MODEL or not isinstance(manifest.get("files"),dict):raise ValueError("Missing Community-1 model provenance")
    official={}
    if manifest.get('revision')==REVISION:
        catalog=json.loads(Path(__file__).with_name('diarization-model-catalog.json').read_text('utf-8'))
        official={item['path']:item for item in catalog['files']}
    for name in FILES:
        target=(path/name).resolve()
        if not target.is_relative_to(path) or hash_file(target,cancellation)!=manifest["files"].get(name):raise ValueError("Diarization model checksum mismatch")
        if name in official:
            reference=official[name]
            if target.stat().st_size!=reference['size']:raise ValueError('Official model file size mismatch')
            if reference.get('sha256') and hash_file(target,cancellation)!=reference['sha256']:raise ValueError('Official model SHA256 mismatch')
            if not reference.get('sha256'):
                data=target.read_bytes()
                if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=reference['gitBlobSha1']:raise ValueError('Official model configuration mismatch')
    return {"path":str(path),"revision":manifest["revision"],"model":MODEL,"license":"CC-BY-4.0","files":manifest["files"]}


def access_problem(exc):
    status_code=exc.response.status_code if exc.response is not None else 0
    try:detail=str(exc.response.json().get('error','')).lower()
    except (AttributeError,ValueError):detail=''
    if status_code==401:return {'reason':'Authentication','message':'Configure a valid Hugging Face read token in Installation.'}
    if 'fine-grained' in detail or 'token permissions' in detail:
        return {'reason':'TokenPermissions','message':'Enable access to public gated repositories in your Hugging Face read token permissions, then retry.'}
    return {'reason':'Conditions','message':'Accept the Community-1 model conditions on Hugging Face, then retry with your read token.'}


def access():
    from huggingface_hub import hf_hub_download
    from huggingface_hub.errors import HfHubHTTPError
    try:
        hf_hub_download(MODEL,"config.yaml",revision=REVISION,token=credential())
        return {"state":"Accessible","source":MODEL_URL}
    except HfHubHTTPError as exc:
        if exc.response is not None and exc.response.status_code in (401,403):return {"state":"AccessRequired","source":MODEL_URL,**access_problem(exc)}
        raise RuntimeError("Could not contact Hugging Face to check model access") from None


def install_model(root,destination):
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import HfHubHTTPError
    root=Path(root).resolve();destination=Path(destination).resolve();base=(root/"data/models/diarization").resolve()
    if not destination.is_relative_to(base) or destination==base or destination.exists():raise ValueError("Expected a new private model directory")
    try:snapshot_download(MODEL,revision=REVISION,token=credential(),local_dir=str(destination),allow_patterns=list(FILES)+["README.md","*/README.md"])
    except HfHubHTTPError as exc:
        if exc.response is not None and exc.response.status_code in (401,403):raise PermissionError(access_problem(exc)["message"]) from None
        raise RuntimeError("Model download failed; retry from Installation") from None
    manifest={"model":MODEL,"revision":REVISION,"files":{name:hash_file(destination/name) for name in FILES}}
    (destination/"cytools-model.json").write_text(json.dumps(manifest,indent=2)+"\n","utf-8")
    return verify_model(destination)


def install_runtime(root,destination):
    import ssl
    import runtime_components
    root=Path(root).resolve();destination=Path(destination).resolve();base=(root/"runtime/components/diarization").resolve()
    if sys.platform!="win32" or sys.version_info[:2]!=(3,11):raise RuntimeError("Guided diarization installation supports Windows CPython 3.11 x64 only")
    if not destination.is_relative_to(base) or destination==base or destination.exists():raise ValueError("Expected a new private runtime directory")
    wheel=root/"app/packages"/runtime_components.PIP_WHEEL
    if hash_file(wheel)!=runtime_components.PIP_SHA256:raise RuntimeError("Bundled installer checksum mismatch")
    destination.mkdir(parents=True)
    certificates=destination/"system-ca.pem"
    certificates.write_text("".join(ssl.DER_cert_to_PEM_cert(cert) for cert in ssl.create_default_context().get_ca_certs(binary_form=True)),"ascii")
    args=["install","--isolated","--cert",str(certificates),"--keyring-provider","disabled","--disable-pip-version-check","--only-binary=:all:","--no-deps","--no-compile","--require-hashes","--target",str(destination),"-r",str(root/"app/requirements-diarization-windows.txt")]
    code="import sys;sys.path.insert(0,"+repr(str(wheel))+");from pip._internal.cli.main import main;raise SystemExit(main("+repr(args)+"))"
    flags=0x08000000 if os.name=="nt" else 0
    subprocess.run([sys.executable,"-c",code],stdout=sys.stderr,stderr=sys.stderr,check=True,creationflags=flags)
    for metadata in destination.glob("*.dist-info/direct_url.json"):metadata.unlink()
    probe="import sys,os;sys.path.insert(0,"+repr(str(destination))+");os.environ['PYANNOTE_METRICS_ENABLED']='0';import torch;assert torch.__version__=='2.8.0+cpu' and torch.version.cuda is None;from pyannote.audio import Pipeline;import importlib.metadata;assert importlib.metadata.version('pyannote.audio')=='4.0.7';print('CPU diarization runtime verified')"
    subprocess.run([sys.executable,"-c",probe],stdout=sys.stderr,stderr=sys.stderr,check=True,creationflags=flags)
    marker={"schemaVersion":1,"directory":destination.relative_to(base).as_posix(),"lockSha256":hash_file(root/"app/diarization-runtime-lock.json")}
    temporary=base/("active-"+uuid.uuid4().hex+".tmp");temporary.write_text(json.dumps(marker,indent=2)+"\n","utf-8");temporary.replace(base/"active.json")
    return status(root)


def infer(root,audio,options,scratch):
    activate(root)
    import numpy as np
    import torch
    import wave
    from pyannote.audio import Pipeline
    torch.set_num_threads(options["threads"])
    record=model_record(root);verify_model(record["path"],metadata=record if record.get("files") else None)
    with wave.open(str(audio),"rb") as f:
        if (f.getframerate(),f.getnchannels(),f.getsampwidth())!=(16000,1,2):raise ValueError("Expected 16 kHz mono PCM16")
        frames=f.getnframes();duration=frames/16000
        if duration>options["max_seconds"]:raise ValueError("Audio exceeds the configured diarization duration limit")
        if frames==0:raise ValueError("Audio is empty")
        # Disk-backed waveform, populated one minute at a time; no full-file
        # tensor copy. Pyannote's model windows and batch sizes remain bounded.
        waveform=np.memmap(str(scratch),mode="w+",dtype="float32",shape=(frames,))
        position=0
        while data:=f.readframes(16000*60):
            samples=np.frombuffer(data,dtype="<i2");waveform[position:position+len(samples)]=samples.astype(np.float32)/32768;position+=len(samples)
        waveform.flush()
    pipeline=Pipeline.from_pretrained(record["path"],token=False)
    pipeline.to(torch.device("cpu"));pipeline.segmentation_batch_size=options["segmentation_batch_size"];pipeline.embedding_batch_size=options["embedding_batch_size"]
    kwargs={k:options[k] for k in ("num_speakers","min_speakers","max_speakers") if options[k]}
    if kwargs.get("num_speakers"):kwargs={"num_speakers":kwargs["num_speakers"]}
    output=pipeline({"waveform":torch.from_numpy(waveform).unsqueeze(0),"sample_rate":16000},**kwargs)
    regular=[(float(turn.start),float(turn.end),str(label)) for turn,_,label in output.speaker_diarization.itertracks(yield_label=True)]
    exclusive=[(float(turn.start),float(turn.end),str(label)) for turn,_,label in output.exclusive_speaker_diarization.itertracks(yield_label=True)]
    labels=list(dict.fromkeys(label for start,end,label in sorted(regular+exclusive)))
    ids={label:f"speaker-{i+1}" for i,label in enumerate(labels)}
    def segments(turns):return [{"start":round(max(0,start),6),"end":round(min(duration,end),6),"speaker":ids[label]} for start,end,label in sorted(turns) if min(duration,end)>max(0,start)]
    return {"model":MODEL,"revision":record["revision"],"device":"cpu","durationSeconds":duration,"speakers":[{"id":ids[label],"name":f"Person {i+1}"} for i,label in enumerate(labels)],"segments":segments(regular),"exclusiveSegments":segments(exclusive)}
