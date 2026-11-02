"""CyTools_Subtitle Dear ImGui application."""
import json
from pathlib import Path
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from imgui_bundle import hello_imgui, portable_file_dialogs as pfd
from subtitle_ui import DocumentHistory, CaptionTimeline, CaptionInspector, VideoSurface, stable_id
from cyui_modules.commands import Command, CommandState, command_palette
from cyui_modules.common import Range
from ui_common import imgui, run, configure_generation, tr
from tool import APP, ROOT, create_runtime, model_records
from preview import Player
from file_drop import FileDrops
from diarization_ui import Panel as SpeakerPanel, generation_options as speaker_options, engine_selector as choose_speaker_engine, device_selector as choose_speaker_device
import speakers
import subtitles
import updates
import runtime_components
import cyui
import ui_common
from ui_common import label, preferences


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
    speaker_panel=SpeakerPanel(ROOT);cue_speaker=""
    runtime_accepted=False;runtime_info=runtime_components.status(ROOT)
    pool=ThreadPoolExecutor(max_workers=2);future=None;future_kind="";player=Player()
    history=DocumentHistory();timelines={key:CaptionTimeline() for key in ('##workspace-timeline','##editor-timeline')};caption_inspector=CaptionInspector();surface=VideoSurface()
    command_state=CommandState();commands_open=False;module_test_phase=0;previous_view=None;submitted_revision=None
    github=updates.read_settings().get("repository","");automatic=updates.read_settings().get("automaticCheck",False)
    test_installation='--ui-test-installation' in sys.argv
    test_repair='--ui-test-repair' in sys.argv
    test_preview='--ui-test-preview' in sys.argv
    test_speakers='--ui-test-speakers' in sys.argv;speaker_test_phase=0
    test_nvidia=any(a.startswith('--ui-test-nvidia') for a in sys.argv);test_nvidia_generate='--ui-test-nvidia-generate' in sys.argv;nvidia_test_submitted=False;nvidia_completion_frame=0
    if test_nvidia:
        form.update(model='phonon-2.5',diarization=True,diarization_engine='nemotron3',nemotron_device=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--ui-test-nvidia-device=')),'cuda'))
    test_started=time.monotonic();test_played=False
    test_media=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--ui-test-media=')),None)
    test_drop='--ui-test-file-drop' in sys.argv
    drops=FileDrops();drop_count=0;preview_frames=0;render_error="";test_paused=False
    view='Workspace';search='';last_state=''
    for flag,target in [('--ui-test-installation','Installation'),('--ui-test-repair','Subtitle editor'),('--ui-test-options','Options'),('--ui-test-logs','Application log'),('--ui-test-advanced','Advanced operations'),('--ui-test-speakers','Subtitle editor'),('--ui-test-speaker-installation','Installation'),('--ui-test-nvidia-installation','Installation'),('--ui-test-nvidia-settings','Media & generation')]:
        if flag in sys.argv:view=target
    view=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--ui-test-view=')),view)
    if test_preview:
        report=json.loads((ROOT/'data/reports/real-inference.json').read_text('utf-8'))
        document_path=report['outputs']['document'];document=subtitles.validate(json.loads(Path(document_path).read_text('utf-8')))
        form['media']=str(ROOT/'data/validation-source/Voice sample.mp4');player.open(form['media'])
    if test_repair:
        demo={"format":"cytools-subtitles","schemaVersion":1,"media":{"durationSeconds":10,"streams":[]},"words":[],"cues":[{"id":"demo-1","start":1,"end":1.1,"text":"Hello and welcome.","kind":"speech"},{"id":"demo-2","start":1.1,"end":1.25,"text":"Please come in.","kind":"speech"}]}
        document_path=str(ROOT/'data/reports/repair-ui-input.json');Path(document_path).write_text(json.dumps(demo),'utf-8');document=demo
    if test_speakers:
        document={'format':'cytools-subtitles','schemaVersion':1,'words':[], 'speakers':[{'id':'speaker-1','name':'Person 1'},{'id':'speaker-2','name':'Person 2'}],'cues':[{'id':'speaker-demo-1','start':1,'end':3,'text':'Hello and welcome.','kind':'speech','speaker':'speaker-1'},{'id':'speaker-demo-2','start':4,'end':6,'text':'Thank you for having me.','kind':'speech','speaker':'speaker-2'}]}
        document_path=str(ROOT/'data/reports/speaker-ui-input.json');Path(document_path).parent.mkdir(parents=True,exist_ok=True);Path(document_path).write_text(json.dumps(document),'utf-8')
    test_document=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--ui-test-document=')),None)
    if test_document:
        document_path=str(Path(test_document).resolve());document=subtitles.validate(json.loads(Path(document_path).read_text('utf-8')))
    if '--ui-test-commands' in sys.argv:commands_open=True
    if document:history.load(document,document_path,reset=True)
    runner=hello_imgui.RunnerParams();runner.app_window_params.window_title="CyTools_Subtitle"
    runner.app_window_params.window_geometry.size=(1500,960)
    runner.platform_backend_type=hello_imgui.PlatformBackendType.glfw
    runner.callbacks.before_exit=lambda:(surface.close(),drops.close())
    runner.imgui_window_params.default_imgui_window_type=hello_imgui.DefaultImGuiWindowType.no_default_window
    if '--ui-test-small' in sys.argv:runner.app_window_params.window_geometry.size=(1024,768)
    (ROOT/"data/settings").mkdir(parents=True,exist_ok=True)
    runner.ini_filename=str(ROOT/("data/reports/cyui-test.ini" if any(a.startswith(("--ui-test","--smoke-test")) for a in sys.argv) else "data/settings/imgui.ini"))
    Path(runner.ini_filename).parent.mkdir(parents=True,exist_ok=True)
    test_mode=any(a.startswith(("--ui-test","--smoke-test")) for a in sys.argv)
    jobs_root=ROOT/("data/reports/ui-test-jobs-"+uuid.uuid4().hex if test_mode else "data/jobs")
    with create_runtime(jobs_root) as runtime:
        actor=runtime.authenticate(runtime.create_client("ImGui",permissions=["network"])["token"])
        session=runtime.create_session(actor,temporary=False)["sessionId"]
        def submit(operation,parameters):
            nonlocal job,message,submitted_revision
            try:
                job=runtime.submit(actor,session,operation,parameters);message=""
                submitted_revision=history.revision if parameters.get("document")==document_path else None
            except Exception as exc: message=str(exc)
        def restore_history(direction):
            nonlocal document,document_path,subtitle_job
            selected_id=document['cues'][selected]['id'] if document and selected<len(document['cues']) else None
            version=history.move(direction)
            if version is not None:
                document=version.document;document_path=version.path;subtitle_job=version.job
                if document["cues"]:select_cue(next((i for i,c in enumerate(document['cues']) if c['id']==selected_id),min(selected,len(document['cues'])-1)))
        def history_buttons(active):
            with cyui.scoped_disabled(active or not history.can_undo):
                if cyui.icon_button(cyui.icon.undo,tr("Undo (Ctrl+Z)")):restore_history(-1)
            imgui.same_line()
            with cyui.scoped_disabled(active or not history.can_redo):
                if cyui.icon_button(cyui.icon.redo,tr("Redo (Ctrl+Y)")):restore_history(1)
        def draw_timeline(active,identifier,height=150):
            nonlocal message
            if not document:return
            caption_timeline=timelines[identifier]
            try:
                result=caption_timeline.draw(identifier,document,history.revision,player.current_time(),player.duration,document["cues"][selected]["id"] if document["cues"] else None,active,height)
                chosen=next((i for i,c in enumerate(document["cues"]) if stable_id("cue",c["id"]) in caption_timeline.state.selected),None)
                if chosen is not None and chosen!=selected:select_cue(chosen)
                if result["seek"] is not None:player.seek(result["seek"])
                if result["clips"].committed:
                    patches=caption_timeline.patches(result["clips"].value)
                    if patches:submit("edit_subtitles",{"document":document_path,"edits":patches})
                if result["remove"] and not active:
                    submit("edit_subtitles",{"document":document_path,"edits":[{"id":caption_timeline.by_id[key]["id"],"delete":True} for key in result["remove"]]})
            except ValueError as exc:message=tr(str(exc));cyui.callout("warning",message)
        def choose(kind):
            nonlocal dialog,dialog_kind
            dialog_kind=kind
            dialog=pfd.select_folder(tr("Export folder")) if kind=="export" else pfd.open_file(tr("Open media") if kind=="media" else tr("Open subtitle document"))
        def open_path(path,kind=None):
            nonlocal document,document_path,subtitle_job,view,message,render_error
            try:
                candidate=Path(path).expanduser().resolve()
                if not candidate.is_file():raise ValueError(tr('The dropped path is not a file.'))
                if kind=='document' or (kind is None and candidate.suffix.lower()=='.json'):
                    parsed=subtitles.validate(json.loads(candidate.read_text('utf-8-sig')))
                    document=parsed;document_path=str(candidate);subtitle_job=None
                    history.load(document,document_path,reset=True)
                    for timeline_view in timelines.values():timeline_view.revision=-1
                    if document['cues']:select_cue(0)
                    view='Workspace'
                else:
                    if kind is None and candidate.suffix.lower() not in ('.wav','.mp3','.m4a','.aac','.flac','.ogg','.opus','.aiff','.aif','.mp4','.mkv','.mov','.webm','.avi','.wmv','.m4v','.wma'):
                        raise ValueError(tr('Drop an audio/video file or a subtitle JSON document.'))
                    player.open(str(candidate),form['audio_stream']);form['media']=str(candidate);render_error='';view='Workspace'
                message=''
            except Exception as exc:
                message=str(exc);cyui.notify(message,'error');ui_common.journal.write(message,'ERROR')
        def install_drop_test():
            if test_drop:
                path=ROOT/'data/reports/drop-window.json';path.parent.mkdir(parents=True,exist_ok=True)
                import os
                path.write_text(json.dumps({'hwnd':drops.native_window,'pid':os.getpid(),'error':drops.error}),'utf-8')
        runner.callbacks.post_init=lambda:(drops.install(),install_drop_test())
        def select_cue(index):
            nonlocal selected,cue_start,cue_end,cue_text,cue_kind,cue_speaker
            selected=index;cue_speaker=document["cues"][index].get("speaker") or ""
            cue=document["cues"][index];cue_start=cue["start"];cue_end=cue["end"];cue_text=cue["text"];cue_kind=int(cue.get("kind")=="sound")
        def repair_current():
            keys=("max_cps","min_duration","max_advance","max_delay","max_extension","min_gap","merge_fragments","max_chars","max_lines","max_duration","pause")
            submit("repair_subtitles",{"document":document_path,**{k:form[k] for k in keys}})
        def gui():
            nonlocal previous_view,module_test_phase,commands_open,nvidia_completion_frame,nvidia_test_submitted,speaker_test_phase,cue_speaker,drop_count,preview_frames,render_error,test_paused,view,search,last_state,job,subtitle_job,message,frames,dialog,loaded_job,document,document_path,selected,cue_text,cue_start,cue_end,cue_kind,offset,export_folder,accepted,model_status,future,future_kind,github,automatic,sound_text,sound_duration,test_played,runtime_accepted,runtime_info
            frames+=1
            if test_speakers and frames==3:
                submit('rename_speakers',{'document':document_path,'names':{'speaker-1':'Alice','speaker-2':'Bob'}});speaker_test_phase=1
            if frames==3 and test_media:open_path(test_media,'media')
            if test_nvidia_generate and frames>=4 and form['media'] and not nvidia_test_submitted:
                submit('transcribe',dict(form));nvidia_test_submitted=True
            for batch in drops.poll():
                # A project is one media file and optionally one subtitle document.
                if not batch:
                    message=tr('Could not read the dropped file paths.');cyui.notify(message,'error');continue
                if len(batch)>2:
                    message=tr('Drop one media file and optionally one subtitle JSON document.');cyui.notify(message,'warning');continue
                for path in batch:
                    open_path(path);drop_count+=1
            if frames==1 and drops.error:
                ui_common.journal.write('File drop: '+drops.error,'ERROR')
            if (test_media or test_drop) and player.duration>0:
                if not test_played:player.seek(.5,play=True);test_played=True
                elif time.monotonic()-test_started>4 and not test_paused:player.stop();test_paused=True
            if (test_media or test_drop) and not test_nvidia_generate and time.monotonic()-test_started>9:runner.app_shall_exit=True
            if test_nvidia_generate and time.monotonic()-test_started>120:raise RuntimeError('NVIDIA GUI generation test timed out')
            if frames==1 and document and document["cues"]:select_cue(0)
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
                        if dialog_kind=='export':export_folder=chosen
                        else:open_path(chosen,dialog_kind)
                    except Exception as exc:message=str(exc)
            if future and future.done():
                try: message=json.dumps(future.result(),ensure_ascii=False,indent=2);cyui.notify(tr('Completed'),'success')
                except Exception as exc:message=str(exc);cyui.notify(str(exc),'error')
                future=None
            if job:
                job=runtime.get_job(actor,job["jobId"])
                if job["state"]=="Completed" and loaded_job!=job["jobId"]:
                    loaded_job=job["jobId"];output=job.get("outputs") or {}
                    if output.get('document') and submitted_revision is not None and submitted_revision!=history.revision:
                        message=tr('The result was saved, but the open document changed during processing.')+'\n'+output['document']
                    elif output.get("document"):
                        subtitle_job=job
                        document_path=output["document"];document=subtitles.validate(json.loads(Path(document_path).read_text("utf-8")))
                        previous_id=history.current.document["cues"][selected]["id"] if history.current and selected<len(history.current.document["cues"]) else None
                        history.load(document,document_path,job,reset=job["operationId"]=="transcribe")
                        if document["cues"]:select_cue(next((i for i,c in enumerate(document["cues"]) if c["id"]==previous_id),0))
                    if job['operationId'] in ('diarization_status','install_diarization_runtime','install_diarization_model','register_diarization_model','nemotron_status','install_nemotron_runtime','install_nemotron_model','register_nemotron_model'):
                        speaker_panel.refresh();ui_common._licenses=None
                        if hasattr(ui_common,'_dependencies'):del ui_common._dependencies
                    if job['operationId']=='check_diarization_access':speaker_panel.message=tr(output.get('message',output.get('state','')))
                    if job["operationId"]=="install_model":model_status=json.dumps(output,ensure_ascii=False)
                    if job["operationId"] in ("runtime_status","install_runtime"):
                        runtime_info=output;runtime_components.activate(ROOT)
                        ui_common._licenses=None
            active=bool(job and job["state"] not in ("Completed","Failed","Cancelled"))
            if test_speakers and not active and job and job['state']=='Completed':
                if speaker_test_phase==1:
                    assert document['speakers'][0]['name']=='Alice'
                    submit('edit_subtitles',{'document':document_path,'edits':[{'id':'speaker-demo-1','speaker':'speaker-2'}]});speaker_test_phase=2
                elif speaker_test_phase==2 and frames>25:
                    assert document['cues'][0]['speaker']=='speaker-2' and document['cues'][0]['speakerManual']
                    runner.app_shall_exit=True
            if test_nvidia_generate and nvidia_test_submitted and not active and job and frames>25:
                assert job['state']=='Completed',job.get('error')
                assert document['diarization']['engine']=='nemotron3' and document['diarization']['device']==('cuda:0' if form['nemotron_device']=='cuda' else 'cpu')
                if not nvidia_completion_frame:nvidia_completion_frame=frames
                if frames>nvidia_completion_frame+12:runner.app_shall_exit=True
            if '--ui-test-modules-history' in sys.argv and document and not active:
                if module_test_phase==0:
                    cue=document['cues'][0];submit('edit_subtitles',{'document':document_path,'edits':[{'id':cue['id'],'start':cue['start']+.2,'end':cue['end']+.2}]});module_test_phase=1
                elif module_test_phase==1 and job and job['state']=='Completed':
                    assert history.can_undo and len(history.versions)==2
                    expected=document['cues'][0]['start'];restore_history(-1)
                    assert document['cues'][0]['start']==round(expected-.2,6) and history.can_redo
                    restore_history(1);assert document['cues'][0]['start']==expected
                    module_test_phase=2
            # Keyboard actions are suppressed while typing into any field.
            io=imgui.get_io()
            if not io.want_text_input and not commands_open:
                if io.key_ctrl and io.key_shift and imgui.is_key_pressed(imgui.Key.p,False):commands_open=True
                if not active and io.key_ctrl and imgui.is_key_pressed(imgui.Key.z,False):restore_history(1 if io.key_shift else -1)
                if not active and io.key_ctrl and imgui.is_key_pressed(imgui.Key.y,False):restore_history(1)
                if io.key_ctrl and imgui.is_key_pressed(imgui.Key.o,False):choose('document' if io.key_shift else 'media')
                if io.key_ctrl and imgui.is_key_pressed(imgui.Key.r,False) and form['media']:player.open(form['media'],form['audio_stream'])
                if imgui.is_key_pressed(imgui.Key.left_arrow,False):player.seek(player.current_time()-2)
                if imgui.is_key_pressed(imgui.Key.space,False) and not imgui.is_mouse_down(0) and not surface.state.canvas.panning:player.toggle()
                if io.key_ctrl and imgui.is_key_pressed(imgui.Key.s,False) and document and not active:
                    submit('edit_subtitles',{'document':document_path,'edits':[]})
            state=job['state'] if job else 'Ready'
            if job and state!=last_state:
                if state in ('Completed','Failed','Cancelled'):cyui.notify(tr(state), 'success' if state=='Completed' else 'error' if state=='Failed' else 'warning')
                last_state=state
            cyui.begin_top_bar('###subtitle-top')
            cyui.heading('CyTools_Subtitle',3);imgui.same_line();cyui.text_dim(tr('Local subtitles · Phonon · SRT / VTT'))
            cyui.end_top_bar()
            cyui.begin_status_bar('###subtitle-status')
            cyui.status_text('accent' if active else 'success',tr(state))
            imgui.same_line();cyui.text_faint((' · '+job['operationId']) if job else ' · CPU · '+form['model'])
            imgui.same_line();cyui.text_faint(tr('Space: play / pause · Ctrl+O: open · Ctrl+S: save'))
            cyui.end_status_bar()
            cyui.begin_sidebar('###subtitle-navigation',205)
            cyui.sidebar_header(tr('Subtitle studio'))
            cyui.sidebar_group(tr('PROJECT'))
            for name,glyph in [('Workspace',cyui.icon.video),('Media & generation',cyui.icon.microphone),('Subtitle editor',cyui.icon.edit)]:
                if cyui.sidebar_item(glyph,tr(name),view==name):view=name
            cyui.sidebar_group(tr('APPLICATION'))
            for name,glyph in [('Installation',cyui.icon.download),('Updates',cyui.icon.refresh),('Advanced operations',cyui.icon.code),('Application log',cyui.icon.document),('Options',cyui.icon.settings)]:
                if cyui.sidebar_item(glyph,tr(name),view==name):view=name
            cyui.space(18);cyui.badge(tr('Transcription')+' · CPU','neutral')
            if document and document.get('diarization',{}).get('device'):cyui.badge(tr('Voices')+' · '+document['diarization']['device'].upper(),'neutral')
            cyui.text_faint('SRT / WebVTT / JSON')
            cyui.end_sidebar()
            vp=imgui.get_main_viewport()
            imgui.set_next_window_pos(vp.work_pos);imgui.set_next_window_size(vp.work_size)
            flags=imgui.WindowFlags_.no_title_bar|imgui.WindowFlags_.no_move|imgui.WindowFlags_.no_resize|imgui.WindowFlags_.no_saved_settings
            imgui.begin('###subtitle-content',flags=flags)
            if previous_view!=view:
                for timeline_view in timelines.values():
                    timeline_view.state.mode=0;timeline_view.state.panning=False;timeline_view.state.preview.clear()
                previous_view=view
            cyui.panel_header(tr(view),tr('Review speech, timing and sound descriptions.'))
            cyui.divider()
            if active:
                progress=job.get('progress') or {}
                cyui.progress_bar(float(progress.get('percent',0))/100,overlay=tr(str(progress.get('currentStep',''))))
                if cyui.button(label('Cancel')):runtime.cancel(actor,job['jobId'])
            if job and job.get('error'):cyui.callout('error',tr(job['error']['code'])+': '+tr(job['error']['message']))
            if view=='Workspace':
                cyui.begin_toolbar('##workspace-tools')
                if cyui.icon_button(cyui.icon.folder,tr('Open media (Ctrl+O)')):choose('media')
                imgui.same_line()
                if cyui.icon_button(cyui.icon.document,tr('Open subtitle document (Ctrl+Shift+O)')):choose('document')
                imgui.same_line()
                with cyui.scoped_disabled(not document or active):
                    if cyui.icon_button(cyui.icon.save,tr('Save current subtitle bundle (Ctrl+S)')):submit('edit_subtitles',{'document':document_path,'edits':[]})
                imgui.same_line();cyui.toolbar_separator();imgui.same_line()
                with cyui.scoped_disabled(not form['media']):
                    if cyui.icon_button(cyui.icon.refresh,tr('Load preview (Ctrl+R)')):player.open(form['media'],form['audio_stream'])
                imgui.same_line();history_buttons(active)
                imgui.same_line()
                if cyui.icon_button(cyui.icon.search,tr('Command palette (Ctrl+Shift+P)')):commands_open=True
                imgui.same_line();cyui.text_dim(Path(form['media']).name if form['media'] else tr('No media selected'))
                cyui.end_toolbar()
                wide=imgui.get_content_region_avail().x>cyui.dp(880)
                if wide:wide=imgui.begin_table('##workspace-columns',2,imgui.TableFlags_.resizable)
                if wide:
                    imgui.table_setup_column('preview',imgui.TableColumnFlags_.width_stretch,3)
                    imgui.table_setup_column('inspector',imgui.TableColumnFlags_.width_stretch,1.2)
                    imgui.table_next_column()
                cyui.begin_card('##preview-card',tr('Preview'))
                room=imgui.get_content_region_avail().x
                height=min(cyui.dp(335),room*9/16)
                frame=player.frame
                if frame is not None:
                    caption='\n'.join(speakers.display_text(document,c) for c in document['cues'] if c['start']<=player.current_time()<c['end']) if document else ''
                    try:surface.draw(frame,(room,height),caption);preview_frames+=1
                    except (TypeError,ValueError,RuntimeError) as exc:
                        detail=tr('Video preview failed: ')+str(exc)
                        if detail!=render_error:ui_common.journal.write(detail,'ERROR');cyui.notify(detail,'error')
                        render_error=detail;imgui.dummy((room,height))
                else:
                    imgui.begin_child('##empty-preview',(0,height))
                    cyui.empty_state(tr('Audio / video preview'),tr('Drop an audio/video file here or open media to review your subtitles in sync.'),cyui.icon.audio if form['media'] else cyui.icon.video)
                    if form['media']:cyui.text_dim(Path(form['media']).name)
                    imgui.end_child()
                with cyui.scoped_disabled(not player.duration):
                    if cyui.icon_button(cyui.icon.play,tr('Play / pause (Space)')):player.toggle()
                    imgui.same_line()
                    if cyui.icon_button(cyui.icon.back,tr('Back 2 seconds (Left arrow)')):player.seek(player.current_time()-2)
                    imgui.same_line();cyui.text_mono(f'{player.current_time():.1f} / {player.duration:.1f} s')
                if not document and player.duration:
                    changed,position=cyui.slider_bar('##media-seek',player.current_time(),0,max(.1,player.duration),'%.2f s',-1)
                    if changed:player.seek(position)
                draw_timeline(active,'##workspace-timeline',165 if document and document.get('speakers') else 115)
                if document:
                    cyui.text_faint(tr('Wheel: zoom · Shift+wheel: pan · Ctrl+wheel: lanes · Drag edges: trim · Esc: cancel'))
                cyui.text_faint(tr('Source pixels / preview pixels')+f': {player.width} × {player.height} / '+(f'{frame.shape[1]} × {frame.shape[0]}' if frame is not None else '—'))
                if player.error:cyui.callout('error',player.error)
                if render_error:cyui.callout('error',render_error)
                cyui.end_card()
                cyui.begin_card('##cue-summary',tr('Subtitles'))
                if document:
                    warnings=subtitles.quality(document)
                    analysis=document.get('diarization',{})
                    if analysis.get('model'):
                        engine_name='NVIDIA Nemotron 3' if analysis.get('engine')=='nemotron3' else analysis['model']
                        cyui.text_dim(tr('Speaker analysis')+': '+engine_name+' · '+analysis.get('device',''))
                        unassigned=sum(c.get('kind','speech')=='speech' and c.get('speaker') is None for c in document['cues'])
                        if unassigned:cyui.badge(str(unassigned)+' '+tr('Captions without a speaker'),'warning')
                    cyui.badge(str(len(document['cues']))+' '+tr('Cues'),'neutral');imgui.same_line();cyui.badge(str(len(warnings))+' '+tr('Timing warnings'),'warning' if warnings else 'success')
                    _,search=cyui.search_field('##cue-search',search,tr('Search captions'))
                    if imgui.begin_table('##caption-table',3,imgui.TableFlags_.scroll_y|imgui.TableFlags_.row_bg|imgui.TableFlags_.borders_inner_h,(0,cyui.dp(210))):
                        imgui.table_setup_column(tr('Time'),imgui.TableColumnFlags_.width_fixed,cyui.dp(155));imgui.table_setup_column(tr('Caption'),imgui.TableColumnFlags_.width_stretch);imgui.table_setup_column(tr('Type'),imgui.TableColumnFlags_.width_fixed,cyui.dp(70));imgui.table_headers_row()
                        for i,cue in enumerate(document['cues']):
                            if search.casefold() not in cue['text'].casefold():continue
                            imgui.table_next_row();imgui.table_next_column()
                            clicked,_=imgui.selectable(f"{cue['start']:.2f} → {cue['end']:.2f}##{cue['id']}",selected==i,imgui.SelectableFlags_.span_all_columns)
                            if clicked:select_cue(i);player.seek(cue['start'])
                            imgui.table_next_column();ui_common.raw().text_wrapped(speakers.display_text(document,cue));imgui.table_next_column();cyui.text_dim(tr('Sound' if cue.get('kind')=='sound' else 'Speech'))
                        imgui.end_table()
                else:cyui.empty_state(tr('No subtitles yet'),tr('Generate phrase captions, then review their timing here.'),cyui.icon.document)
                cyui.end_card()
                if wide:imgui.table_next_column()
                cyui.begin_card('##generation-summary',tr('Generation'))
                if cyui.begin_properties('##quick-generation'):
                    cyui.property(tr('Model'));models=['phonon-2','phonon-2.5','phonon-2.5-en']
                    changed,index=imgui.combo('##quick-model',models.index(form['model']),models)
                    if changed:form['model']=models[index]
                    cyui.property(tr('CPU threads'));_,form['threads']=imgui.slider_int('##quick-threads',form['threads'],1,32)
                    cyui.property(tr('Audio track (zero based)'));_,form['audio_stream']=imgui.slider_int('##quick-track',form['audio_stream'],0,31)
                    cyui.property(tr('Identify different speakers'));_,form['diarization']=imgui.checkbox('##quick-diarization',form['diarization'])
                    if form['diarization']:choose_speaker_engine(form,'quick-speaker-engine');choose_speaker_device(form,'quick-nvidia-compute')
                    cyui.end_properties()
                if form['diarization'] and not speaker_panel.ready(form):cyui.callout('warning',tr('Install the selected speaker engine and model in Installation first.'))
                cyui.text_dim(tr('Phrase captions with original word timings.'))
                if not runtime_info['ready']:
                    cyui.callout('warning',tr('PyTorch is not installed. Open Installation to download it before generating subtitles.'))
                    if cyui.button(label('Installation')):view='Installation'
                with cyui.scoped_disabled(active or not runtime_info['ready'] or not form['media'] or (form['diarization'] and not speaker_panel.ready(form))):
                    if cyui.primary_button(label('Generate subtitles'),size=(-1,0)):submit('transcribe',dict(form))
                if cyui.button(label('All generation settings'),size=(-1,0)):view='Media & generation'
                cyui.end_card()
                cyui.begin_card('##selected-cue',tr('Selected caption'))
                if document and document['cues']:
                    cue=document['cues'][selected]
                    cyui.text_mono(f"{cue['start']:.3f} → {cue['end']:.3f}")
                    ui_common.raw().text_wrapped(speakers.display_text(document,cue))
                    if cyui.button(label('Edit caption and timing'),size=(-1,0)):view='Subtitle editor'
                else:cyui.text_faint(tr('Select a caption to inspect it.'))
                cyui.end_card()
                if wide:imgui.end_table()
            elif view=='Media & generation':
                cyui.begin_card('##generation',tr('Transcription settings'))
                if cyui.begin_properties('##media-source'):
                    cyui.property(tr('Audio / video file'));_,form['media']=imgui.input_text('##Audio / video file',form['media'])
                    cyui.end_properties()
                if cyui.button(label('Open media')):choose('media')
                imgui.same_line()
                if cyui.button(label('Load preview')) and form['media']:player.open(form['media'],form['audio_stream']);view='Workspace'
                models=["phonon-2","phonon-2.5","phonon-2.5-en"]
                if cyui.begin_properties("##props-Model"):
                    cyui.property(tr('Model'))
                    changed,index=imgui.combo("##Model",models.index(form["model"]),models)
                    if changed:form["model"]=models[index]
                    cyui.end_properties()
                imgui.text_wrapped(tr("Phonon-2: English. Phonon-2.5: multilingual including French. CPU inference; no GPU setup needed."))
                if cyui.begin_properties("##props-CPU threads"):
                    cyui.property(tr('CPU threads'))
                    _,form["threads"]=imgui.slider_int("##CPU threads",form["threads"],1,32)
                    cyui.end_properties()
                filters=["none","voice","denoise"]
                if cyui.begin_properties("##props-Audio filter"):
                    cyui.property(tr('Audio filter'))
                    changed,index=imgui.combo("##Audio filter",filters.index(form["filter"]),[tr("None"),tr("Voice band + denoise"),tr("Denoise")])
                    if changed:form["filter"]=filters[index]
                    cyui.end_properties()
                imgui.text_wrapped(tr("Voice filtering reduces noise; it does not isolate vocals from music."))
                if cyui.begin_section(label("Segmentation & layout")):

                    if cyui.begin_properties("##props-Window seconds"):
                        cyui.property(tr('Window seconds'))
                        _,form["chunk_seconds"]=imgui.slider_float("##Window seconds",form["chunk_seconds"],5,28)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Overlap seconds"):
                        cyui.property(tr('Overlap seconds'))
                        _,form["overlap_seconds"]=imgui.slider_float("##Overlap seconds",form["overlap_seconds"],.2,4)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Audio track (zero based)"):
                        cyui.property(tr('Audio track (zero based)'))
                        _,form["audio_stream"]=imgui.slider_int("##Audio track (zero based)",form["audio_stream"],0,31)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Characters per line"):
                        cyui.property(tr('Characters per line'))
                        _,form["max_chars"]=imgui.slider_int("##Characters per line",form["max_chars"],10,100)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Maximum lines"):
                        cyui.property(tr('Maximum lines'))
                        _,form["max_lines"]=imgui.slider_int("##Maximum lines",form["max_lines"],1,4)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Maximum cue seconds"):
                        cyui.property(tr('Maximum cue seconds'))
                        _,form["max_duration"]=imgui.slider_float("##Maximum cue seconds",form["max_duration"],.5,20)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Split at pause seconds"):
                        cyui.property(tr('Split at pause seconds'))
                        _,form["pause"]=imgui.slider_float("##Split at pause seconds",form["pause"],.1,5)
                        cyui.end_properties()
                    cyui.end_section()
                if cyui.begin_section(label('Reading comfort'),False):
                    if cyui.begin_properties("##props-Repair timing automatically"):
                        cyui.property(tr('Repair timing automatically'))
                        _,form["auto_timing"]=imgui.checkbox("##Repair timing automatically",form["auto_timing"])
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Reading characters per second"):
                        cyui.property(tr('Reading characters per second'))
                        _,form["max_cps"]=imgui.slider_float("##Reading characters per second",form["max_cps"],5,40)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Minimum display seconds"):
                        cyui.property(tr('Minimum display seconds'))
                        _,form["min_duration"]=imgui.slider_float("##Minimum display seconds",form["min_duration"],.2,3)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Maximum early shift seconds"):
                        cyui.property(tr('Maximum early shift seconds'))
                        _,form["max_advance"]=imgui.slider_float("##Maximum early shift seconds",form["max_advance"],0,1)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Maximum onset delay seconds"):
                        cyui.property(tr('Maximum onset delay seconds'))
                        _,form["max_delay"]=imgui.slider_float("##Maximum onset delay seconds",form["max_delay"],0,2)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Maximum end extension seconds"):
                        cyui.property(tr('Maximum end extension seconds'))
                        _,form["max_extension"]=imgui.slider_float("##Maximum end extension seconds",form["max_extension"],0,3)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Minimum caption gap seconds"):
                        cyui.property(tr('Minimum caption gap seconds'))
                        _,form["min_gap"]=imgui.slider_float("##Minimum caption gap seconds",form["min_gap"],0,.5)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Merge compatible fragments"):
                        cyui.property(tr('Merge compatible fragments'))
                        _,form["merge_fragments"]=imgui.checkbox("##Merge compatible fragments",form["merge_fragments"])
                        cyui.end_properties()
                    cyui.end_section()
                if cyui.begin_section(label('Model hints and local weights'),False):
                    if cyui.begin_properties("##props-Hotwords (comma separated)"):
                        cyui.property(tr('Hotwords (comma separated)'))
                        changed,text=imgui.input_text("##Hotwords (comma separated)",", ".join(form["hotwords"]))
                        if changed:form["hotwords"]=[x.strip() for x in text.split(",") if x.strip()]
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Hotword strength"):
                        cyui.property(tr('Hotword strength'))
                        _,form["hotword_lambda"]=imgui.slider_float("##Hotword strength",form["hotword_lambda"],0,10)
                        cyui.end_properties()
                    if cyui.begin_properties("##props-Optional local Phonon model folder"):
                        cyui.property(tr('Optional local Phonon model folder'))
                        _,form["local_model"]=imgui.input_text("##Optional local Phonon model folder",form["local_model"])
                        cyui.end_properties()
                    imgui.text_wrapped(tr("Local models are referenced in place. Only compatible Phonon-2 family directories; LoRA is not supported by this engine."))
                    cyui.end_section()
                if '--ui-test-nvidia-settings' in sys.argv:imgui.set_next_item_open(True,imgui.Cond_.always)
                if cyui.begin_section(label('Speaker identification'),False):
                    _,form['diarization']=imgui.checkbox('Identify different speakers',form['diarization'])
                    speaker_options(form)
                    if '--ui-test-nvidia-settings' in sys.argv and frames>3:imgui.set_scroll_here_y(.2)
                    if form['diarization'] and not speaker_panel.ready(form):cyui.callout('warning',tr('Install the selected speaker engine and model in Installation first.'))
                    cyui.end_section()
                with cyui.scoped_disabled(active or not runtime_info['ready'] or not form['media'] or (form['diarization'] and not speaker_panel.ready(form))):
                    if cyui.primary_button(label('Generate subtitles')):submit('transcribe',dict(form))
                imgui.same_line()
                with cyui.scoped_disabled(active or not form['media']):
                    if cyui.button(label('Inspect media')):submit('inspect_media',{'media':form['media'],'audio_stream':form['audio_stream'],'excerpt':True})
                if not runtime_info['ready']:cyui.callout('warning',tr('PyTorch is not installed. Open Installation to download it before generating subtitles.'))
                cyui.end_card()
                if '--ui-test-nvidia-settings' in sys.argv and frames>3:imgui.set_scroll_here_y(1.0)
            elif view=='Subtitle editor':
                if cyui.button(label("Open subtitle document")):choose("document")
                imgui.same_line()
                if cyui.button(label("Export folder")):choose("export")
                if cyui.begin_properties("##props-Export destination"):
                    cyui.property(tr('Export destination'))
                    _,export_folder=imgui.input_text("##Export destination",export_folder)
                    cyui.end_properties()
                imgui.begin_disabled(not subtitle_job or not export_folder)
                if cyui.button(label("Export SRT / VTT / JSON")):
                    future=pool.submit(runtime.export_job,actor,subtitle_job["jobId"],export_folder)
                imgui.end_disabled()
                if document:
                    imgui.begin_disabled(active)
                    if cyui.button(label("Save current subtitle bundle")):submit("edit_subtitles",{"document":document_path,"edits":[]})
                    imgui.end_disabled()
                    ui_common.raw().text_wrapped(document_path)
                    imgui.text(tr("Cues / timing warnings")+f': {len(document["cues"])} / {len(subtitles.quality(document))}')
                    if document.get("timingRepair",{}).get("state")=="Unresolved":imgui.text_wrapped(tr(document["timingRepair"]["error"]))
                    editor_wide=imgui.get_content_region_avail().x>cyui.dp(880)
                    if editor_wide:editor_wide=imgui.begin_table('##editor-columns',2,imgui.TableFlags_.resizable)
                    if editor_wide:
                        imgui.table_setup_column('captions',imgui.TableColumnFlags_.width_stretch,1.3)
                        imgui.table_setup_column('inspector',imgui.TableColumnFlags_.width_stretch,1)
                        imgui.table_next_column()
                    cyui.begin_card('##editor-captions',tr('Subtitles'))
                    history_buttons(active);imgui.same_line()
                    if cyui.button(label('Fit timeline')):timelines['##editor-timeline'].state.view=Range(0,max(10,player.duration,max((c['end'] for c in document['cues']),default=0)))
                    draw_timeline(active,'##editor-timeline',180)
                    if imgui.begin_child("cue-list",(0,cyui.dp(420 if editor_wide else 200))):
                        for i,cue in enumerate(document["cues"]):
                            clicked,_=imgui.selectable(f'{cue["start"]:.3f} -> {cue["end"]:.3f}  {speakers.display_text(document,cue).replace(chr(10)," ")}##{cue["id"]}',selected==i)
                            if clicked:select_cue(i);player.seek(cue["start"])
                    imgui.end_child()
                    cyui.end_card()
                    if editor_wide:imgui.table_next_column()
                    cyui.begin_card('##caption-inspector',tr('Caption inspector'))
                    if document["cues"]:
                        values=caption_inspector.draw('##cue-inspector',document['cues'][selected],{'start':cue_start,'end':cue_end,'text':cue_text,'kind':['Speech','Sound description'][cue_kind]},history.revision)
                        cue_start=values['start'];cue_end=values['end'];cue_text=values['text'];cue_kind=int(values['kind']=='Sound description')
                        if document.get('speakers') and cyui.begin_properties('##cue-speaker'):
                            cyui.property(tr('Speaker'))
                            ids=['']+[item['id'] for item in document['speakers']]
                            names=[tr('Unassigned')]+[item['name'] for item in document['speakers']]
                            changed,index=ui_common.raw().combo('##cue-speaker-choice',ids.index(cue_speaker) if cue_speaker in ids else 0,names)
                            if changed:cue_speaker=ids[index]
                            cyui.end_properties()
                        if len(document['cues'][selected].get('speakerCandidates',[]))>1:cyui.text_dim(tr('This caption spans more than one voice. Review the assignment or rebuild at speaker changes.'))
                        imgui.begin_disabled(active or bool(caption_inspector.state.errors))
                        if cyui.primary_button(label("Apply cue edit")):submit("edit_subtitles",{"document":document_path,"edits":[{"id":document["cues"][selected]["id"],"start":cue_start,"end":cue_end,"text":cue_text,"kind":["speech","sound"][cue_kind],**({"speaker":cue_speaker or None} if document.get("speakers") else {})}]})
                        imgui.same_line()
                        if cyui.danger_button(label("Delete cue")):submit("edit_subtitles",{"document":document_path,"edits":[{"id":document["cues"][selected]["id"],"delete":True}]})
                        imgui.end_disabled()
                    if cyui.begin_section(label('Track timing'),False):
                        if cyui.begin_properties("##props-Shift entire track seconds"):
                            cyui.property(tr('Shift entire track seconds'))
                            _,offset=imgui.input_double("##Shift entire track seconds",offset,.04,.2,"%.3f")
                            cyui.end_properties()
                        imgui.begin_disabled(active)
                        if cyui.button(label("Apply track shift")):submit("edit_subtitles",{"document":document_path,"offset_seconds":offset})
                        imgui.same_line()
                        if cyui.button(label("Rebuild layout from original words")):submit("reflow_subtitles",{"document":document_path,**{k:form[k] for k in ("max_chars","max_lines","max_duration","pause","auto_timing","max_cps","min_duration","max_advance","max_delay","max_extension","min_gap","merge_fragments")}})
                        if cyui.button(label("Repair reading time and overlaps")):repair_current()
                        imgui.end_disabled()
                        imgui.text_wrapped(tr("Repair preserves every word. Remaining fast-dialogue warnings require review within the chosen timing limits."))
                        cyui.end_section()
                    if cyui.begin_section(label('Sound descriptions'),False):
                        if cyui.begin_properties("##props-Sound description at playhead"):
                            cyui.property(tr('Sound description at playhead'))
                            _,sound_text=imgui.input_text("##Sound description at playhead",sound_text)
                            cyui.end_properties()
                        if cyui.begin_properties("##props-Sound caption duration"):
                            cyui.property(tr('Sound caption duration'))
                            _,sound_duration=imgui.slider_float("##Sound caption duration",sound_duration,.1,20)
                            cyui.end_properties()
                        imgui.begin_disabled(active or not sound_text.strip())
                        if cyui.button(label("Add sound description")):
                            import uuid
                            start=player.current_time();submit("edit_subtitles",{"document":document_path,"edits":[{"id":"sound-"+uuid.uuid4().hex[:12],"start":start,"end":start+sound_duration,"text":sound_text,"kind":"sound"}]})
                        imgui.end_disabled()
                        cyui.end_section()
                    speaker_panel.editor(document,document_path,form["media"],form,submit,active)
                    cyui.end_card()
                    if editor_wide:imgui.end_table()
                else:
                    cyui.empty_state(tr('No subtitle document'),tr('Generate subtitles or open a JSON subtitle document to start editing.'),cyui.icon.document)
            elif view=='Installation':
                cyui.begin_card('##installation',tr('Runtime and model installation'))
                if cyui.begin_properties('##install-model-choice'):
                    cyui.property(tr('Model'));models=['phonon-2','phonon-2.5','phonon-2.5-en']
                    changed,index=imgui.combo('##install-model',models.index(form['model']),models)
                    if changed:form['model']=models[index]
                    cyui.end_properties()
                imgui.text("PyTorch CPU "+runtime_info["expectedVersion"]);imgui.same_line();imgui.text(tr(runtime_info["state"]))
                imgui.text_wrapped(tr("PyTorch is downloaded separately and installed privately for this Tool. CPU inference only."))
                if cyui.button(label("PyTorch license and source")):
                    import webbrowser
                    webbrowser.open(runtime_components.LICENSE_URL)
                if cyui.begin_properties("##props-I reviewed the PyTorch license"):
                    cyui.property(tr('I reviewed the PyTorch license'))
                    _,runtime_accepted=imgui.checkbox("##I reviewed the PyTorch license",runtime_accepted)
                    cyui.end_properties()
                imgui.begin_disabled(active or not runtime_accepted)
                if cyui.button(label("Download / repair PyTorch")):submit("install_runtime",{"license_accepted":runtime_accepted,"repair":True})
                imgui.end_disabled()
                imgui.begin_disabled(active)
                if cyui.button(label("Check PyTorch installation")):submit("runtime_status",{})
                imgui.end_disabled()
                imgui.separator()
                imgui.text_wrapped(tr("Public model weights: CC-BY-4.0. Download size about 160 MB per model; expanded installation is larger. Downloads stay private to this Tool."))
                if cyui.button(label("Official model page")):
                    import webbrowser
                    repo={"phonon-2":"Phonon-2","phonon-2.5":"Phonon-2.5","phonon-2.5-en":"Phonon-2.5-English"}[form["model"]]
                    webbrowser.open("https://huggingface.co/FermionResearch/"+repo)
                if cyui.begin_properties("##props-I reviewed the model license"):
                    cyui.property(tr('I reviewed the model license'))
                    _,accepted=imgui.checkbox("##I reviewed the model license",accepted)
                    cyui.end_properties()
                imgui.text(tr("Selected model")+": "+form["model"])
                for key,value in model_records().items():imgui.text_wrapped(key+": "+value["path"])
                imgui.begin_disabled(active or not accepted)
                if cyui.button(label("Download / resume / repair model")):submit("install_model",{"model":form["model"],"license_accepted":accepted})
                imgui.end_disabled()
                if cyui.button(label("Check installation")):submit("model_status",{})
                if cyui.begin_properties("##props-Local model directory"):
                    cyui.property(tr('Local model directory'))
                    _,form["local_model"]=imgui.input_text("##Local model directory",form["local_model"])
                    cyui.end_properties()
                imgui.begin_disabled(active or not form["local_model"])
                if cyui.button(label("Register local model")):
                    submit("register_local_model",{"path":form["local_model"],"name":Path(form["local_model"]).name,"model":form["model"]})
                imgui.end_disabled()
                for ident,record in model_records().items():
                    if ident.startswith("local-") and imgui.button(record.get("name",ident)+"##"+ident):
                        form["local_model"]=record["path"];form["model"]=record.get("model","phonon-2")
                if model_status:imgui.text_wrapped(model_status)
                cyui.end_card()
                speaker_panel.installation(submit,active)
                if any(a in sys.argv for a in ("--ui-test-speaker-installation","--ui-test-nvidia-installation")) and frames>3:imgui.set_scroll_here_y(1.0)
            elif view=='Updates':
                cyui.begin_card('##updates',tr('GitHub updates'))
                imgui.text_wrapped(tr("Configure the application GitHub repository. No public repository is assumed. Engine updates require a new tested runtime; model downloads are separate."))
                if cyui.begin_properties("##props-GitHub owner/repository"):
                    cyui.property(tr('GitHub owner/repository'))
                    _,github=imgui.input_text("##GitHub owner/repository",github)
                    cyui.end_properties()
                if cyui.begin_properties("##props-Check updates at startup"):
                    cyui.property(tr('Check updates at startup'))
                    _,automatic=imgui.checkbox("##Check updates at startup",automatic)
                    cyui.end_properties()
                if cyui.button(label("Save update settings")):
                    try:updates.write_settings({"repository":github,"automaticCheck":automatic});message=tr("Saved")
                    except Exception as exc:message=str(exc)
                imgui.begin_disabled(future is not None or active)
                for action_label,action in (("Check updates",updates.check),("Download update",updates.download),("Restore previous version",updates.rollback)):
                    if imgui.button(action_label):future=pool.submit(action)
                    imgui.same_line()
                imgui.end_disabled();imgui.new_line()
                imgui.text_wrapped(tr("Updates activate on restart and preserve data. Releases contain app/ only, with a matching Tool ID and runtime ABI."))
                cyui.end_card()
            elif view=='Options':ui_common.options_panel()
            elif view=='Application log':ui_common.journal.draw_panel()
            elif view=='Advanced operations':ui_common._advanced_panel.draw_panel()
            if job and job['state']=='Completed' and job['operationId']=='inspect_media':
                imgui.input_text_multiline('Inspection result',json.dumps(job['outputs'],indent=2,ensure_ascii=False),(0,cyui.dp(120)),flags=imgui.InputTextFlags_.read_only)
            if drops.error:cyui.callout('warning',tr('File drop unavailable: ')+drops.error)
            if message:
                if cyui.begin_section(label('Last action result')):
                    imgui.input_text_multiline('##last-action',message,(0,cyui.dp(100)),flags=imgui.InputTextFlags_.read_only);cyui.end_section()
            commands=[Command(1,'Open media','Ctrl+O','Files'),Command(2,'Open subtitle document','Ctrl+Shift+O','Files'),Command(3,'Save current subtitle bundle','Ctrl+S','Files',bool(document) and not active),Command(4,'Load preview','Ctrl+R','Playback',bool(form['media'])),Command(5,'Play / pause','Space','Playback',bool(form['media'])),Command(6,'Undo','Ctrl+Z','Editing',history.can_undo and not active),Command(7,'Redo','Ctrl+Y','Editing',history.can_redo and not active),Command(8,'Workspace','','Views'),Command(9,'Subtitle editor','','Views'),Command(10,'Application log','','Views'),Command(11,'Options','','Views')]
            commands_open,requested=command_palette('Command palette',commands_open,command_state,commands)
            if requested==1:choose('media')
            elif requested==2:choose('document')
            elif requested==3:submit('edit_subtitles',{'document':document_path,'edits':[]})
            elif requested==4:player.open(form['media'],form['audio_stream'])
            elif requested==5:player.toggle()
            elif requested in (6,7):restore_history(-1 if requested==6 else 1)
            elif requested in (8,9,10,11):view={8:'Workspace',9:'Subtitle editor',10:'Application log',11:'Options'}[requested]
            imgui.end()
            if '--ui-test-modules-history' in sys.argv:
                if module_test_phase==2 and frames>35:runner.app_shall_exit=True
                elif time.monotonic()-test_started>30:raise RuntimeError('Module history UI test timed out')
            elif ('--smoke-test' in sys.argv or test_installation) and frames>20:runner.app_shall_exit=True
        configure_generation(runtime,lambda:{"operationId":"transcribe","parameters":dict(form)},lambda recipe:restore_form(form,recipe))
        runner.callbacks.show_gui=gui
        try:
            if automatic and github:future=pool.submit(updates.check)
            run(runner,shell=True)
            if '--ui-test-modules-history' in sys.argv:
                assert module_test_phase==2
                (ROOT/'data/reports/modules-history-ui.json').write_text(json.dumps({'phase':module_test_phase,'undoRedo':True,'transactions':len(history.versions)-1,'wordsPreserved':history.current.document.get('words')==history.versions[0].document.get('words')}),'utf-8')
            if test_nvidia_generate:
                from standalone_log import save_screenshot
                save_screenshot(ROOT/'data/reports/nvidia-generation.png',hello_imgui.final_app_window_screenshot())
                (ROOT/'data/reports/nvidia-generation-ui.json').write_text(json.dumps({'state':job['state'],'outputs':job['outputs'],'engine':document['diarization']['engine'],'device':document['diarization']['device'],'parameters':form}), 'utf-8')
            if test_speakers:
                from standalone_log import save_screenshot
                save_screenshot(ROOT/('data/reports/speakers-'+preferences.values['language']+'.png'),hello_imgui.final_app_window_screenshot())
                (ROOT/'data/reports/speakers-ui.json').write_text(json.dumps({'phase':speaker_test_phase,'speakers':document['speakers'],'cueSpeaker':document['cues'][0]['speaker'],'manual':document['cues'][0]['speakerManual']}),'utf-8')
            if test_media or test_drop:
                from standalone_log import save_screenshot
                frame=player.frame
                report={'media':form['media'],'dropCount':drop_count,'cueCount':len(document['cues']) if document else 0,'message':message,'dropError':drops.error,'renderedFrames':preview_frames,'sourcePixels':[player.width,player.height],'previewPixels':[frame.shape[1],frame.shape[0]] if frame is not None else None,'contiguous':bool(frame is not None and frame.flags.c_contiguous),'error':render_error or player.error,'played':test_played,'paused':test_paused}
                (ROOT/'data/reports/preview-input-test.json').write_text(json.dumps(report,indent=2),'utf-8')
                save_screenshot(ROOT/'data/reports/preview-input-test.png',hello_imgui.final_app_window_screenshot())
            if any(a.startswith('--ui-test-theme=') for a in sys.argv) or '--ui-test-view' in ' '.join(sys.argv):
                from standalone_log import save_screenshot
                name='cyui-'+preferences.values['theme']+'-'+preferences.values['language']+'-'+view.replace(' ','-')+'-'+preferences.values['density']+'.png'
                save_screenshot(ROOT/'data/reports'/name,hello_imgui.final_app_window_screenshot())
            if test_preview:
                from standalone_log import save_screenshot
                save_screenshot(ROOT/'data/reports/preview.png',hello_imgui.final_app_window_screenshot())
            if test_installation:
                from standalone_log import save_screenshot
                save_screenshot(ROOT/('data/reports/installation-'+preferences.values['language']+'.png'),hello_imgui.final_app_window_screenshot())
                (ROOT/'data/reports/installation-ui.json').write_text(json.dumps(runtime_info),'utf-8')
            if test_repair:
                assert job and job["state"]=="Completed",job
                assert not document["warnings"],document["warnings"]
                from standalone_log import save_screenshot
                save_screenshot(ROOT/('data/reports/repair-'+preferences.values['language']+'.png'),hello_imgui.final_app_window_screenshot())
                (ROOT/'data/reports/repair-ui.json').write_text(json.dumps({"state":job["state"],"cueCount":len(document["cues"]),"warnings":document["warnings"]}),'utf-8')
        finally:
            player.stop();pool.shutdown(wait=True,cancel_futures=True)


if __name__=="__main__":main()
