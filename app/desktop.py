"""CyTools_Subtitle Dear ImGui application."""
import json
from pathlib import Path
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from imgui_bundle import hello_imgui, immvision, portable_file_dialogs as pfd
from ui_common import imgui, run, configure_generation, tr
from tool import APP, ROOT, create_runtime, model_records
from preview import Player
import subtitles
import updates
import runtime_components


def defaults():
    from cytools_core import load_manifest
    op=load_manifest(APP/"CyTool.json")["operations"][0]
    return {k:v["default"] for k,v in op["inputSchema"]["properties"].items() if "default" in v}|{"media":""}


def restore_form(form,recipe):
    if recipe["operationId"]!="transcribe": raise ValueError("Use Advanced operations for this configuration")
    form.clear();form.update(defaults());form.update(recipe["parameters"])


def main():
    form=defaults();job=None;subtitle_job=None;message="";frames=0;dialog=None;dialog_kind="";loaded_job=""
    document=None;document_path="";selected=0;cue_text="";cue_start=0.;cue_end=1.;cue_kind=0
    offset=0.;export_folder="";accepted=False;model_status="";sound_text="";sound_duration=2.
    runtime_accepted=False;runtime_info=runtime_components.status(ROOT)
    pool=ThreadPoolExecutor(max_workers=2);future=None;future_kind="";player=Player()
    github=updates.read_settings().get("repository","");automatic=updates.read_settings().get("automaticCheck",False)
    test_installation='--ui-test-installation' in sys.argv
    test_repair='--ui-test-repair' in sys.argv
    test_preview='--ui-test-preview' in sys.argv
    test_started=time.monotonic();test_played=False
    if test_preview:
        report=json.loads((ROOT/'data/reports/real-inference.json').read_text('utf-8'))
        document_path=report['outputs']['document'];document=subtitles.validate(json.loads(Path(document_path).read_text('utf-8')))
        form['media']=str(ROOT/'data/validation-source/Voice sample.mp4');player.open(form['media'])
    if test_repair:
        demo={"format":"cytools-subtitles","schemaVersion":1,"media":{"durationSeconds":10,"streams":[]},"words":[],"cues":[{"id":"demo-1","start":1,"end":1.1,"text":"Hello and welcome.","kind":"speech"},{"id":"demo-2","start":1.1,"end":1.25,"text":"Please come in.","kind":"speech"}]}
        document_path=str(ROOT/'data/reports/repair-ui-input.json');Path(document_path).write_text(json.dumps(demo),'utf-8');document=demo
    image_params=immvision.ImageParams();image_params.image_display_size=(880,330);image_params.show_options_button=False;image_params.show_image_info=False
    image_params.show_pixel_info=False;image_params.refresh_image=True;image_params.resize_keep_aspect_ratio=True
    runner=hello_imgui.RunnerParams();runner.app_window_params.window_title="CyTools_Subtitle"
    runner.app_window_params.window_geometry.size=(1180,900)
    (ROOT/"data/settings").mkdir(parents=True,exist_ok=True)
    runner.ini_filename=str(ROOT/"data/settings/imgui.ini")
    with create_runtime(ROOT/"data/jobs") as runtime:
        actor=runtime.authenticate(runtime.create_client("ImGui",permissions=["network"])["token"])
        session=runtime.create_session(actor,temporary=False)["sessionId"]
        def submit(operation,parameters):
            nonlocal job,message
            try: job=runtime.submit(actor,session,operation,parameters);message=""
            except Exception as exc: message=str(exc)
        def choose(kind):
            nonlocal dialog,dialog_kind
            dialog_kind=kind
            dialog=pfd.select_folder(tr("Export folder")) if kind=="export" else pfd.open_file(tr("Open media") if kind=="media" else tr("Open subtitle document"))
        def select_cue(index):
            nonlocal selected,cue_start,cue_end,cue_text,cue_kind
            selected=index
            cue=document["cues"][index];cue_start=cue["start"];cue_end=cue["end"];cue_text=cue["text"];cue_kind=int(cue.get("kind")=="sound")
        def repair_current():
            keys=("max_cps","min_duration","max_advance","max_delay","max_extension","min_gap","merge_fragments","max_chars","max_lines","max_duration","pause")
            submit("repair_subtitles",{"document":document_path,**{k:form[k] for k in keys}})
        def gui():
            nonlocal job,subtitle_job,message,frames,dialog,loaded_job,document,document_path,selected,cue_text,cue_start,cue_end,cue_kind,offset,export_folder,accepted,model_status,future,future_kind,github,automatic,sound_text,sound_duration,test_played,runtime_accepted,runtime_info
            frames+=1
            if test_repair and frames==3:repair_current()
            if test_repair and frames>30 and job and job["state"] in ("Completed","Failed","Cancelled"):runner.app_shall_exit=True
            if test_preview and player.frame is not None and not test_played:
                player.seek(.5,play=True);test_played=True
            if test_preview and time.monotonic()-test_started>7:runner.app_shall_exit=True
            if dialog and dialog.ready():
                result=dialog.result();dialog=None
                chosen=result if isinstance(result,str) else result[0] if result else ""
                if chosen:
                    try:
                        if dialog_kind=="media": form["media"]=chosen;player.open(chosen,form["audio_stream"])
                        elif dialog_kind=="document":
                            document=subtitles.validate(json.loads(Path(chosen).read_text("utf-8-sig")));document_path=chosen
                            if document["cues"]: select_cue(0)
                        elif dialog_kind=="export":export_folder=chosen
                    except Exception as exc:message=str(exc)
            if future and future.done():
                try: message=json.dumps(future.result(),ensure_ascii=False,indent=2)
                except Exception as exc:message=str(exc)
                future=None
            if job:
                job=runtime.get_job(actor,job["jobId"])
                if job["state"]=="Completed" and loaded_job!=job["jobId"]:
                    loaded_job=job["jobId"];output=job.get("outputs") or {}
                    if output.get("document"):
                        subtitle_job=job
                        document_path=output["document"];document=subtitles.validate(json.loads(Path(document_path).read_text("utf-8")))
                        if document["cues"]:select_cue(0)
                    if job["operationId"]=="install_model":model_status=json.dumps(output,ensure_ascii=False)
                    if job["operationId"] in ("runtime_status","install_runtime"):
                        runtime_info=output;runtime_components.activate(ROOT)
                        import ui_common
                        ui_common._licenses=None
            active=bool(job and job["state"] not in ("Completed","Failed","Cancelled"))
            imgui.text("CyTools_Subtitle");imgui.same_line();imgui.text(tr("Local subtitles · Phonon · SRT / VTT"))
            if imgui.begin_tab_bar("subtitle-tabs"):
                opened,_=imgui.begin_tab_item("Media & generation")
                if opened:
                    _,form["media"]=imgui.input_text("Audio / video file",form["media"])
                    if imgui.button("Open media"):choose("media")
                    imgui.same_line()
                    if imgui.button("Load preview") and form["media"]:player.open(form["media"],form["audio_stream"])
                    models=["phonon-2","phonon-2.5","phonon-2.5-en"]
                    changed,index=imgui.combo("Model",models.index(form["model"]),models)
                    if changed:form["model"]=models[index]
                    imgui.text_wrapped(tr("Phonon-2: English. Phonon-2.5: multilingual including French. CPU inference; no GPU setup needed."))
                    _,form["threads"]=imgui.slider_int("CPU threads",form["threads"],1,32)
                    filters=["none","voice","denoise"]
                    changed,index=imgui.combo("Audio filter",filters.index(form["filter"]),[tr("None"),tr("Voice band + denoise"),tr("Denoise")])
                    if changed:form["filter"]=filters[index]
                    imgui.text_wrapped(tr("Voice filtering reduces noise; it does not isolate vocals from music."))
                    if imgui.collapsing_header("Segmentation & layout"):
                        _,form["chunk_seconds"]=imgui.slider_float("Window seconds",form["chunk_seconds"],5,28)
                        _,form["overlap_seconds"]=imgui.slider_float("Overlap seconds",form["overlap_seconds"],.2,4)
                        _,form["audio_stream"]=imgui.slider_int("Audio track (zero based)",form["audio_stream"],0,31)
                        _,form["max_chars"]=imgui.slider_int("Characters per line",form["max_chars"],10,100)
                        _,form["max_lines"]=imgui.slider_int("Maximum lines",form["max_lines"],1,4)
                        _,form["max_duration"]=imgui.slider_float("Maximum cue seconds",form["max_duration"],.5,20)
                        _,form["pause"]=imgui.slider_float("Split at pause seconds",form["pause"],.1,5)
                        _,form["auto_timing"]=imgui.checkbox("Repair timing automatically",form["auto_timing"])
                        _,form["max_cps"]=imgui.slider_float("Reading characters per second",form["max_cps"],5,40)
                        _,form["min_duration"]=imgui.slider_float("Minimum display seconds",form["min_duration"],.2,3)
                        _,form["max_advance"]=imgui.slider_float("Maximum early shift seconds",form["max_advance"],0,1)
                        _,form["max_delay"]=imgui.slider_float("Maximum onset delay seconds",form["max_delay"],0,2)
                        _,form["max_extension"]=imgui.slider_float("Maximum end extension seconds",form["max_extension"],0,3)
                        _,form["min_gap"]=imgui.slider_float("Minimum caption gap seconds",form["min_gap"],0,.5)
                        _,form["merge_fragments"]=imgui.checkbox("Merge compatible fragments",form["merge_fragments"])
                        changed,text=imgui.input_text("Hotwords (comma separated)",", ".join(form["hotwords"]))
                        if changed:form["hotwords"]=[x.strip() for x in text.split(",") if x.strip()]
                        _,form["hotword_lambda"]=imgui.slider_float("Hotword strength",form["hotword_lambda"],0,10)
                        _,form["local_model"]=imgui.input_text("Optional local Phonon model folder",form["local_model"])
                        imgui.text_wrapped(tr("Local models are referenced in place. Only compatible Phonon-2 family directories; LoRA is not supported by this engine."))
                    imgui.begin_disabled(active)
                    if not runtime_info["ready"]:imgui.text_wrapped(tr("PyTorch is not installed. Open Installation to download it before generating subtitles."))
                    imgui.begin_disabled(not runtime_info["ready"])
                    if imgui.button("Generate subtitles"):submit("transcribe",dict(form))
                    imgui.end_disabled()
                    imgui.same_line()
                    if imgui.button("Inspect media"):submit("inspect_media",{"media":form["media"],"audio_stream":form["audio_stream"],"excerpt":True})
                    imgui.end_disabled()
                    imgui.separator()
                    imgui.text(tr("Preview"))
                    if imgui.button("Play / pause"):player.toggle()
                    imgui.same_line()
                    if imgui.button("Back 2 seconds"):player.seek(player.current_time()-2)
                    changed,position=imgui.slider_float("Timeline (seconds)",player.current_time(),0,max(.1,player.duration),"%.3f")
                    if changed:player.seek(position)
                    imgui.text(f"{player.current_time():.3f} / {player.duration:.3f} s")
                    imgui.text(tr("Source pixels / preview pixels")+f": {player.width} × {player.height} / "+(f"{player.frame.shape[1]} × {player.frame.shape[0]}" if player.frame is not None else "—"))
                    if player.frame is not None:
                        width=min(1050,int(imgui.get_content_region_avail().x));height=min(330,int(width*player.frame.shape[0]/player.frame.shape[1]));width=int(height*player.frame.shape[1]/player.frame.shape[0])
                        image_params.image_display_size=(width,height)
                        image_origin=imgui.get_cursor_screen_pos()
                        immvision.image("##video",player.frame,image_params)
                        if document:
                            now=player.current_time()
                            caption="\n".join(c["text"] for c in document["cues"] if c["start"]<=now<c["end"])
                            if caption:
                                size=imgui.calc_text_size(caption);x=image_origin.x+(width-size.x)/2;y=image_origin.y+height-size.y-18
                                draw=imgui.get_window_draw_list()
                                draw.add_rect_filled((x-10,y-5),(x+size.x+10,y+size.y+5),0xD0000000,4)
                                draw.add_text((x,y),0xFFFFFFFF,caption)
                    if document:
                        now=player.current_time()
                        for cue in document["cues"]:
                            if cue["start"]<=now<cue["end"]:imgui.text_wrapped(cue["text"])
                    if player.error:imgui.text_wrapped(player.error)
                    imgui.end_tab_item()
                opened,_=imgui.begin_tab_item("Subtitle editor",flags=imgui.TabItemFlags_.set_selected if test_repair else 0)
                if opened:
                    if imgui.button("Open subtitle document"):choose("document")
                    imgui.same_line()
                    if imgui.button("Export folder"):choose("export")
                    _,export_folder=imgui.input_text("Export destination",export_folder)
                    imgui.begin_disabled(not subtitle_job or not export_folder)
                    if imgui.button("Export SRT / VTT / JSON"):
                        future=pool.submit(runtime.export_job,actor,subtitle_job["jobId"],export_folder)
                    imgui.end_disabled()
                    if document:
                        imgui.begin_disabled(active)
                        if imgui.button("Save current subtitle bundle"):submit("edit_subtitles",{"document":document_path,"edits":[]})
                        imgui.end_disabled()
                        imgui.text_wrapped(document_path)
                        imgui.text(tr("Cues / timing warnings")+f': {len(document["cues"])} / {len(subtitles.quality(document))}')
                        if document.get("timingRepair",{}).get("state")=="Unresolved":imgui.text_wrapped(tr(document["timingRepair"]["error"]))
                        if imgui.begin_child("cue-list",(0,220)):
                            for i,cue in enumerate(document["cues"]):
                                clicked,_=imgui.selectable(f'{cue["start"]:.3f} -> {cue["end"]:.3f}  {cue["text"].replace(chr(10)," ")}##{cue["id"]}',selected==i)
                                if clicked:select_cue(i);player.seek(cue["start"])
                        imgui.end_child()
                        if document["cues"]:
                            _,cue_start=imgui.input_double("Start seconds",cue_start,.04,.2,"%.3f")
                            _,cue_end=imgui.input_double("End seconds",cue_end,.04,.2,"%.3f")
                            _,cue_text=imgui.input_text_multiline("Caption",cue_text,(0,90))
                            _,cue_kind=imgui.combo("Cue type",cue_kind,[tr("Speech"),tr("Sound description")])
                            imgui.begin_disabled(active)
                            if imgui.button("Apply cue edit"):submit("edit_subtitles",{"document":document_path,"edits":[{"id":document["cues"][selected]["id"],"start":cue_start,"end":cue_end,"text":cue_text,"kind":["speech","sound"][cue_kind]}]})
                            imgui.same_line()
                            if imgui.button("Delete cue"):submit("edit_subtitles",{"document":document_path,"edits":[{"id":document["cues"][selected]["id"],"delete":True}]})
                            imgui.end_disabled()
                        _,offset=imgui.input_double("Shift entire track seconds",offset,.04,.2,"%.3f")
                        imgui.begin_disabled(active)
                        if imgui.button("Apply track shift"):submit("edit_subtitles",{"document":document_path,"offset_seconds":offset})
                        imgui.same_line()
                        if imgui.button("Rebuild layout from original words"):submit("reflow_subtitles",{"document":document_path,**{k:form[k] for k in ("max_chars","max_lines","max_duration","pause","auto_timing","max_cps","min_duration","max_advance","max_delay","max_extension","min_gap","merge_fragments")}})
                        if imgui.button("Repair reading time and overlaps"):repair_current()
                        imgui.end_disabled()
                        imgui.text_wrapped(tr("Repair preserves every word. Remaining fast-dialogue warnings require review within the chosen timing limits."))
                        _,sound_text=imgui.input_text("Sound description at playhead",sound_text)
                        _,sound_duration=imgui.slider_float("Sound caption duration",sound_duration,.1,20)
                        imgui.begin_disabled(active or not sound_text.strip())
                        if imgui.button("Add sound description"):
                            import uuid
                            start=player.current_time();submit("edit_subtitles",{"document":document_path,"edits":[{"id":"sound-"+uuid.uuid4().hex[:12],"start":start,"end":start+sound_duration,"text":sound_text,"kind":"sound"}]})
                        imgui.end_disabled()
                    imgui.end_tab_item()
                opened,_=imgui.begin_tab_item("Installation",flags=imgui.TabItemFlags_.set_selected if test_installation else 0)
                if opened:
                    imgui.text("PyTorch CPU "+runtime_info["expectedVersion"]);imgui.same_line();imgui.text(tr(runtime_info["state"]))
                    imgui.text_wrapped(tr("PyTorch is downloaded separately and installed privately for this Tool. CPU inference only."))
                    if imgui.button("PyTorch license and source"):
                        import webbrowser
                        webbrowser.open(runtime_components.LICENSE_URL)
                    _,runtime_accepted=imgui.checkbox("I reviewed the PyTorch license",runtime_accepted)
                    imgui.begin_disabled(active or not runtime_accepted)
                    if imgui.button("Download / repair PyTorch"):submit("install_runtime",{"license_accepted":runtime_accepted,"repair":True})
                    imgui.end_disabled()
                    imgui.begin_disabled(active)
                    if imgui.button("Check PyTorch installation"):submit("runtime_status",{})
                    imgui.end_disabled()
                    imgui.separator()
                    imgui.text_wrapped(tr("Public model weights: CC-BY-4.0. Download size about 160 MB per model; expanded installation is larger. Downloads stay private to this Tool."))
                    if imgui.button("Official model page"):
                        import webbrowser
                        repo={"phonon-2":"Phonon-2","phonon-2.5":"Phonon-2.5","phonon-2.5-en":"Phonon-2.5-English"}[form["model"]]
                        webbrowser.open("https://huggingface.co/FermionResearch/"+repo)
                    _,accepted=imgui.checkbox("I reviewed the model license",accepted)
                    imgui.text(tr("Selected model")+": "+form["model"])
                    for key,value in model_records().items():imgui.text_wrapped(key+": "+value["path"])
                    imgui.begin_disabled(active or not accepted)
                    if imgui.button("Download / resume / repair model"):submit("install_model",{"model":form["model"],"license_accepted":accepted})
                    imgui.end_disabled()
                    if imgui.button("Check installation"):submit("model_status",{})
                    _,form["local_model"]=imgui.input_text("Local model directory",form["local_model"])
                    imgui.begin_disabled(active or not form["local_model"])
                    if imgui.button("Register local model"):
                        submit("register_local_model",{"path":form["local_model"],"name":Path(form["local_model"]).name,"model":form["model"]})
                    imgui.end_disabled()
                    for ident,record in model_records().items():
                        if ident.startswith("local-") and imgui.button(record.get("name",ident)+"##"+ident):
                            form["local_model"]=record["path"];form["model"]=record.get("model","phonon-2")
                    if model_status:imgui.text_wrapped(model_status)
                    imgui.end_tab_item()
                opened,_=imgui.begin_tab_item("Updates")
                if opened:
                    imgui.text_wrapped(tr("Configure the application GitHub repository. No public repository is assumed. Engine updates require a new tested runtime; model downloads are separate."))
                    _,github=imgui.input_text("GitHub owner/repository",github)
                    _,automatic=imgui.checkbox("Check updates at startup",automatic)
                    if imgui.button("Save update settings"):
                        try:updates.write_settings({"repository":github,"automaticCheck":automatic});message=tr("Saved")
                        except Exception as exc:message=str(exc)
                    imgui.begin_disabled(future is not None or active)
                    for label,action in (("Check updates",updates.check),("Download update",updates.download),("Restore previous version",updates.rollback)):
                        if imgui.button(label):future=pool.submit(action)
                        imgui.same_line()
                    imgui.end_disabled();imgui.new_line()
                    imgui.text_wrapped(tr("Updates activate on restart and preserve data. Releases contain app/ only, with a matching Tool ID and runtime ABI."))
                    imgui.end_tab_item()
                imgui.end_tab_bar()
            if job:
                imgui.separator();imgui.text(tr(job["state"])+" · "+job["operationId"])
                progress=job.get("progress") or {};imgui.progress_bar(float(progress.get("percent",0))/100,(-1,0),tr(str(progress.get("currentStep",""))))
                if active and imgui.button("Cancel"):runtime.cancel(actor,job["jobId"])
                if job.get("error"):
                    imgui.text_wrapped(tr(job["error"]["code"])+": "+tr(job["error"]["message"]))
                if job["state"]=="Completed" and job["operationId"]=="inspect_media":
                    imgui.input_text_multiline("Inspection result",json.dumps(job["outputs"],indent=2,ensure_ascii=False),(0,120))
            if message:imgui.text_wrapped(message)
            if ('--smoke-test' in sys.argv or test_installation) and frames>20:runner.app_shall_exit=True
        configure_generation(runtime,lambda:{"operationId":"transcribe","parameters":dict(form)},lambda recipe:restore_form(form,recipe))
        runner.callbacks.show_gui=gui
        try:
            if automatic and github:future=pool.submit(updates.check)
            run(runner)
            if test_preview:
                from standalone_log import save_screenshot
                save_screenshot(ROOT/'data/reports/preview.png',hello_imgui.final_app_window_screenshot())
            if test_installation:
                from standalone_log import save_screenshot
                from ui_common import preferences
                save_screenshot(ROOT/('data/reports/installation-'+preferences.values['language']+'.png'),hello_imgui.final_app_window_screenshot())
                (ROOT/'data/reports/installation-ui.json').write_text(json.dumps(runtime_info),'utf-8')
            if test_repair:
                assert job and job["state"]=="Completed",job
                assert not document["warnings"],document["warnings"]
                from standalone_log import save_screenshot
                from ui_common import preferences
                save_screenshot(ROOT/('data/reports/repair-'+preferences.values['language']+'.png'),hello_imgui.final_app_window_screenshot())
                (ROOT/'data/reports/repair-ui.json').write_text(json.dumps({"state":job["state"],"cueCount":len(document["cues"]),"warnings":document["warnings"]}),'utf-8')
        finally:
            player.stop();pool.shutdown(wait=True,cancel_futures=True)


if __name__=="__main__":main()
