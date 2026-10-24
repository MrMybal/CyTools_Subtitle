"""Subtitle documents, layout and interchange; times are media-relative seconds."""
import copy
import json
import math
import textwrap


def validate(document):
    if document.get("format") != "cytools-subtitles" or document.get("schemaVersion") != 1:
        raise ValueError("Unsupported subtitle document")
    if not isinstance(document.get("cues"), list) or len(document["cues"]) > 100000:
        raise ValueError("Invalid cue list")
    policy=document.get("timingPolicy",{})
    if not isinstance(policy,dict):raise ValueError("Invalid timing policy")
    max_cps=policy.get("max_cps",22)
    if not isinstance(max_cps,(int,float)) or isinstance(max_cps,bool) or not math.isfinite(max_cps) or not 5<=max_cps<=40:raise ValueError("Invalid reading speed policy")
    anchors=document.get("timingAnchors",{})
    if not isinstance(anchors,dict):raise ValueError("Invalid timing anchors")
    for anchor in anchors.values():
        if not isinstance(anchor,dict) or not all(isinstance(anchor.get(k),(int,float)) and not isinstance(anchor.get(k),bool) and math.isfinite(anchor[k]) for k in ("start","end","lastStart","lastEnd")) or anchor["start"]<0 or anchor["end"]<=anchor["start"]:raise ValueError("Invalid timing anchors")
    words=document.get("words",[])
    if not isinstance(words,list) or len(words)>1000000:raise ValueError("Invalid word list")
    for word in words:
        if not isinstance(word.get("text"),str) or not word["text"].strip():raise ValueError("Invalid word text")
        start,end=word.get("start"),word.get("end")
        if not all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in (start,end)) or start<0 or end<start:raise ValueError("Invalid word timing")
    ids = set()
    for cue in document["cues"]:
        if not isinstance(cue.get("id"), str) or cue["id"] in ids:
            raise ValueError("Cue IDs must be unique strings")
        ids.add(cue["id"])
        start, end = cue["start"], cue["end"]
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (start, end)) or start < 0 or end <= start:
            raise ValueError("Cue times must satisfy 0 <= start < end")
        if not isinstance(cue["text"], str) or not cue["text"].strip() or len(cue["text"]) > 10000:
            raise ValueError("Cue text is empty or too long")
        if cue.get("kind", "speech") not in ("speech", "sound"):
            raise ValueError("Unknown cue kind")
    document["cues"].sort(key=lambda c: (c["start"], c["end"], c["id"]))
    return document


def layout(words, max_chars=42, max_lines=2, max_duration=6.0, pause=.65):
    cues, group = [], []
    def emit():
        if not group: return
        text = " ".join(w["text"] for w in group)
        cues.append({"id": f"cue-{len(cues)+1:06d}", "start": group[0]["start"],
                     "end": max(group[-1]["end"], group[0]["start"]+.04),
                     "text": "\n".join(textwrap.wrap(text, max_chars, break_long_words=False, break_on_hyphens=False)), "kind": "speech"})
        group.clear()
    for word in words:
        if group:
            candidate = " ".join(w["text"] for w in [*group, word])
            lines = textwrap.wrap(candidate, max_chars, break_long_words=False, break_on_hyphens=False)
            if word["start"]-group[-1]["end"] >= pause or word["end"]-group[0]["start"] > max_duration or len(lines)>max_lines:
                emit()
        group.append(word)
        if word["text"].endswith((".", "?", "!")): emit()
    emit()
    return cues


def timestamp(seconds, separator=","):
    ms = max(0, round(seconds*1000))
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{ms:03}"


def quality(document, max_cps=None):
    if max_cps is None:max_cps=document.get("timingPolicy",{}).get("max_cps",22)
    warnings, speech_end = [], 0.0
    for cue in document["cues"]:
        duration = cue["end"]-cue["start"]
        if len(cue["text"].replace("\n", "")) / duration > max_cps:
            warnings.append({"cueId": cue["id"], "issue": "reading_speed", "seconds": duration})
        if cue.get("kind", "speech") == "speech":
            if cue["start"] < speech_end-.001:
                warnings.append({"cueId": cue["id"], "issue": "speech_overlap"})
            speech_end = max(speech_end, cue["end"])
    return warnings


def save(document, directory):
    validate(document)
    directory.mkdir(parents=True, exist_ok=True)
    paths = {}
    for extension in ("srt", "vtt"):
        blocks = []
        for i, cue in enumerate(document["cues"], 1):
            sep = "," if extension == "srt" else "."
            text = cue["text"].replace("-->", "→").replace("<", "‹").replace(">", "›")
            blocks.append(f'{i}\n{timestamp(cue["start"], sep)} --> {timestamp(cue["end"], sep)}\n{text}\n')
        path = directory/f"subtitles.{extension}"
        path.write_text(("WEBVTT\n\n" if extension=="vtt" else "")+"\n".join(blocks), encoding="utf-8")
        paths[extension] = str(path)
    document["warnings"] = quality(document)
    path = directory/"subtitles.json"
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False), "utf-8")
    paths["document"] = str(path)
    return {**paths, "cueCount": len(document["cues"]), "warnings": document["warnings"]}


def edit(document, edits, offset=0.0):
    result = copy.deepcopy(validate(document))
    by_id = {c["id"]: c for c in result["cues"]}
    for change in edits:
        ident = change["id"]
        if change.get("delete"):
            if ident not in by_id: raise ValueError("Unknown cue ID: "+ident)
            del by_id[ident]
        else:
            if ident not in by_id and not all(k in change for k in ("start", "end", "text")):
                raise ValueError("New cues require start, end and text")
            cue = by_id.setdefault(ident, {"id": ident, "kind": "sound"})
            cue.update({k: v for k,v in change.items() if k in ("start","end","text","kind")})
    result["cues"] = list(by_id.values())
    for cue in result["cues"]:
        cue["start"] += offset
        cue["end"] += offset
    result.setdefault("history", []).append({"action":"edit", "count":len(edits), "offsetSeconds":offset})
    return validate(result)
