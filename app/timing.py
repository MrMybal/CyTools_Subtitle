"""Bounded subtitle timing repair. Original words stay immutable evidence."""
import copy
import math
import hashlib
import textwrap
import warnings

import subtitles


def _text(cue):
    return " ".join(cue["text"].split())


def _needs(cue, max_cps, min_duration):
    return max(min_duration, (len(cue.get("_speakerPrefix",""))+len(cue["text"].replace("\n", "")))/max_cps+.002)


def _merge(cues, max_cps, min_duration, max_chars, max_lines, max_duration, pause):
    result, sources = [], {}
    for original in cues:
        cue=copy.deepcopy(original)
        if cue.get("kind", "speech")!="speech":continue
        if result:
            previous=result[-1]
            text=_text(previous)+" "+_text(cue)
            lines=textwrap.wrap(text,max_chars,break_long_words=False,break_on_hyphens=False)
            gap=cue["start"]-previous["end"]
            span=max(previous["end"],cue["end"])-previous["start"]
            short=min(previous["end"]-previous["start"],cue["end"]-cue["start"])<min_duration
            fast=any(_needs(x,max_cps,min_duration)>x["end"]-x["start"]+.003 for x in (previous,cue))
            if previous.get("speaker")==cue.get("speaker") and previous.get("speakerManual",False)==cue.get("speakerManual",False) and gap<=pause and span<=max_duration and len(lines)<=max_lines and (gap<0 or short or fast):
                previous["text"]="\n".join(lines)
                previous["end"]=max(previous["end"],cue["end"])
                sources[previous["id"]].append(cue["id"])
                continue
        result.append(cue);sources[cue["id"]]=[cue["id"]]
    return result,sources


def _solve(cues, max_cps, min_duration, max_advance, max_delay, max_extension, min_gap, media_end, next_start=None):
    # LP slack measures unmet reading time. It never relaxes synchronization bounds.
    import numpy as np
    from scipy.optimize import linprog, OptimizeWarning
    from scipy.sparse import coo_matrix
    count=len(cues);rows=[];cols=[];data=[];rhs=[]
    def constraint(coefficients, upper):
        row=len(rhs);rhs.append(upper)
        for column,value in coefficients.items():rows.append(row);cols.append(column);data.append(value)
    objective=np.zeros(7*count);bounds=[]
    for i,cue in enumerate(cues):
        start,end=cue["start"],cue["end"];base=7*i
        objective[base+2]=1000
        objective[base+3:base+7]=1
        lower_end=max(start+.04,end-max_advance)
        upper_end=min(end+max_extension,media_end)
        if i==count-1 and next_start is not None:upper_end=min(upper_end,next_start-max_advance-min_gap)
        bounds.extend([(max(0,start-max_advance),min(start+max_delay,media_end-.04)),(lower_end,upper_end),(0,None),(0,None),(0,None),(0,None),(0,None)])
        constraint({base:1,base+1:-1,base+2:-1},-_needs(cue,max_cps,min_duration))
        constraint({base:1,base+1:-1},-.04)
        # Absolute deviations prefer original timing when an equivalent solution exists.
        constraint({base:1,base+3:-1,base+4:1},start)
        constraint({base:-1,base+3:1,base+4:-1},-start)
        constraint({base+1:1,base+5:-1,base+6:1},end)
        constraint({base+1:-1,base+5:1,base+6:-1},-end)
        if i+1<count:constraint({base+1:1,base+7:-1},-min_gap)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",message="Unrecognized options detected.*",category=OptimizeWarning)
        solution=linprog(objective,A_ub=coo_matrix((data,(rows,cols)),shape=(len(rhs),7*count)).tocsr(),b_ub=rhs,bounds=bounds,method="highs",options={"time_limit":15,"threads":1})
    if not solution.success:
        raise ValueError("Timing repair cannot satisfy the synchronization limits; original document preserved")
    result=[]
    for i,cue in enumerate(cues):
        changed=dict(cue)
        changed["start"]=round(float(solution.x[7*i]),3)
        changed["end"]=round(float(solution.x[7*i+1]),3)
        result.append(changed)
    return result


def repair(document, max_cps=22., min_duration=.8, max_advance=.25, max_delay=.5,
           max_extension=2., min_gap=.04, max_chars=42, max_lines=2,
           max_duration=6., pause=.65, merge_fragments=True):
    original=copy.deepcopy(document);subtitles.validate(original)
    policy={"max_cps":max_cps,"min_duration":min_duration,"max_advance":max_advance,
            "max_delay":max_delay,"max_extension":max_extension,"min_gap":min_gap,
            "max_chars":max_chars,"max_lines":max_lines,"max_duration":max_duration,
            "pause":pause,"merge_fragments":merge_fragments}
    sounds=[dict(c) for c in original["cues"] if c.get("kind")=="sound"]
    speech=[dict(c) for c in original["cues"] if c.get("kind","speech")=="speech"]
    import speakers
    for cue in speech:
        name=speakers.name_for(original,cue.get("speaker")) if original.get("speakerLabels",True) else ""
        cue["_speakerPrefix"]=("["+name+"] ") if name else ""
    previous_anchors=original.get("timingAnchors",{})
    for cue in speech:
        anchor=previous_anchors.get(cue["id"],{})
        fingerprint=hashlib.sha256(_text(cue).encode("utf-8")).hexdigest()
        if anchor.get("textSha256")==fingerprint and abs(cue["start"]-anchor.get("lastStart",-1))<.0011 and abs(cue["end"]-anchor.get("lastEnd",-1))<.0011:
            cue["start"],cue["end"]=anchor["start"],anchor["end"]
    anchor_by_id={c["id"]:dict(c) for c in speech}
    if merge_fragments:
        cues,sources=_merge(speech,max_cps,min_duration,max_chars,max_lines,max_duration,pause)
    else:cues=speech;sources={c["id"]:[c["id"]] for c in cues}
    duration=original.get("media",{}).get("durationSeconds")
    media_end=float(duration) if isinstance(duration,(int,float)) and math.isfinite(duration) and duration>0 else max((c["end"] for c in original["cues"]),default=0)+max_extension
    repaired=[]
    # Bound solver allocation per contiguous group; distant pauses need no shared budget.
    first=0
    while first<len(cues):
        last=first+1
        while last<len(cues) and last-first<256:
            if cues[last]["start"]-cues[last-1]["end"]>max_extension+max_advance+max_delay+min_gap:break
            last+=1
        next_start=cues[last]["start"] if last<len(cues) else None
        repaired.extend(_solve(cues[first:last],max_cps,min_duration,max_advance,max_delay,max_extension,min_gap,media_end,next_start))
        first=last
    for cue in repaired:cue.pop("_speakerPrefix",None)
    original_by_id={c["id"]:c for c in original["cues"]}
    changes=[];anchors={}
    for cue in repaired:
        ids=sources[cue["id"]]
        anchor_start=anchor_by_id[ids[0]]["start"]
        anchor_end=max(anchor_by_id[i]["end"] for i in ids)
        anchors[cue["id"]]={"start":anchor_start,"end":anchor_end,"lastStart":cue["start"],"lastEnd":cue["end"],"textSha256":hashlib.sha256(_text(cue).encode("utf-8")).hexdigest()}
        if len(ids)>1 or any(cue[k]!=original_by_id[cue["id"]][k] for k in ("start","end","text")):
            changes.append({"cueId":cue["id"],"sourceCueIds":ids,"beforeStart":anchor_start,"beforeEnd":anchor_end,"start":cue["start"],"end":cue["end"]})
    result=copy.deepcopy(original);result["cues"]=repaired+sounds
    result["timingPolicy"]=policy
    result["timingAnchors"]=anchors
    result["timingRepair"]={"inputCueCount":len(original["cues"]),"outputCueCount":len(result["cues"]),
                            "beforeWarnings":subtitles.quality(original,max_cps),"changes":changes}
    result.setdefault("history",[]).append({"action":"repair_timing","policy":policy})
    subtitles.validate(result)
    result["warnings"]=subtitles.quality(result,max_cps)
    result["timingRepair"]["afterWarnings"]=result["warnings"]
    return result
