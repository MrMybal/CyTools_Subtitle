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

APP=Path(__file__).resolve().parent
ROOT=APP.parent
MODELS=ROOT/"data/settings/models.json"
MODEL_IDS=("phonon-2","phonon-2.5","phonon-2.5-en")


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
    runtime.configure_inputs(ROOT/"data/inputs", fields={"transcribe":["media"],"inspect_media":["media"],"read_subtitles":["document"],"edit_subtitles":["document"],"reflow_subtitles":["document"],"repair_subtitles":["document"]})
    from cytools_core.shared_installation import register_operations
    register_operations(runtime,ROOT)

    def worker(ctx, p, timeout=600):
        unit=ProcessWorker([sys.executable,str(APP/"worker.py")],idle_timeout=timeout)
        runtime.register_worker(ctx.job_id+"-"+uuid.uuid4().hex,unit)
        try:
            response=unit.run(ctx,p)
            if not response["ok"]:
                message=response["error"]
                code="MissingDependency" if response.get("type")=="ModuleNotFoundError" else "InvalidTiming" if p.get("task")=="repair" else "BackendError"
                if "401" in message or "403" in message: code="AccessRequired"
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

    def transcribe(ctx,p):
        path=source(ctx,p,"media")
        model_path=p["local_model"] or model_records().get(p["model"],{}).get("path","")
        if not model_path or not Path(model_path).is_dir():
            raise CyToolError("ModelNotInstalled","Use Installation > Download / repair, or install_model, before transcription",recoverable=True)
        try:verify_model(model_path,ctx.cancellation)
        except (OSError,ValueError) as exc:raise CyToolError("InvalidModel",str(exc),recoverable=True) from exc
        meta=worker(ctx,{"task":"probe","source":str(path)})
        duration=meta["durationSeconds"]
        if not 0<duration<=86400: raise CyToolError("InvalidMedia","Media duration must be known and between 0 and 24 hours")
        audio=ctx.path("intermediates/audio.wav")
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
        doc=apply_timing(ctx,doc,p,automatic=True)
        result=publish(ctx,doc)
        # Audio intermediates are not user outputs and must not grow on retained desktop jobs.
        audio.unlink(missing_ok=True)
        ctx.path("intermediates/chunk.wav").unlink(missing_ok=True)
        return result

    def read_subtitles(ctx,p):
        doc=document(ctx,p)
        if p["end"]<=p["start"]:raise CyToolError("InvalidParameters","end must be greater than start")
        cues=[c for c in doc["cues"] if c["end"]>p["start"] and c["start"]<p["end"]]
        words=[w for w in doc.get("words",[]) if w["end"]>p["start"] and w["start"]<p["end"]]
        ctx.progress(100,currentStep="Read")
        return {"cues":cues[p["offset"]:p["offset"]+p["limit"]],"total":len(cues),"words":words[p["offset"]:p["offset"]+p["limit"]],"totalWords":len(words),"warnings":subtitles.quality(doc)}

    def edit_subtitles(ctx,p):
        try: return publish(ctx,subtitles.edit(document(ctx,p),p["edits"],p["offset_seconds"]))
        except (ValueError,KeyError,TypeError) as exc: raise CyToolError("InvalidEdit",str(exc)) from exc

    def reflow_subtitles(ctx,p):
        doc=document(ctx,p)
        if not doc.get("words"): raise CyToolError("MissingWordTimings","Document has no original word timestamps")
        sounds=[c for c in doc["cues"] if c.get("kind")=="sound"]
        speech=subtitles.layout(doc["words"],**{k:p[k] for k in ("max_chars","max_lines","max_duration","pause")})
        # Avoid collisions with IDs selected by clients for added sound captions.
        sound_ids={c["id"] for c in sounds}
        for cue in speech:
            while cue["id"] in sound_ids: cue["id"]="reflow-"+cue["id"]
        doc["cues"]=speech+sounds
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

    def estimate(p,backend,model):
        # Conservative 4 GiB CPU model envelope, plus input copies and up to 24h PCM.
        size=0
        if p.get("media"):
            candidate=Path(p["media"])
            if not candidate.is_absolute(): candidate=ROOT/"data/inputs"/candidate
            try: size=candidate.stat().st_size
            except OSError: pass
        return {"ramBytes":4*1024**3,"diskBytes":size*2+3*1024**3,"cpuThreads":p.get("threads",4)}

    def estimate_input(p,backend,model):
        candidate=Path(p.get("media",p.get("document","")))
        if not candidate.is_absolute(): candidate=ROOT/"data/inputs"/candidate
        try:size=candidate.stat().st_size
        except OSError:size=0
        return {"ramBytes":512*1024**2,"diskBytes":size*2+128*1024**2,"cpuThreads":1}

    for name,handler in (("transcribe",transcribe),("inspect_media",inspect_media),("read_subtitles",read_subtitles),("edit_subtitles",edit_subtitles),("reflow_subtitles",reflow_subtitles),("repair_subtitles",repair_subtitles),("model_status",status),("install_model",install),("register_local_model",register_local)):
        runtime.register(name,handler,**({"estimate":estimate} if name=="transcribe" else {"estimate":estimate_input} if name in ("inspect_media","read_subtitles","edit_subtitles","reflow_subtitles","repair_subtitles") else {}))
    return runtime


if __name__=="__main__": raise SystemExit(run_cli(create_runtime))
