---
id: operation-edit-subtitles
title: edit_subtitles
description: Patch cue text/times by stable ID, add timed sound descriptions, delete cues or shift the track; creates a new bundle and preserves the original.
section: Reference
order: 200
parent: operations
revision: 35b617df296f3938
---

Patch cue text/times by stable ID, add timed sound descriptions, delete cues or shift the track; creates a new bundle and preserves the original.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `document` | `string` | Yes | Subtitle JSON. Absolute local paths accepted; automatically imported into the private task.  |
| `edits` | `array` | No | See the operation parameters. `default=[]` |
| `offset_seconds` | `number` | No | Signed cue-track offset in seconds; original word evidence is retained. `default=0`, `minimum=-86400`, `maximum=86400` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation edit_subtitles
```
