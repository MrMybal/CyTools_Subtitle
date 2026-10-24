import asyncio
import copy
import json
import os
from pathlib import Path
import sys
import threading
import time
import wave
import zipfile

import pytest
from cytools_core import CyToolError, validate_parameters
import tool
import subtitles
import updates


@pytest.fixture
def configured(tmp_path,monkeypatch):
    monkeypatch.setattr(tool,"ROOT",tmp_path)
    monkeypatch.setattr(tool,"MODELS",tmp_path/"data/settings/models.json")
    return tmp_path


def actor(runtime): return runtime.authenticate(runtime.create_client("Test")["token"])
def run(runtime,a,s,operation,parameters):
    return runtime.wait(a,runtime.submit(a,s,operation,parameters)["jobId"],timeout=30)
def doc(): return {"format":"cytools-subtitles","schemaVersion":1,"words":[{"text":"Hello.","start":.2,"end":1.}],"cues":[{"id":"one","start":.2,"end":1.,"text":"Hello.","kind":"speech"}]}
def write_doc(path): path.write_text(json.dumps(doc()),"utf-8");return str(path)


def test_layout_timing_and_exports(tmp_path):
    words=[{"text":text,"start":i*.5,"end":i*.5+.4} for i,text in enumerate(["Hello,","this","is","a","caption.","Second","sentence."])]
    cues=subtitles.layout(words,max_chars=15,max_lines=2,max_duration=2)
    assert " ".join(c["text"].replace("\n"," ") for c in cues)==" ".join(w["text"] for w in words)
    assert all(c["end"]-c["start"]<=2 for c in cues)
    document=doc();document["cues"]=cues
    out=subtitles.save(document,tmp_path)
    assert Path(out["vtt"]).read_text().startswith("WEBVTT\n\n")
    assert "00:00:00,000 -->" in Path(out["srt"]).read_text()
    assert subtitles.timestamp(3599.9996)=="01:00:00,000"


def test_patch_sound_offset_invalid_preserves_original():
    original=doc()
    changed=subtitles.edit(original,[{"id":"sound","start":1.,"end":2.,"text":"[door closes]","kind":"sound"}],.1)
    assert len(changed["cues"])==2 and changed["cues"][1]["start"]==1.1
    assert original==doc()
    with pytest.raises(ValueError):subtitles.edit(original,[], -5)
    with pytest.raises(ValueError):subtitles.edit(original,[{"id":"unknown","delete":True}])
    for bad in (float("nan"),float("inf"),True):
        invalid=doc();invalid["cues"][0]["end"]=bad
        with pytest.raises(ValueError):subtitles.validate(invalid)


def test_private_inputs_export_finish_and_all_document_fields(configured,tmp_path):
    path=write_doc(tmp_path/"outside Tool Ã©.json")
    with tool.create_runtime(tmp_path/"jobs") as r:
        a=actor(r);b=actor(r);s=r.create_session(a)["sessionId"]
        result=run(r,a,s,"edit_subtitles",{"document":path,"edits":[{"id":"one","text":"Bonjour."},{"id":"sound","start":1.2,"end":2.,"text":"[music]","kind":"sound"}]})
        assert result["state"]=="Completed",result
        output=Path(result["outputs"]["document"])
        assert output.is_relative_to(Path(result["workspace"]))
        assert r.list_jobs(b)==[]
        with pytest.raises(CyToolError):r.get_job(b,result["jobId"])
        with pytest.raises(CyToolError):r.submit(b,r.create_session(b)["sessionId"],"read_subtitles",{"document":str(output)})
        read=run(r,a,s,"read_subtitles",{"document":str(output),"start":1.,"limit":1})
        assert read["state"]=="Completed" and read["outputs"]["total"]==1
        reflow=run(r,a,s,"reflow_subtitles",{"document":str(output),"max_chars":10})
        assert reflow["state"]=="Completed"
        assert len(json.loads(Path(reflow["outputs"]["document"]).read_text())["cues"])==2
        exported=r.export_job(a,result["jobId"],str(tmp_path/"saved"))
        saved=Path(exported["outputs"]["srt"])
        assert saved.exists()
        r.finish_task(a,s)
        assert not output.exists() and saved.exists() and Path(path).exists()
        assert not list((tmp_path/"data/inputs").rglob("*.json"))


def test_bad_schema_model_and_media(configured,tmp_path):
    with tool.create_runtime(tmp_path/"jobs") as r:
        a=actor(r);s=r.create_session(a)["sessionId"]
        with pytest.raises(CyToolError):r.submit(a,s,"transcribe",{"media":"x","chunk_seconds":100})
        with pytest.raises(CyToolError):r.submit(a,s,"transcribe",{"media":"x","clientId":"forged"})
        with pytest.raises(CyToolError):r.submit(a,s,"install_model",{"license_accepted":True})
        path=tmp_path/"bad.wav";path.write_text("not audio")
        missing=run(r,a,s,"transcribe",{"media":str(path)})
        assert missing["error"]["code"]=="ModelNotInstalled"
        bad=run(r,a,s,"inspect_media",{"media":str(path)})
        assert bad["state"]=="Failed" and bad["error"]["code"]=="BackendError"
        invalid=tmp_path/"invalid.json";invalid.write_text("{}")
        job=run(r,a,s,"read_subtitles",{"document":str(invalid)})
        assert job["error"]["code"]=="InvalidDocument"


def test_real_audio_import_inspection(configured,tmp_path):
    source=tmp_path/"original outside Tool Ã©.wav"
    with wave.open(str(source),"wb") as w:w.setparams((1,2,16000,0,"NONE","not compressed"));w.writeframes(bytes(32000))
    with tool.create_runtime(tmp_path/"jobs") as r:
        a=actor(r);s=r.create_session(a,temporary=False)["sessionId"]
        j=run(r,a,s,"inspect_media",{"media":str(source),"duration":.4})
        assert j["state"]=="Completed",j
        assert j["outputs"]["durationSeconds"]==pytest.approx(1)
        assert len(j["outputs"]["waveform"])<=650
        assert Path(j["outputs"]["excerpt"]).is_relative_to(Path(j["workspace"]))
        with wave.open(j["outputs"]["excerpt"]) as w: assert w.getnframes()==6400
        r.close_session(a,s)
        assert Path(j["outputs"]["excerpt"]).exists() and source.exists()


def test_cancelled_worker_reservation_and_independent_job(configured,tmp_path):
    from cytools_core.workers import ProcessWorker
    started=threading.Event();stopped=threading.Event()
    with tool.create_runtime(tmp_path/"jobs") as r:
        a=actor(r);b=actor(r);s=r.create_session(a)["sessionId"];s2=r.create_session(b)["sessionId"]
        script=tmp_path/"slow.py";script.write_text('import time;time.sleep(60)')
        unit=ProcessWorker([sys.executable,str(script)],idle_timeout=120)
        def slow(ctx,p):
            r.register_worker("slow",unit);started.set()
            try:unit.run(ctx,{})
            finally:stopped.set()
        r._handlers["transcribe"]=slow
        source=tmp_path/"fixture.wav";source.write_bytes(b"fixture")
        j=r.submit(a,s,"transcribe",{"media":str(source)})
        assert started.wait(5)
        deadline=time.monotonic()+3
        while not unit.process and time.monotonic()<deadline:time.sleep(.01)
        assert unit.process is not None
        independent=run(r,b,s2,"edit_subtitles",{"document":write_doc(tmp_path/"independent.json")})
        assert independent["state"]=="Completed"
        r.cancel(a,j["jobId"])
        result=r.wait(a,j["jobId"],timeout=10)
        assert result["state"]=="Cancelled" and stopped.is_set()
        assert unit.process is None and not r._running



def test_generation_configuration_roundtrip(tmp_path):
    from desktop import defaults, restore_form
    from generation_config import recipe,save,load
    from cytools_core import load_manifest
    manifest=load_manifest(tool.APP/"CyTool.json")
    form=defaults();form.update(media="D:/original outside Tool/音.wav",model="phonon-2.5",threads=2,filter="denoise",hotwords=["Ada Lovelace"],chunk_seconds=8)
    value=recipe(manifest,"transcribe",form)
    path=tmp_path/"config.json";save(path,value)
    restored=defaults();restore_form(restored,load(path,manifest))
    assert restored==form and value["validParameters"]
    assert not list(tmp_path.glob("*.sqlite"))


def test_update_archive_rejection_activation_and_restore(tmp_path,monkeypatch):
    root=tmp_path/"product";root.mkdir()
    monkeypatch.setattr(updates,"ROOT",root);monkeypatch.setattr(updates,"SETTINGS",root/"data/settings");monkeypatch.setattr(updates,"UPDATES",root/"runtime/updates")
    for name in ("../escape", "data/models/destroy", "app/../../escape", "app/bad.py"):
        archive=tmp_path/"invalid.zip"
        with zipfile.ZipFile(archive,"w") as z:
            z.writestr(name,"this is invalid Python !!!")
        with pytest.raises((ValueError,SyntaxError)):updates.extract(archive,tmp_path/"bad")
    archive=tmp_path/"valid.zip"
    manifest=json.loads((tool.APP/"CyTool.json").read_text())
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("app/CyTool.json",json.dumps(manifest));z.writestr("app/release.json",json.dumps({"runtime_abi":updates.ABI,"platform":"any"}));z.writestr("app/desktop.py","VALUE = 2")
    candidate=updates.extract(archive,updates.UPDATES/"candidate")
    (root/"app").mkdir();(root/"app/version.txt").write_text("original")
    # Existing app carries valid metadata for the rollback preflight too.
    (root/"app/CyTool.json").write_text(json.dumps(manifest));(root/"app/release.json").write_text(json.dumps({"runtime_abi":updates.ABI}));(root/"app/desktop.py").write_text("VALUE = 1")
    (root/"data/models").mkdir(parents=True);weight=root/"data/models/preserve.bin";weight.write_bytes(b"weights")
    updates.write(updates.SETTINGS/"update-pending.json",{"app":str(candidate.relative_to(root))})
    updates.apply();assert (root/"app/desktop.py").read_text()=="VALUE = 2"
    assert weight.read_bytes()==b"weights"
    updates.rollback();updates.apply()
    assert (root/"app/version.txt").read_text()=="original" and weight.exists()


def test_local_model_registration_and_corruption(configured,tmp_path):
    import hashlib
    model=tmp_path/"external compatible model";model.mkdir()
    weights=b"fixture container bytes"
    (model/"model.fermion").write_bytes(weights)
    (model/"config.json").write_text(json.dumps({"model_type":"parakeet","sample_rate":16000}))
    (model/"packed_manifest.json").write_text(json.dumps({"format":"fermion-five-value-parakeet-v1","base_model":"nvidia/parakeet-tdt-0.6b-v3","container_sha256":hashlib.sha256(weights).hexdigest()}))
    with tool.create_runtime(tmp_path/"jobs") as r:
        a=actor(r);session=r.create_session(a)["sessionId"]
        registered=run(r,a,session,"register_local_model",{"path":str(model),"name":"Fixture model"})
        assert registered["state"]=="Completed",registered
        assert Path(registered["outputs"]["path"])==model
        assert registered["outputs"]["sha256"]["model.fermion"]==hashlib.sha256(weights).hexdigest()
        (model/"model.fermion").write_bytes(b"corrupted")
        status=run(r,a,session,"model_status",{})
        record=next(x for x in status["outputs"]["models"] if x["id"]==registered["outputs"]["id"])
        assert not record["installed"] and "checksum" in record["reason"].lower()
        with pytest.raises(ValueError):tool.verify_model(model)


def test_second_audio_track_is_actually_selected(configured,tmp_path):
    import imageio_ffmpeg
    import subprocess
    import array
    path=tmp_path/"two tracks.mkv"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-nostdin","-hide_banner","-loglevel","error","-f","lavfi","-i","anullsrc=r=16000:cl=mono:d=1","-f","lavfi","-i","sine=frequency=440:sample_rate=16000:duration=1","-map","0:a","-map","1:a","-c:a","pcm_s16le","-y",str(path)],check=True)
    with tool.create_runtime(tmp_path/"jobs") as r:
        a=actor(r);session=r.create_session(a)["sessionId"]
        first=run(r,a,session,"inspect_media",{"media":str(path),"audio_stream":0})
        second=run(r,a,session,"inspect_media",{"media":str(path),"audio_stream":1})
        assert first["state"]==second["state"]=="Completed"
        with wave.open(first["outputs"]["excerpt"]) as w:quiet=array.array("h",w.readframes(w.getnframes()))
        with wave.open(second["outputs"]["excerpt"]) as w:tone=array.array("h",w.readframes(w.getnframes()))
        assert max(abs(x) for x in quiet)==0 and max(abs(x) for x in tone)>1000
