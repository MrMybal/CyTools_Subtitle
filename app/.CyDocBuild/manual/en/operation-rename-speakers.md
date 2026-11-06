---
id: operation-rename-speakers
title: rename_speakers
description: Rename speaker display names and toggle labels without altering words, cue text or timing.
section: Reference
order: 200
parent: operations
revision: d2dc5c46b3a114e3
---

Rename speaker display names and toggle labels without altering words, cue text or timing.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `document` | `string` | Yes | Subtitle JSON with speaker registry. Absolute local paths are automatically imported privately.  |
| `names` | `object` | Yes | See the operation parameters.  |
| `show_labels` | `boolean` | No | See the operation parameters. `default=true` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation rename_speakers
```
