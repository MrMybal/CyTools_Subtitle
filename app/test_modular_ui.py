"""Tool adapters tested against real CyUI ImGui frames and existing SDK operations."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pytest
import subtitles
from subtitle_ui import CaptionTimeline, CaptionInspector, DocumentHistory, stable_id


def sample():
    return {'format':'cytools-subtitles','schemaVersion':1,'words':[{'start':1.,'end':2.,'text':'Hello'}], 'cues':[{'id':'caption-a','start':1.,'end':3.,'text':'Hello there.','kind':'speech'},{'id':'caption-b','start':4.,'end':5.,'text':'[Door closes]','kind':'sound'}]}


def test_vendored_modules_are_exact_and_selective():
    app=Path(__file__).parent;pin=json.loads((app/'cyui-source.json').read_text('utf-8'))
    assert len(pin['revision'])==40 and not pin['modifications']
    for relative,digest in pin['files'].items():assert hashlib.sha256((app/relative).read_bytes()).hexdigest()==digest
    assert {p.name for p in (app/'cyui_modules').glob('*.py')}=={Path(k).name for k in pin['files'] if k.startswith('cyui_modules/')}
    assert not (app/'cyui_modules/cef.py').exists() and not (app/'cyui_modules/nodes.py').exists()


def test_model_imports_do_not_load_ui_ml_or_decoder():
    code="import subtitle_ui,sys;assert not any(k in sys.modules for k in ('imgui_bundle','torch','av','numpy'))"
    subprocess.run([sys.executable,'-c',code],check=True,creationflags=0x08000000 if sys.platform=='win32' else 0)


def test_history_branching_budgets_and_immutable_words():
    original=sample();before=deepcopy(original);history=DocumentHistory(capacity=3)
    history.load(original,'original.json',reset=True)
    for offset in (.1,.2,.3):history.load(subtitles.edit(original,[{'id':'caption-a','start':1+offset}]),str(offset)+'.json')
    assert len(history.versions)==3 and history.can_undo
    history.move(-1);assert history.current.document['cues'][0]['start']==1.2
    history.move(1);assert history.current.document['cues'][0]['start']==1.3
    history.move(-1);history.load(subtitles.edit(original,[{'id':'caption-a','text':'Changed'}]),'branch.json')
    assert not history.can_redo and history.current.document['words']==original['words'] and original==before
    tiny=DocumentHistory(max_bytes=1);tiny.load(original,'one');tiny.load(subtitles.edit(original,[{'id':'caption-a','text':'Two'}]),'two');assert len(tiny.versions)==1


def test_multi_caption_gesture_is_atomic_and_cross_lane_is_explicit():
    doc=sample();timeline=CaptionTimeline();timeline.prepare(doc,1)
    moved=[replace(c,start=c.start+.5) for c in timeline.clips];patches=timeline.patches(moved)
    assert len(patches)==2 and doc==sample()
    changed=subtitles.edit(doc,patches);assert changed['words']==doc['words'] and changed['cues'][0]['start']==1.5
    broken=[moved[0],replace(moved[1],start=-1.)]
    with pytest.raises(ValueError):timeline.patches(broken)
    assert doc==sample()
    sound=replace(timeline.clips[0],lane=stable_id('lane','sound'))
    assert timeline.patches([sound])==[{'id':'caption-a','kind':'sound'}]


@pytest.fixture
def gui():
    from imgui_bundle import imgui as i
    import cyui as c
    context=i.create_context();io=i.get_io();io.display_size=(1000,800);io.delta_time=1/60;io.set_ini_filename('');io.backend_flags|=i.BackendFlags_.renderer_has_textures;c.apply()
    def frame(draw,position=(-100,-100),button=None,key=None):
        io.add_mouse_pos_event(*position)
        if button is not None:io.add_mouse_button_event(*button)
        if key is not None:io.add_key_event(key,True)
        i.new_frame();i.set_next_window_pos((0,0));i.set_next_window_size((1000,800));i.begin('Adapter test',None,i.WindowFlags_.no_title_bar|i.WindowFlags_.no_saved_settings|i.WindowFlags_.no_move);i.set_cursor_screen_pos((20,20))
        result=draw();i.dummy((0,0));i.end();i.render()
        if key is not None:io.add_key_event(key,False)
        return result
    yield i,c,frame
    i.destroy_context(context)


@pytest.mark.parametrize('action',['move','trim','escape','revision'])
def test_real_timeline_gestures_are_proposals(gui,action):
    i,c,frame=gui;doc=sample();adapter=CaptionTimeline();revision=[1]
    draw=lambda:adapter.draw('timeline',doc,revision[0],0,10,None,height=180)
    available=frame(lambda:i.get_content_region_avail().x)
    frame(draw);frame(draw)
    x=lambda t:170+(available-150)*t/10
    y=20+i.get_frame_height()+18
    start=(x(3)-2,y) if action=='trim' else (x(2),y)
    frame(draw,start)
    begin=frame(draw,start,(0,True));assert begin['clips'].phase=='begin'
    update=frame(draw,(start[0]+(available-150)/10,y));assert update['clips'].phase=='update'
    assert doc==sample()
    if action=='escape':
        cancelled=frame(draw,(start[0]+(available-150)/10,y),key=i.Key.escape);assert cancelled['clips'].phase=='cancel'
        frame(draw,(start[0]+(available-150)/10,y),(0,False));assert doc==sample();return
    if action=='revision':
        revision[0]+=1;cancelled=frame(draw,(start[0]+(available-150)/10,y));assert cancelled['clips'].phase=='cancel'
        frame(draw,(start[0]+(available-150)/10,y),(0,False));assert doc==sample();return
    commit=frame(draw,(start[0]+(available-150)/10,y),(0,False));assert commit['clips'].committed
    patches=adapter.patches(commit['clips'].value);changed=subtitles.edit(doc,patches)
    assert len(patches)==1 and changed['cues'][0]['end']==pytest.approx(4.,abs=.011)
    assert changed['cues'][0]['start']==pytest.approx(1. if action=='trim' else 2.,abs=.011)
    history=DocumentHistory();history.load(doc,'before');history.load(changed,'after');assert len(history.versions)==2
    assert history.move(-1).document==doc and history.move(1).document==changed


def test_inspector_cancel_and_revision_preserve_host_draft(gui):
    i,c,frame=gui;adapter=CaptionInspector();doc=sample();values={'start':1.,'end':3.,'text':'Hello there.','kind':'Speech'}
    draw=lambda:adapter.draw('inspect',doc['cues'][0],values,1)
    frame(draw);frame(draw)
    point=(90,20+i.get_text_line_height()+i.get_style().item_spacing.y+i.get_frame_height()/2)
    frame(draw,point);frame(draw,point,(0,True));frame(draw,point,(0,False))
    assert 1 in adapter.state.active
    frame(draw,point,key=i.Key.escape);assert not adapter.state.active and values['start']==1.
    adapter.state.active.add(1);adapter.state.before[1]=1.;adapter.state.drafts[1]=2.
    frame(lambda:adapter.draw('inspect',doc['cues'][0],values,2));assert not adapter.state.active and values['start']==1.


def test_common_palette_keyboard_and_localization(gui):
    i,c,frame=gui
    from cyui_modules.commands import Command,CommandState,command_palette
    from cyui_modules.locale import locale_scope
    state=CommandState();commands=[Command(1,'Save'),Command(2,'Open',enabled=False)]
    draw=lambda:command_palette('Commands',True,state,commands)
    frame(draw);frame(draw)
    assert frame(draw,key=i.Key.enter)==(False,1)
    english=frame(lambda:i.get_id(c.tr_label('Save')))
    with locale_scope('fr'):assert frame(lambda:i.get_id(c.tr_label('Save')))==english


@pytest.mark.parametrize('theme,density,dpi',[('mid-grey','compact',1.),('light-grey','comfortable',1.5),('amber-night','compact',2.),('violet','comfortable',1.25),('navy','compact',1.5)])
def test_modules_render_with_scaled_theme_metrics(gui,theme,density,dpi):
    i,c,frame=gui;c.apply(theme,density,dpi)
    assert c.dp(20)==pytest.approx(20*dpi)
    adapter=CaptionTimeline();doc=sample()
    frame(lambda:adapter.draw('scaled-timeline',doc,1,1,10,None,height=120))
    properties=CaptionInspector();values={'start':1.,'end':3.,'text':'Hello','kind':'Speech'}
    frame(lambda:properties.draw('scaled-inspector',doc['cues'][0],values,1))
    assert doc==sample()



def test_noop_save_and_speaker_names_do_not_create_identity_conflicts():
    doc=sample();doc['speakers']=[{'id':'sound','name':'Sound'}];doc['cues'][0]['speaker']='sound'
    timeline=CaptionTimeline();timeline.prepare(doc,1)
    assert timeline.clips[0].lane!=timeline.clips[1].lane
    history=DocumentHistory();history.load(doc,'original')
    saved=deepcopy(doc);saved['history']=[{'action':'edit','count':0}];history.load(saved,'saved',job={'jobId':'new'})
    assert len(history.versions)==1 and history.current.path=='saved' and history.current.job['jobId']=='new'
