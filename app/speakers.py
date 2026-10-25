"""Speaker attribution over original timestamps; never infer new words or cue times."""
import copy
import math
from bisect import bisect_right


def validate_metadata(document):
    records=document.get("speakers",[])
    if not isinstance(records,list) or len(records)>32:raise ValueError("Invalid speaker list")
    ids=set()
    for record in records:
        if not isinstance(record,dict) or not isinstance(record.get("id"),str) or not record["id"] or len(record["id"])>64 or record["id"] in ids:raise ValueError("Invalid speaker identity")
        name=record.get("name")
        if not isinstance(name,str) or not name.strip() or len(name)>80 or any(ord(c)<32 for c in name):raise ValueError("Invalid speaker name")
        ids.add(record["id"])
    for cue in document.get("cues",[]):
        if cue.get("speaker") is not None and cue["speaker"] not in ids:raise ValueError("Unknown cue speaker")
        if "speakerManual" in cue and not isinstance(cue["speakerManual"],bool):raise ValueError("Invalid speaker override")
        candidates=cue.get('speakerCandidates',[])
        if not isinstance(candidates,list) or len(candidates)>32 or any(c not in ids for c in candidates):raise ValueError('Invalid speaker candidates')
        fraction=cue.get('speakerOverlapFraction',0.)
        if not isinstance(fraction,(int,float)) or isinstance(fraction,bool) or not math.isfinite(fraction) or not 0<=fraction<=1:raise ValueError('Invalid temporal speaker overlap')
    if "speakerLabels" in document and not isinstance(document["speakerLabels"],bool):raise ValueError("Invalid speaker label preference")
    info=document.get("diarization",{})
    if not isinstance(info,dict):raise ValueError("Invalid diarization metadata")
    for key in ("segments","exclusiveSegments"):
        previous_end=0.
        segments=info.get(key,[])
        if not isinstance(segments,list) or len(segments)>200000:raise ValueError("Invalid speaker timeline")
        for turn in segments:
            if not isinstance(turn,dict) or turn.get("speaker") not in ids:raise ValueError("Unknown timeline speaker")
            if not all(isinstance(turn.get(k),(int,float)) and not isinstance(turn[k],bool) and math.isfinite(turn[k]) for k in ("start","end")) or not 0<=turn["start"]<turn["end"]:raise ValueError("Invalid speaker timing")
            if key=="exclusiveSegments" and turn["start"]<previous_end-1e-6:raise ValueError("Exclusive speaker segments must be ordered and non-overlapping")
            previous_end=turn["end"]


def name_for(document,identifier):
    return next((s["name"] for s in document.get("speakers",[]) if s["id"]==identifier),"")


def display_text(document,cue):
    name=name_for(document,cue.get("speaker")) if document.get("speakerLabels",True) and cue.get("kind","speech")=="speech" else ""
    return f"[{name}] {cue['text']}" if name else cue["text"]


class Timeline(list):
    def __init__(self,segments):
        super().__init__(sorted(segments,key=lambda t:t['start']))
        self.ends=[turn['end'] for turn in self]


def attribution(start,end,segments,preferred=None):
    totals={}
    first=bisect_right(segments.ends,start) if isinstance(segments,Timeline) else 0
    for index in range(first,len(segments)):
        turn=segments[index]
        if turn["start"]>=end:break
        overlap=max(0.,min(end,turn["end"])-max(start,turn["start"]))
        if overlap:totals[turn["speaker"]]=totals.get(turn["speaker"],0.)+overlap
    if not totals:return None,0.,[]
    ranked=sorted(totals,key=lambda key:(-totals[key],key))
    chosen=ranked[0] if preferred is None else preferred
    return chosen,min(1.,totals.get(chosen,0.)/max(.001,end-start)),ranked


def label_cues(document,replace_manual=False):
    segments=Timeline(document.get("diarization",{}).get("exclusiveSegments",[]))
    for cue in document["cues"]:
        if cue.get("kind","speech")!="speech" or (cue.get("speakerManual") and not replace_manual):continue
        speaker,fraction,candidates=attribution(cue["start"],cue["end"],segments)
        cue["speaker"]=speaker or nearby_speaker(cue['start'],cue['end'],segments);cue["speakerOverlapFraction"]=round(fraction,4)
        cue["speakerCandidates"]=candidates
        cue["speakerManual"]=False
    return document


def nearby_speaker(start,end,segments,tolerance=.25):
    """Resolve small ASR/VAD boundary differences, never a long silent gap."""
    first=bisect_right(segments.ends,start) if isinstance(segments,Timeline) else 0
    candidates=segments[max(0,first-1):first+1]
    if not candidates:return None
    distance=lambda turn:max(0.,turn['start']-end,start-turn['end'])
    nearest=min(candidates,key=distance)
    return nearest['speaker'] if distance(nearest)<=tolerance else None


def attributed_words(document):
    import subtitles
    segments=Timeline(document.get("diarization",{}).get("exclusiveSegments",[]))
    words=document.get('words',[])
    evidence=[attribution(w['start'],max(w['end'],w['start']+.001),segments) for w in words]
    result=[]
    for index,word in enumerate(words):
        start,end=word['start'],max(word['end'],word['start']+.001)
        speaker,fraction,candidates=evidence[index]
        speaker=speaker or nearby_speaker(start,end,segments)
        # Keep weak mixed boundary evidence from creating a one-word speaker
        # change. A fully covered brief reply still establishes its own voice.
        if result and fraction<.6 and len(candidates)>1 and start-result[-1]['end']<=.65:
            previous=result[-1]['speaker']
            if previous in candidates and attribution(start,end,segments,preferred=previous)[1]>=.25:
                speaker=previous
        # A near-boundary fallback has no overlap evidence of its own. Prefer
        # the following well-covered word in the same unfinished phrase.
        if speaker is not None and fraction==0 and index+1<len(words) and not word['text'].endswith(('.', '?', '!')):
            following=words[index+1];following_speaker,coverage,_=evidence[index+1]
            if following_speaker and coverage>=.6 and following['start']-end<=.65:
                speaker=following_speaker
        # ASR often timestamps punctuation separately, after the voice ended.
        # A punctuation token cannot establish a new speaker identity.
        if result and subtitles.closing_punctuation(word['text']) and start-result[-1]['end']<=.65:
            speaker=result[-1]['speaker']
        result.append({**word,'speaker':speaker})
    return result


def attach(document,result,*,rebuild=False,layout_options=None,replace_manual=False):
    import subtitles
    changed=copy.deepcopy(subtitles.validate(document))
    existing={s["id"]:s["name"] for s in changed.get("speakers",[])}
    # Keep explicit names for the same source recording only.
    if changed.get("diarization",{}).get("mediaSha256")!=result.get("mediaSha256"):existing={}
    changed["speakers"]=[{**s,"name":existing.get(s["id"],s["name"])} for s in result["speakers"]]
    # Manual assignments must not refer to identities absent from a new analysis.
    valid={s["id"] for s in changed["speakers"]}
    for cue in changed["cues"]:
        if cue.get("speaker") not in valid:cue.pop("speaker",None);cue.pop("speakerManual",None)
        if "speakerCandidates" in cue:cue["speakerCandidates"]=[identifier for identifier in cue["speakerCandidates"] if identifier in valid]
    changed["diarization"]={k:copy.deepcopy(v) for k,v in result.items() if k!="speakers"}
    changed.setdefault("speakerLabels",True)
    if rebuild:
        sounds=[c for c in changed["cues"] if c.get("kind")=="sound"]
        changed["cues"]=subtitles.layout(attributed_words(changed),**(layout_options or {}))+sounds
        changed.pop("timingAnchors",None)
    label_cues(changed,replace_manual=replace_manual)
    changed.setdefault("history",[]).append({"action":"diarize","model":result["model"],"speakerCount":len(result["speakers"])})
    return subtitles.validate(changed)


def rename(document,names,show_labels=True):
    import subtitles
    result=copy.deepcopy(subtitles.validate(document));known={s["id"] for s in result.get("speakers",[])}
    if set(names)-known:raise ValueError("Unknown speaker ID")
    for record in result.get("speakers",[]):
        if record["id"] in names:record["name"]=names[record["id"]]
    result["speakerLabels"]=show_labels
    result.setdefault("history",[]).append({"action":"rename_speakers","count":len(names)})
    return subtitles.validate(result)
