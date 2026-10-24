import copy
import json
from pathlib import Path

import pytest
from cytools_core import CyToolError,load_manifest
import subtitles
from timing import repair
import tool


def document(cues,words=None,duration=20):
    return {"format":"cytools-subtitles","schemaVersion":1,"cues":cues,"words":words or [],"media":{"durationSeconds":duration,"streams":[]}}

def cue(ident,start,end,text,kind="speech"):
    return {"id":ident,"start":start,"end":end,"text":text,"kind":kind}

def text(doc):return " ".join(" ".join(c["text"].split()) for c in doc["cues"] if c.get("kind","speech")=="speech")


def test_repair_fast_fragments_overlaps_sound_and_raw_words():
    source=document([cue("a",1,1.12,"Hello there."),cue("b",1.12,1.3,"Welcome."),cue("c",1.12,2.,"Come in."),cue("music",1,3,"[music]","sound")],[{"text":"Hello","start":1,"end":1.12}])
    original=copy.deepcopy(source);fixed=repair(source)
    assert source==original
    assert text(fixed)==text(original)
    assert fixed["words"]==source["words"]
    assert next(c for c in fixed["cues"] if c["id"]=="music")==source["cues"][3]
    assert not fixed["warnings"]
    assert len(fixed["cues"])<len(source["cues"])
    assert fixed["timingRepair"]["changes"]


def test_timing_never_drifts_to_hide_unavoidable_fast_dialogue():
    source=document([cue("a",1,1.25,"A very long subtitle which cannot fit this brief moment."),cue("b",1.25,1.5,"Another long sentence in immediate rapid dialogue.")])
    fixed=repair(source,merge_fragments=False,max_advance=.1,max_delay=.1,max_extension=.2,min_duration=.5)
    assert any(w["issue"]=="reading_speed" for w in fixed["warnings"])
    assert not any(w["issue"]=="speech_overlap" for w in fixed["warnings"])
    for before,after in zip(source["cues"],fixed["cues"]):
        assert before["start"]-.101<=after["start"]<=before["start"]+.101
        assert before["end"]-.101<=after["end"]<=before["end"]+.201
    assert fixed["cues"][1]["start"]-fixed["cues"][0]["end"]>=.039


def test_repair_respects_frame_rounding_media_end_and_custom_policy():
    source=document([cue("a",0,.04,"Hi."),cue("b",.16,.44,"Yes."),cue("c",3.999,4.18,"Last one.")],duration=4.2)
    fixed=repair(source,max_cps=12,merge_fragments=False)
    speech=fixed["cues"]
    assert min(c["start"] for c in speech)>=0
    assert max(c["end"] for c in speech)<=4.2
    assert all(b["start"]-a["end"]>=.039 for a,b in zip(speech,speech[1:]))
    assert subtitles.quality(fixed)==subtitles.quality(fixed,12)
    assert len(subtitles.quality(fixed,40))<=len(fixed["warnings"])


def test_repair_changes_neither_manual_text_nor_independent_sound_captions():
    source=document([cue("a",1,2,"My manual correction."),cue("b",10,10.1,"[door]","sound")],[{"text":"Different original text.","start":1,"end":2}])
    fixed=repair(source)
    assert "My manual correction." in text(fixed)
    assert fixed["words"]==source["words"]
    assert next(c for c in fixed["cues"] if c["id"]=="b")==source["cues"][1]


def test_runtime_repairs_external_document_and_exports_before_task_cleanup(tmp_path,monkeypatch):
    monkeypatch.setattr(tool,"ROOT",tmp_path)
    source=tmp_path/"external manual subtitles.json"
    original=document([cue("a",1,1.08,"Welcome."),cue("b",1.1,1.3,"Hello there.")])
    source.write_text(json.dumps(original),"utf-8")
    with tool.create_runtime(tmp_path/"jobs") as runtime:
        actor=runtime.authenticate(runtime.create_client("Repair test")["token"])
        with runtime.task(actor) as session:
            submitted=runtime.submit(actor,session,"repair_subtitles",{"document":str(source),"max_cps":18,"max_extension":1.5})
            job=runtime.wait(actor,submitted["jobId"],timeout=30)
            assert job["state"]=="Completed",job
            path=Path(job["outputs"]["document"])
            fixed=json.loads(path.read_text("utf-8"));assert fixed["timingPolicy"]["max_cps"]==18
            assert text(fixed)==text(original)
            assert not job["outputs"]["warnings"]
            exported=runtime.export_job(actor,job["jobId"],str(tmp_path/"saved"))
        assert not path.exists()
        assert Path(exported["outputs"]["srt"]).exists()
        assert json.loads(source.read_text())==original


def test_old_configuration_receives_new_defaults_without_starting_a_job(tmp_path):
    from generation_config import recipe,save,load
    from desktop import defaults,restore_form
    manifest=load_manifest(tool.APP/"CyTool.json")
    old={"media":"D:/test.mp4","threads":2,"model":"phonon-2.5"}
    path=tmp_path/"old.json";value=recipe(manifest,"transcribe",old);value["toolVersion"]="0.1.0";save(path,value)
    form={};restore_form(form,load(path,manifest))
    assert form["auto_timing"] is True and form["max_cps"]==22
    assert form["threads"]==2 and form["media"]==old["media"]


def test_repeated_repairs_do_not_accumulate_timing_drift():
    source=document([cue("a",1,1.2,"A deliberately fast line."),cue("b",1.25,1.5,"Another very fast subtitle."),cue("c",6,7,"Goodbye.")])
    once=repair(source,merge_fragments=False)
    again=repair(once,merge_fragments=False)
    assert again["cues"]==once["cues"]
    assert again["words"]==once["words"]
    assert again["warnings"]==once["warnings"]
    # An explicit manual edit establishes a new anchor for that edited cue.
    edited=subtitles.edit(once,[{"id":"c","start":10,"end":11}])
    fixed=repair(edited,merge_fragments=False)
    assert fixed["timingAnchors"]["c"]["start"]==10


@pytest.mark.parametrize("policy",[{"max_cps":0},{"max_cps":float("nan")},[],{"max_cps":"fast"}])
def test_malformed_timing_policy_is_rejected(policy):
    source=document([cue("a",1,2,"Hello.")]);source["timingPolicy"]=policy
    with pytest.raises(ValueError):subtitles.validate(source)
