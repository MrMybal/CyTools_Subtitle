---
id: operation-reflow-subtitles
title: reflow_subtitles
description: Rebuild readable cues from original word timestamps while preserving manually added sound descriptions. Manual speech text changes are replaced by original words.
section: Reference
order: 200
parent: operations
revision: 3ceb856787cdc7d0
---

Rebuild readable cues from original word timestamps while preserving manually added sound descriptions. Manual speech text changes are replaced by original words.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `document` | `string` | Yes | Subtitle JSON. Absolute local paths accepted; automatically imported into the private task.  |
| `max_chars` | `integer` | No | Maximum characters per line; long unbreakable words are preserved. `default=42`, `minimum=10`, `maximum=100` |
| `max_lines` | `integer` | No | Maximum lines per speech cue. `default=2`, `minimum=1`, `maximum=4` |
| `max_duration` | `number` | No | Target maximum speech cue duration in seconds; a single word is never split. `default=6`, `minimum=0.5`, `maximum=20` |
| `pause` | `number` | No | Split speech after a silence gap of at least this many seconds. `default=0.65`, `minimum=0.1`, `maximum=5` |
| `auto_timing` | `boolean` | No | Automatically repair reading time after transcription/reflow. Native word evidence stays unchanged; unresolved warnings remain visible. `default=true` |
| `max_cps` | `number` | No | Target maximum readable characters per second. Unavoidable violations remain reported. `default=22`, `minimum=5`, `maximum=40` |
| `min_duration` | `number` | No | Target minimum cue display duration in seconds, subject to synchronization limits. `default=0.8`, `minimum=0.2`, `maximum=3` |
| `max_advance` | `number` | No | Maximum seconds a caption may start early or end earlier than its source cue. `default=0.25`, `minimum=0`, `maximum=1` |
| `max_delay` | `number` | No | Maximum permitted delay of cue onset in seconds; never accumulated across the track. `default=0.5`, `minimum=0`, `maximum=2` |
| `max_extension` | `number` | No | Maximum seconds to extend a cue end, without overlapping another speech caption or exceeding media duration. `default=2`, `minimum=0`, `maximum=3` |
| `min_gap` | `number` | No | Minimum separation between speech captions in seconds. `default=0.04`, `minimum=0`, `maximum=0.5` |
| `merge_fragments` | `boolean` | No | Combine nearby short/fast/overlapping speech cues when the line and duration bounds permit; retain every word. `default=true` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `document` | `string` | Yes | Versioned subtitle JSON, cues and original word timings. Absolute local paths accepted; automatically imported into the private task.  |
| `srt` | `string` | Yes | UTF-8 SubRip subtitles. Absolute local paths accepted; automatically imported into the private task.  |
| `vtt` | `string` | Yes | UTF-8 WebVTT subtitles. Absolute local paths accepted; automatically imported into the private task.  |
| `cueCount` | `integer` | Yes | See the operation parameters.  |
| `warnings` | `array` | Yes | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation reflow_subtitles
```
