"""CyTools_Subtitle runtime. No media, ML or UI imports at module import time."""
import json
import hashlib
import math
import os
from pathlib import Path
import sys
import uuid
import wave
from cytools_core import Runtime, load_manifest, CyToolError
from cytools_core.transports.cli import run_cli
from cytools_core.workers import ProcessWorker
import subtitles
import runtime_components
import diarization
import nemotron
import speakers

APP=Path(__file__).resolve().parent
ROOT=APP.parent
MODELS=ROOT/"data/settings/models.json"
MODEL_IDS=("phonon-2","phonon-2.5","phonon-2.5-en")
runtime_components.activate(ROOT)


def model_records():
    try: return json.loads(MODELS.read_text("utf-8"))
    except FileNotFoundError: return {}


def verify_model(path, cancellation=None):
    path=Path(path).resolve()
    metadata=json.loads((path/"packed_manifest.json").read_text("utf-8"))
    if metadata.get("format")!="fermion-five-value-parakeet-v1" or metadata.get("base_model")!="nvidia/parakeet-tdt-0.6b-v3":
        raise ValueError("Expected a compatible Phonon-2 family model")
    config=json.loads((path/"config.json").read_text("utf-8"))
    if config.get("model_type")!="parakeet" or config.get("sample_rate")!=16000:raise ValueError("Incompatible model configuration")
    hashes={}
    for name in ("model.fermion","config.json","packed_manifest.json"):
        digest=hashlib.sha256()
        with (path/name).open("rb") as stream:
            while block:=stream.read(1024**2):
                if cancellation:cancellation.check()
                digest.update(block)
        hashes[name]=digest.hexdigest()
    if hashes["model.fermion"]!=metadata.get("container_sha256"):
        raise ValueError("Model checksum mismatch: use Download / resume / repair model")
    return {"path":str(path),"sha256":hashes,"format":"fermion-five-value-parakeet-v1"}


def configure_environment():
    from cytools_core.shared_installation import InstallationStorage
    InstallationStorage(ROOT).apply_environment()
    os.environ["FERMION_CACHE_DIR"]=str(ROOT/"data/models")
    os.environ["FERMION_DEVICE"]="cpu"
    os.environ["PYTHONIOENCODING"]="utf-8"
    os.environ["PYTHONUTF8"]="1"


def create_runtime(data_dir, **options):
    configure_environment()
    runtime=Runtime(load_manifest(APP/"CyTool.json"),data_dir,**options)
    runtime.configure_inputs(ROOT/"data/inputs", fields={"transcribe":["media"],"inspect_media":["media"],"read_subtitles":["document"],"edit_subtitles":["document"],"reflow_subtitles":["document"],"repair_subtitles":["document"],"diarize_subtitles":["media","document"],"rename_speakers":["document"]})
    from cytools_core.shared_installation import register_operations
    register_operations(runtime,ROOT)

    def worker(ctx, p, timeout=600, script="worker.py"):
        unit=ProcessWorker([sys.executable,str(APP/script)],idle_timeout=timeout)
        runtime.register_worker(ctx.job_id+"-"+uuid.uuid4().hex,unit)
        try:
            response=unit.run(ctx,p)
            if not response["ok"]:
                message=response["error"]
                code="MissingDependency" if response.get("type")=="ModuleNotFoundError" else "InvalidTiming" if p.get("task")=="repair" else "BackendError"
                if response.get("type")=="PermissionError" or "401" in message or "403" in message: code="AccessRequired"
                if any(t in message.lower() for t in ("no space left", "disk full", "errno 28")): code="InsufficientDisk"
                raise CyToolError(code,message,recoverable=True)
            return response["result"]
        finally:
            unit.stop()
            # Keep only the current worker registered; stopped processes own no reservations.
            with runtime._cv:
                for key,value in list(runtime._workers.items()):
                    if value is unit: runtime._workers.pop(key,None)

    def source(ctx,p,key):
        return ctx.import_input(p[key],base_dir=ROOT/"data/inputs",suffixes=[".wav",".mp3",".m4a",".aac",".flac",".ogg",".opus",".aiff",".aif",".mp4",".mkv",".mov",".webm",".avi",".wmv",".m4v",".wma"] if key=="media" else [".json"],max_bytes=8*1024**3 if key=="media" else 64*1024**2)

    def document(ctx,p):
        path=source(ctx,p,"document")
        try: return subtitles.validate(json.loads(path.read_text("utf-8-sig")))
        except (ValueError,KeyError,TypeError) as exc: raise CyToolError("InvalidDocument",str(exc)) from exc

    def publish(ctx,doc):
        ctx.cancellation.check()
        result=subtitles.save(doc,ctx.path("outputs/subtitles.json").parent)
        ctx.progress(100,currentStep="Subtitles written")
        return result

    def inspect_media(ctx,p):
        path=source(ctx,p,"media")
        meta=worker(ctx,{"task":"probe","source":str(path)})
        if p["excerpt"]:
            dest=ctx.path("outputs/excerpt.wav")
            worker(ctx,{"task":"extract","source":str(path),"destination":str(dest),"start":p["start"],"duration":p["duration"],"audio_stream":p["audio_stream"]})
            peaks=[]
            import array
            with wave.open(str(dest),"rb") as audio:
                step=max(1,math.ceil(audio.getnframes()/600))
                while True:
                    ctx.cancellation.check()
                    data=audio.readframes(step)
                    if not data: break
                    values=array.array("h",data)
                    peaks.append(round(max(abs(v) for v in values)/32768,4))
                meta.update(excerpt=str(dest),excerptStartSeconds=p["start"],waveform=peaks)
        ctx.progress(100,currentStep="Media inspected")
        return meta

    def repair_options(p):
        return {key:p[key] for key in ("max_cps","min_duration","max_advance","max_delay","max_extension","min_gap","merge_fragments","max_chars","max_lines","max_duration","pause")}

    def apply_timing(ctx,doc,p,automatic=False):
        if automatic and not p["auto_timing"]:return doc
        ctx.progress(96,currentStep="Repairing subtitle timing")
        try:return worker(ctx,{"task":"repair","document":doc,"options":repair_options(p)},120)
        except CyToolError as exc:
            if not automatic or exc.code!="InvalidTiming":raise
            ctx.log(str(exc),level="Warning")
            doc["timingRepair"]={"state":"Unresolved","error":str(exc)}
            return doc

    def diarization_options(p):
        if p.get('diarization_engine')=='nemotron3':
            try:return nemotron.options(p)
            except ValueError as exc:raise CyToolError('InvalidParameters',str(exc)) from exc
        if not p['speaker_count'] and p['min_speakers']>p['max_speakers']:raise CyToolError('InvalidParameters','Minimum speakers must not exceed maximum speakers')
        return {'threads':p['threads'],'num_speakers':p['speaker_count'],'min_speakers':p['min_speakers'],'max_speakers':p['max_speakers'],'max_seconds':p['diarization_max_seconds'],'segmentation_batch_size':p['segmentation_batch_size'],'embedding_batch_size':p['embedding_batch_size']}

    def require_diarization(ctx,p):
        if p.get('diarization_engine')=='nemotron3':
            info=nemotron.status(ROOT);device=p['nemotron_device']
            if not info[device+'Ready']:raise CyToolError('MissingDependency','Install the selected NVIDIA runtime from Installation',recoverable=True)
            if not info['modelReady']:raise CyToolError('ModelNotInstalled','Install or register the NVIDIA GGUF from Installation',recoverable=True)
            try:nemotron.verify_model(info['modelPath'],ctx.cancellation)
            except (OSError,ValueError) as exc:raise CyToolError('InvalidModel',str(exc)) from exc
            return
        info=diarization.status(ROOT)
        if not info['runtimeReady']:raise CyToolError('MissingDependency','Install the optional diarization runtime from Installation',recoverable=True)
        if not info['modelReady']:raise CyToolError('ModelNotInstalled','Install or register Community-1 from Installation',recoverable=True)
        record=diarization.model_record(ROOT)
        try:diarization.verify_model(info['modelPath'],ctx.cancellation,metadata=record if record.get('files') else None)
        except (OSError,ValueError,KeyError) as exc:raise CyToolError('InvalidModel',str(exc),recoverable=True) from exc

    def analyze_speakers(ctx,audio,p,media_hash):
        if p.get('diarization_engine')=='nemotron3':
            ctx.progress(95,currentStep='Identifying speakers with NVIDIA Nemotron 3 ('+p['nemotron_device']+')')
            scratch=ctx.path('intermediates/nemotron.json')
            try:
                result=worker(ctx,{'task':'nemotron_infer','root':str(ROOT),'audio':str(audio),'scratch':str(scratch),'options':diarization_options(p)},7200,script='diarization_worker.py')
                result['mediaSha256']=media_hash
                return result
            finally:scratch.unlink(missing_ok=True)
        ctx.progress(95,currentStep='Identifying speakers with Community-1 (CPU)')
        scratch=ctx.path('intermediates/diarization.float32')
        try:
            result=worker(ctx,{'task':'infer','root':str(ROOT),'audio':str(audio),'scratch':str(scratch),'options':diarization_options(p)},7200,script='diarization_worker.py')
            result['mediaSha256']=media_hash;result['engine']='community1'
            return result
        finally:scratch.unlink(missing_ok=True)

    def transcribe(ctx,p):
        if p["diarization"]:diarization_options(p);require_diarization(ctx,p)
        path=source(ctx,p,"media")
        model_path=p["local_model"] or model_records().get(p["model"],{}).get("path","")
        if not model_path or not Path(model_path).is_dir():
            raise CyToolError("ModelNotInstalled","Use Installation > Download / repair, or install_model, before transcription",recoverable=True)
        if not runtime_components.status(ROOT)["ready"]:
            raise CyToolError("MissingDependency","Install PyTorch from Installation > Download / repair PyTorch before transcription",recoverable=True)
        try:verify_model(model_path,ctx.cancellation)
        except (OSError,ValueError) as exc:raise CyToolError("InvalidModel",str(exc),recoverable=True) from exc
        meta=worker(ctx,{"task":"probe","source":str(path)})
        duration=meta["durationSeconds"]
        if p.get('diarization_engine')=='nemotron3' and p['diarization'] and p['nemotron_mode']=='full' and duration>360:raise CyToolError('DurationLimit','Full attention is limited to 360 seconds; use chunked NVIDIA analysis')
        if p["diarization"] and duration>p["diarization_max_seconds"]:raise CyToolError("DurationLimit","Audio exceeds the configured diarization duration limit")
        if not 0<duration<=86400: raise CyToolError("InvalidMedia","Media duration must be known and between 0 and 24 hours")
        audio=ctx.path("intermediates/audio.wav")
        try:
            ctx.progress(3,currentStep="Extracting 16 kHz audio")
            worker(ctx,{"task":"extract","source":str(path),"destination":str(audio),"audio_stream":p["audio_stream"],"filter":p["filter"]},3600)
            words, chunks=[],[]
            with wave.open(str(audio),"rb") as full:
                duration=full.getnframes()/16000
                count=math.ceil(duration/p["chunk_seconds"])
                for index in range(count):
                    ctx.cancellation.check()
                    core=index*p["chunk_seconds"]
                    left=max(0,core-p["overlap_seconds"]/2)
                    right=min(duration,core+p["chunk_seconds"]+p["overlap_seconds"]/2)
                    clip=ctx.path("intermediates/chunk.wav")
                    full.setpos(round(left*16000))
                    with wave.open(str(clip),"wb") as target:
                        target.setparams((1,2,16000,0,"NONE","not compressed"))
                        target.writeframes(full.readframes(round((right-left)*16000)))
                    ctx.progress(5+90*index/count,currentStep=f"Transcribing window {index+1}/{count}",currentStepIndex=index+1,stepCount=count)
                    output=worker(ctx,{"task":"infer","model_path":model_path,"audio":str(clip),"threads":p["threads"],"hotwords":p["hotwords"],"hotword_lambda":p["hotword_lambda"]})
                    chunks.append({"start":left,"end":right,"engine":output.get("engine"),"backend":output.get("backend")})
                    for word in output.get("words") or []:
                        start=float(word["start"])+left
                        end=float(word["end"])+left
                        if not all(math.isfinite(t) for t in (start,end)) or end<start: raise CyToolError("InvalidTiming","Non-finite or reversed word timing from Phonon")
                        center=(start+end)/2
                        if not core<=center<min(duration,core+p["chunk_seconds"]): continue
                        text=word.get("text",word.get("word",""))
                        if text.strip(): words.append({"text":text,"start":round(max(left,start),3),"end":round(min(duration,max(end,start+.04)),3)})
            words.sort(key=lambda w:w["start"])
            # Ownership by word midpoint prevents overlap-window duplication; retain every accepted word.
            doc={"format":"cytools-subtitles","schemaVersion":1,"model":p["model"],"device":"cpu","media":meta,"words":words,"chunks":chunks,"parameters":{k:v for k,v in p.items() if k not in ("media","local_model")},"cues":subtitles.layout(words,**{k:p[k] for k in ("max_chars","max_lines","max_duration","pause")})}
            if p['diarization']:
                # Use unfiltered audio for voice identity; voice filtering can alter timbre.
                identity_audio=audio
                if p['filter']!='none':
                    identity_audio=ctx.path('intermediates/voices.wav')
                    worker(ctx,{'task':'extract','source':str(path),'destination':str(identity_audio),'audio_stream':p['audio_stream'],'filter':'none'},3600)
                analysis=analyze_speakers(ctx,identity_audio,p,diarization.hash_file(path,ctx.cancellation))
                doc=speakers.attach(doc,analysis,rebuild=True,layout_options={k:p[k] for k in ('max_chars','max_lines','max_duration','pause')})
                doc['speakerLabels']=p['speaker_labels']
                if identity_audio!=audio:identity_audio.unlink(missing_ok=True)
            doc=apply_timing(ctx,doc,p,automatic=True)
            result=publish(ctx,doc)
            return result
        finally:
            for name in ('audio.wav','chunk.wav','voices.wav','diarization.float32'):
                ctx.path('intermediates/'+name).unlink(missing_ok=True)

    def read_subtitles(ctx,p):
        doc=document(ctx,p)
        if p["end"]<=p["start"]:raise CyToolError("InvalidParameters","end must be greater than start")
        cues=[c for c in doc["cues"] if c["end"]>p["start"] and c["start"]<p["end"]]
        words=[w for w in doc.get("words",[]) if w["end"]>p["start"] and w["start"]<p["end"]]
        ctx.progress(100,currentStep="Read")
        return {"cues":cues[p["offset"]:p["offset"]+p["limit"]],"total":len(cues),"words":words[p["offset"]:p["offset"]+p["limit"]],"totalWords":len(words),"warnings":subtitles.quality(doc),"speakers":doc.get("speakers",[]),"speakerLabels":doc.get("speakerLabels",True)}

    def edit_subtitles(ctx,p):
        try: return publish(ctx,subtitles.edit(document(ctx,p),p["edits"],p["offset_seconds"]))
        except (ValueError,KeyError,TypeError) as exc: raise CyToolError("InvalidEdit",str(exc)) from exc

    def reflow_subtitles(ctx,p):
        doc=document(ctx,p)
        if not doc.get("words"): raise CyToolError("MissingWordTimings","Document has no original word timestamps")
        sounds=[c for c in doc["cues"] if c.get("kind")=="sound"]
        speech=subtitles.layout(speakers.attributed_words(doc) if doc.get("diarization") else doc["words"],**{k:p[k] for k in ("max_chars","max_lines","max_duration","pause")})
        # Avoid collisions with IDs selected by clients for added sound captions.
        sound_ids={c["id"] for c in sounds}
        for cue in speech:
            while cue["id"] in sound_ids: cue["id"]="reflow-"+cue["id"]
        doc["cues"]=speech+sounds
        if doc.get("diarization"):speakers.label_cues(doc)
        doc.pop("timingRepair",None);doc.pop("timingPolicy",None);doc.pop("timingAnchors",None)
        return publish(ctx,apply_timing(ctx,doc,p,automatic=True))

    def repair_subtitles(ctx,p):
        return publish(ctx,apply_timing(ctx,document(ctx,p),p))

    def status(ctx,p):
        import importlib.metadata
        records=model_records()
        ctx.progress(100,currentStep="Checked")
        models=[]
        for key,record in {**{key:{} for key in MODEL_IDS},**records}.items():
            try:
                verified=verify_model(record["path"],ctx.cancellation)
                models.append({"id":key,"installed":True,**record,**verified})
            except (OSError,ValueError,KeyError) as exc:models.append({"id":key,"installed":False,"reason":str(exc),**record})
        return {"device":"cpu","models":models,"fermionVersion":importlib.metadata.version("fermion-research"),"loraSupported":False}

    def install(ctx,p):
        if not p["license_accepted"]: raise CyToolError("LicenseAcceptanceRequired","Review CC-BY-4.0 at https://huggingface.co/FermionResearch/Phonon-2 and explicitly accept",recoverable=True)
        ctx.progress(5,currentStep="Downloading and verifying model")
        from filelock import FileLock, Timeout
        lock=FileLock(str(ROOT/"data/settings/model-install.lock"))
        MODELS.parent.mkdir(parents=True,exist_ok=True)
        while True:
            ctx.cancellation.check()
            try:lock.acquire(timeout=0);break
            except Timeout:ctx.cancellation.sleep(.1)
        try:
            existing=model_records().get(p["model"],{}).get("path","")
            if existing and Path(existing).is_dir():
                try:verify_model(existing,ctx.cancellation)
                except (OSError,ValueError):
                    old=Path(existing).resolve()
                    if not old.is_relative_to((ROOT/"data/models").resolve()):raise CyToolError("InvalidModel","External model is invalid; repair it at its source")
                    old.rename(old.with_name(old.name+".invalid-"+uuid.uuid4().hex[:8]))
                    ctx.log("Preserved damaged model in a neighbouring .invalid folder")
            value=worker(ctx,{"task":"install","model":p["model"]},3600)
        finally:lock.release()
        records=model_records()
        records[p["model"]]={**verify_model(value["path"],ctx.cancellation),"verifiedBy":"fermion-research 0.2.14 --download-only and SHA256","license":"CC-BY-4.0"}
        MODELS.parent.mkdir(parents=True,exist_ok=True)
        temp=MODELS.with_suffix(".tmp")
        temp.write_text(json.dumps(records,indent=2),"utf-8"); temp.replace(MODELS)
        ctx.progress(100,currentStep="Model verified")
        return records[p["model"]]

    def register_local(ctx,p):
        try:record=verify_model(p["path"],ctx.cancellation)
        except (OSError,ValueError) as exc:raise CyToolError("InvalidModel",str(exc)) from exc
        record.update(name=p["name"],model=p["model"],license=p["license"],source=p["source"])
        records=model_records();identifier="local-"+hashlib.sha256(record["path"].encode()).hexdigest()[:16]
        records[identifier]=record
        MODELS.parent.mkdir(parents=True,exist_ok=True)
        temp=MODELS.with_suffix(".tmp");temp.write_text(json.dumps(records,indent=2),"utf-8");temp.replace(MODELS)
        ctx.progress(100,currentStep="Local model registered")
        return {"id":identifier,**record}

    def runtime_status(ctx,p):
        result=runtime_components.status(ROOT)
        ctx.progress(100,currentStep="Checked")
        return result

    def install_runtime(ctx,p):
        if not p["license_accepted"]:
            raise CyToolError("LicenseAcceptanceRequired","Review the PyTorch BSD-3-Clause license before installing",recoverable=True)
        if sys.platform!="win32":raise CyToolError("UnsupportedPlatform","Guided PyTorch installation currently supports Windows only",recoverable=True)
        if runtime_components.status(ROOT)["ready"] and not p["repair"]:return runtime_components.status(ROOT)
        from filelock import FileLock,Timeout
        base=ROOT/"runtime/components/pytorch";base.mkdir(parents=True,exist_ok=True)
        lock=FileLock(str(base/"install.lock"))
        while True:
            ctx.cancellation.check()
            try:lock.acquire(timeout=0);break
            except Timeout:ctx.cancellation.sleep(.1)
        try:
            ctx.progress(5,currentStep="Downloading and verifying PyTorch")
            candidate=base/(runtime_components.PACKAGES["torch"]+"-"+uuid.uuid4().hex)
            value=worker(ctx,{"task":"install_runtime","root":str(ROOT),"destination":str(candidate)},1800)
            ctx.progress(100,currentStep="PyTorch ready")
            return value
        finally:lock.release()

    def diarization_status(ctx,p):
        return diarization.status(ROOT)

    def check_diarization_access(ctx,p):
        return worker(ctx,{'task':'access'},60,script='diarization_worker.py')

    def install_diarization(ctx,p,kind):
        if not p['license_accepted']:raise CyToolError('LicenseAcceptanceRequired','Review the Community-1 conditions and component licenses in Installation',recoverable=True)
        if kind=='runtime' and sys.platform!='win32':raise CyToolError('UnsupportedPlatform','Guided diarization runtime installation currently supports Windows only')
        info=diarization.status(ROOT)
        if info[kind+'Ready'] and not p['repair']:return info
        from filelock import FileLock,Timeout
        base=ROOT/('runtime/components/diarization' if kind=='runtime' else 'data/models/diarization');base.mkdir(parents=True,exist_ok=True)
        lock=FileLock(str(base/'install.lock'))
        while True:
            ctx.cancellation.check()
            try:lock.acquire(timeout=0);break
            except Timeout:ctx.cancellation.sleep(.1)
        try:
            ctx.progress(5,currentStep='Installing optional speaker '+kind)
            value=worker(ctx,{'task':'install_'+kind,'root':str(ROOT),'destination':str(base/uuid.uuid4().hex)},3600,script='diarization_worker.py')
            if kind=='model':
                registry=ROOT/'data/settings/diarization.json';registry.parent.mkdir(parents=True,exist_ok=True)
                tmp=registry.with_suffix('.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(value,indent=2),'utf-8');tmp.replace(registry)
            ctx.progress(100,currentStep='Speaker '+kind+' ready')
            return diarization.status(ROOT)
        finally:lock.release()

    def install_diarization_runtime(ctx,p):return install_diarization(ctx,p,'runtime')
    def install_diarization_model(ctx,p):return install_diarization(ctx,p,'model')

    def register_diarization_model(ctx,p):
        try:
            directory=Path(p['path']).resolve()
            manifest={'model':diarization.MODEL,'revision':'local','files':{name:diarization.hash_file(directory/name,ctx.cancellation) for name in diarization.FILES}}
            value=diarization.verify_model(directory,ctx.cancellation,metadata=manifest)
        except (OSError,ValueError,KeyError) as exc:raise CyToolError('InvalidModel',str(exc)) from exc
        registry=ROOT/'data/settings/diarization.json';registry.parent.mkdir(parents=True,exist_ok=True)
        tmp=registry.with_suffix('.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(value,indent=2),'utf-8');tmp.replace(registry)
        return diarization.status(ROOT)

    def diarize_subtitles(ctx,p):
        options=diarization_options(p);require_diarization(ctx,p)
        doc=document(ctx,p);path=source(ctx,p,'media');meta=worker(ctx,{'task':'probe','source':str(path)})
        if p.get('diarization_engine')=='nemotron3' and p['nemotron_mode']=='full' and meta['durationSeconds']>360:raise CyToolError('DurationLimit','Full attention is limited to 360 seconds; use chunked NVIDIA analysis')
        if meta['durationSeconds']>options['max_seconds']:raise CyToolError('DurationLimit','Audio exceeds the configured diarization duration limit')
        original_duration=doc.get('media',{}).get('durationSeconds')
        if original_duration and abs(original_duration-meta['durationSeconds'])>1:raise CyToolError('MediaMismatch','Selected media duration does not match this subtitle document')
        source_hash=diarization.hash_file(path,ctx.cancellation)
        previous_hash=doc.get('diarization',{}).get('mediaSha256')
        if previous_hash and previous_hash!=source_hash:raise CyToolError('MediaMismatch','Selected media is different from the previously analyzed recording')
        audio=ctx.path('intermediates/voices.wav')
        try:
            worker(ctx,{'task':'extract','source':str(path),'destination':str(audio),'audio_stream':p['audio_stream'],'filter':'none'},3600)
            analysis=analyze_speakers(ctx,audio,p,source_hash)
            try:doc=speakers.attach(doc,analysis,rebuild=p['rebuild'],layout_options={k:p[k] for k in ('max_chars','max_lines','max_duration','pause')},replace_manual=p['replace_manual'])
            except ValueError as exc:raise CyToolError('InvalidSpeakerAnalysis',str(exc),recoverable=True) from exc
            doc['speakerLabels']=p['speaker_labels']
            return publish(ctx,doc)
        finally:audio.unlink(missing_ok=True)

    def nemotron_status(ctx,p):return nemotron.status(ROOT)

    def nemotron_diagnostics(ctx,p):return worker(ctx,{'task':'nemotron_probe','root':str(ROOT),'backend':p['backend']},30,script='diarization_worker.py')

    def install_nvidia(ctx,p,kind):
        if not p['license_accepted']:raise CyToolError('LicenseAcceptanceRequired','Review the NVIDIA model/runtime license in Installation and explicitly accept it',recoverable=True)
        info=nemotron.status(ROOT);backend=p.get('backend','cpu')
        if not p['repair'] and info[backend+'Ready' if kind=='runtime' else 'modelReady']:return info
        from filelock import FileLock,Timeout
        base=ROOT/('runtime/components/nemotron/'+backend if kind=='runtime' else 'data/models/nemotron');base.mkdir(parents=True,exist_ok=True)
        lock=FileLock(str(base/'install.lock'))
        while True:
            ctx.cancellation.check()
            try:lock.acquire(timeout=0);break
            except Timeout:ctx.cancellation.sleep(.1)
        try:
            return worker(ctx,{'task':'nemotron_'+kind,'root':str(ROOT),'backend':backend,'license_accepted':p['license_accepted']},1800,script='diarization_worker.py')
        finally:lock.release()

    def install_nemotron_runtime(ctx,p):return install_nvidia(ctx,p,'runtime')
    def install_nemotron_model(ctx,p):return install_nvidia(ctx,p,'model')

    def register_nemotron_model(ctx,p):
        try:value=nemotron.verify_model(p['path'],ctx.cancellation)
        except (OSError,ValueError) as exc:raise CyToolError('InvalidModel',str(exc)) from exc
        nemotron.atomic(ROOT/'data/settings/nemotron.json',value)
        return nemotron.status(ROOT)

    def rename_speakers(ctx,p):
        try:return publish(ctx,speakers.rename(document(ctx,p),p['names'],p['show_labels']))
        except (ValueError,KeyError,TypeError) as exc:raise CyToolError('InvalidEdit',str(exc)) from exc

    def estimate(p,backend,model):
        # Conservative 4 GiB CPU model envelope, plus input copies and up to 24h PCM.
        size=0
        if p.get("media"):
            candidate=Path(p["media"])
            if not candidate.is_absolute(): candidate=ROOT/"data/inputs"/candidate
            try: size=candidate.stat().st_size
            except OSError: pass
        result={"ramBytes":(6 if p.get("diarization") else 4)*1024**3,"diskBytes":size*2+(5 if p.get("diarization") else 3)*1024**3,"cpuThreads":p.get("threads",4)}
        if p.get('diarization') and p.get('diarization_engine')=='nemotron3' and p.get('nemotron_device')=='cuda':result['vramBytes']={'0':(6 if p.get('nemotron_mode')=='full' or p.get('nemotron_preset')=='custom' else 2)*1024**3}
        return result

    def estimate_diarization(p,backend,model):
        resources=estimate(p,backend,model)
        resources['ramBytes']=6*1024**3;resources['diskBytes']+=2*1024**3
        if p.get('diarization_engine')=='nemotron3' and p.get('nemotron_device')=='cuda':resources['vramBytes']={'0':(6 if p.get('nemotron_mode')=='full' or p.get('nemotron_preset')=='custom' else 2)*1024**3}
        return resources

    def estimate_input(p,backend,model):
        candidate=Path(p.get("media",p.get("document","")))
        if not candidate.is_absolute(): candidate=ROOT/"data/inputs"/candidate
        try:size=candidate.stat().st_size
        except OSError:size=0
        return {"ramBytes":512*1024**2,"diskBytes":size*2+128*1024**2,"cpuThreads":1}

    for name,handler in (("transcribe",transcribe),("inspect_media",inspect_media),("read_subtitles",read_subtitles),("edit_subtitles",edit_subtitles),("reflow_subtitles",reflow_subtitles),("repair_subtitles",repair_subtitles),("model_status",status),("install_model",install),("register_local_model",register_local),("runtime_status",runtime_status),("install_runtime",install_runtime),("diarization_status",diarization_status),("check_diarization_access",check_diarization_access),("install_diarization_runtime",install_diarization_runtime),("install_diarization_model",install_diarization_model),("register_diarization_model",register_diarization_model),("diarize_subtitles",diarize_subtitles),("rename_speakers",rename_speakers),("nemotron_status",nemotron_status),("nemotron_diagnostics",nemotron_diagnostics),("install_nemotron_runtime",install_nemotron_runtime),("install_nemotron_model",install_nemotron_model),("register_nemotron_model",register_nemotron_model)):
        runtime.register(name,handler,**({"estimate":estimate_diarization} if name=="diarize_subtitles" else {"estimate":estimate} if name=="transcribe" else {"estimate":estimate_input} if name in ("inspect_media","read_subtitles","edit_subtitles","reflow_subtitles","repair_subtitles","rename_speakers") else {}))
    return runtime


if __name__=="__main__": raise SystemExit(run_cli(create_runtime))
