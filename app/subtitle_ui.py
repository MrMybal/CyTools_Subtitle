"""Application-owned adapters for CyUI's media and subtitle views.

Decoding, subtitle validation, persistence and history stay in the Tool.
"""
from bisect import bisect_left, bisect_right
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import math

from cyui_modules.common import Range
from cyui_modules.timeline import Clip, Lane, TimelineState, timeline
from cyui_modules.inspector import Property, InspectorState, inspector
from cyui_modules.images import ImageData, ImageState, image_viewport
import subtitles


def stable_id(kind, value):
    return int.from_bytes(hashlib.blake2b((kind+':'+value).encode('utf-8'), digest_size=8).digest(),'big') or 1


@dataclass
class Version:
    document: dict
    path: str
    job: object = None
    size: int = 0


class DocumentHistory:
    """Retained job bundles form application Undo/Redo; never overwrite source files."""
    def __init__(self, capacity=40, max_bytes=32*1024*1024):
        self.capacity=capacity;self.max_bytes=max_bytes;self.versions=[];self.index=-1;self.revision=0

    def load(self, document, path, job=None, reset=False):
        value=subtitles.validate(deepcopy(document))
        size=len(json.dumps(value,ensure_ascii=False).encode('utf-8'))
        if reset:self.versions=[];self.index=-1
        if self.index>=0 and {k:v for k,v in self.versions[self.index].document.items() if k!='history'}=={k:v for k,v in value.items() if k!='history'}:
            # Saving an unchanged bundle still changes the current exportable job.
            self.versions[self.index]=Version(value,str(path),job,size);return
        self.versions=self.versions[:self.index+1]+[Version(value,str(path),job,size)]
        while len(self.versions)>1 and (len(self.versions)>self.capacity or sum(v.size for v in self.versions)>self.max_bytes):self.versions.pop(0)
        self.index=len(self.versions)-1;self.revision+=1

    @property
    def can_undo(self):return self.index>0
    @property
    def can_redo(self):return 0<=self.index<len(self.versions)-1
    @property
    def current(self):return self.versions[self.index] if self.index>=0 else None
    def move(self, direction):
        index=self.index+direction
        if not 0<=index<len(self.versions):return None
        self.index=index;self.revision+=1
        return self.current


class CaptionTimeline:
    def __init__(self):
        self.state=TimelineState();self.revision=-1;self.clips=[];self.lanes=[];self.by_id={};self.lane_values={};self.starts=[];self.ends=[]

    def prepare(self, document, revision, duration=0):
        if self.revision==revision:return
        first=self.revision<0;self.revision=revision;self.document=document
        duration=max(duration,document.get('media',{}).get('durationSeconds',0) or 0)
        self.lane_values={stable_id('lane','unassigned'):('speech',None),stable_id('lane','sound'):('sound',None)}
        self.lanes=[Lane(stable_id('lane','unassigned'),'Speech',36)]
        for speaker in document.get('speakers',[]):
            key=stable_id('speaker-lane',speaker['id']);self.lane_values[key]=('speech',speaker['id']);self.lanes.append(Lane(key,speaker['name'],36))
        self.lanes.append(Lane(stable_id('lane','sound'),'Sound descriptions',36))
        self.clips=[];self.by_id={}
        for cue in document['cues']:
            key=stable_id('cue',cue['id'])
            if key in self.by_id:raise ValueError('Subtitle timeline identity collision')
            self.by_id[key]=cue
            lane=stable_id('lane','sound') if cue.get('kind')=='sound' else stable_id('speaker-lane',cue['speaker']) if cue.get('speaker') else stable_id('lane','unassigned')
            if lane not in self.lane_values:lane=stable_id('lane','unassigned')
            self.clips.append(Clip(key,lane,cue['start'],cue['end']-cue['start'],'',self.lanes.index(next(l for l in self.lanes if l.id==lane))))
        self.starts=[c.start for c in self.clips];latest=0.;self.ends=[]
        for clip in self.clips:latest=max(latest,clip.start+clip.duration);self.ends.append(latest)
        self.state.selected=[key for key in self.state.selected if key in self.by_id]
        if first:self.state.view=Range(0,max(10,duration,max((c.start+c.duration for c in self.clips),default=0)))

    def visible(self):
        left=bisect_left(self.ends,self.state.view.minimum);right=bisect_right(self.starts,self.state.view.maximum)
        shown=self.clips[left:right]
        if len(shown)>3000:raise ValueError('Zoom in to edit this dense subtitle range (more than 3,000 visible captions).')
        return shown

    def patches(self, clips):
        result=[];seen=set()
        for clip in clips:
            if clip.id not in self.by_id or clip.id in seen:raise ValueError('Unknown or repeated timeline caption')
            seen.add(clip.id);cue=self.by_id[clip.id]
            start,end=round(clip.start,6),round(clip.start+clip.duration,6)
            if not all(math.isfinite(t) for t in (start,end)) or start<0 or end<=start:raise ValueError('Cue times must satisfy 0 <= start < end')
            if clip.lane not in self.lane_values:raise ValueError('Unknown timeline lane')
            kind,speaker=self.lane_values[clip.lane];patch={'id':cue['id']}
            if start!=cue['start']:patch['start']=start
            if end!=cue['end']:patch['end']=end
            if kind!=cue.get('kind','speech'):patch['kind']=kind
            if speaker!=cue.get('speaker'):patch['speaker']=speaker
            if len(patch)>1:result.append(patch)
        # The same domain validator used by MCP rejects the complete gesture atomically.
        subtitles.edit(self.document,result)
        return result

    def draw(self, identifier, document, revision, playhead, duration, selected, active=False, height=170):
        import cyui
        from ui_common import tr
        self.prepare(document,revision,duration)
        selected_id=stable_id('cue',selected) if selected else None
        if selected_id and self.state.mode==0 and selected_id not in self.state.selected:self.state.selected=[selected_id]
        lanes=[Lane(l.id,tr(l.label) if l.id in (stable_id('lane','unassigned'),stable_id('lane','sound')) else l.label,l.height) for l in self.lanes]
        def draw_caption(clip,rect):
            from imgui_bundle import imgui
            a,b=rect;cyui.clipped_text(imgui.get_window_draw_list(),(a[0]+cyui.dp(5),a[1]+cyui.dp(3)),max(0,b[0]-a[0]-cyui.dp(10)),cyui.palette().text,self.by_id[clip.id]['text'].replace('\n',' '))
        result=timeline(identifier,self.state,lanes,self.visible(),size=(0,cyui.dp(height)),playhead=playhead,snap_step=.01,revision=revision,read_only=active,format_time=lambda t:f'{t:.1f}s',draw_clip=draw_caption,min_duration=.04)
        return result


class CaptionInspector:
    def __init__(self):self.state=InspectorState();self.identity=None;self.revision=0
    def draw(self, identifier, cue, values, revision):
        if self.identity!=(cue['id'],revision):self.identity=(cue['id'],revision);self.revision+=1
        fields=['start','end','text','kind'];properties=[Property(1,'Start seconds',float(values['start']),minimum=0),Property(2,'End seconds',float(values['end']),minimum=.001),Property(3,'Caption',values['text'],multiline=True),Property(4,'Cue type',values['kind'],choices=('Speech','Sound description'))]
        def validate(key,value):
            from ui_common import tr
            draft={**values,**{fields[k-1]:v for k,v in self.state.drafts.items() if 1<=k<=4},fields[key-1]:value}
            if key in (1,2) and (not math.isfinite(value) or draft['end']<=draft['start']):return tr('Cue times must satisfy 0 <= start < end')
            if key==3 and (not value.strip() or len(value)>10000):return tr('Cue text is empty or too long')
            return ''
        for key,edit in inspector(identifier,self.state,properties,revision=self.revision,validate=validate):
            if edit.committed:values[fields[key-1]]=edit.value
        return values


class VideoSurface:
    """Own the bounded decoder frame's GPU texture until the backend shuts down."""
    def __init__(self):self.state=ImageState();self.frame=None;self.texture=None;self.retired=[];self.shape=None
    def close(self):self.frame=None;self.texture=None;self.retired.clear()
    def draw(self, frame, size, caption=''):
        import numpy as np
        import cyui
        from imgui_bundle import imgui,hello_imgui
        # Previous texture remains alive through its submitted frame.
        self.retired.clear()
        if frame is not self.frame:
            rgba=np.empty((*frame.shape[:2],4),dtype=np.uint8);rgba[:,:,:3]=frame;rgba[:,:,3]=255
            texture=hello_imgui.create_texture_gpu_from_rgba_data(rgba)
            if self.texture:self.retired.append(self.texture)
            self.texture=texture;self.frame=frame
            if self.shape!=frame.shape:self.shape=frame.shape;self.state.fit_pending=True
        origin=tuple(imgui.get_cursor_screen_pos())
        result=image_viewport('##video-surface',self.state,ImageData(self.texture.texture_id(),frame.shape[1],frame.shape[0]),size=size)
        if caption:
            measured=imgui.calc_text_size(caption);width,height=size;point=(origin[0]+(width-measured.x)/2,origin[1]+height-measured.y-cyui.dp(18));draw=imgui.get_window_draw_list();palette=cyui.palette()
            draw.push_clip_rect(origin,(origin[0]+width,origin[1]+height),True)
            draw.add_rect_filled((point[0]-cyui.dp(10),point[1]-cyui.dp(5)),(point[0]+measured.x+cyui.dp(10),point[1]+measured.y+cyui.dp(5)),cyui.alpha(palette.bg0,.94),cyui.dp(4));draw.add_text(point,palette.text,caption);draw.pop_clip_rect()
        return result
