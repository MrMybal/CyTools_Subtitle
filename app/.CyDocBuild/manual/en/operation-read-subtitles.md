---
id: operation-read-subtitles
title: read_subtitles
description: Read a paginated time range of cues and original word timings for AI correction.
section: Reference
order: 200
parent: operations
revision: 145200797a2e5d38
---

Read a paginated time range of cues and original word timings for AI correction.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `document` | `string` | Yes | Subtitle JSON. Absolute local paths accepted; automatically imported into the private task.  |
| `start` | `number` | No | Start time in seconds from media start. `default=0`, `minimum=0`, `maximum=86400` |
| `end` | `number` | No | Exclusive end time in seconds from media start. `default=86400`, `minimum=0.001`, `maximum=86400` |
| `offset` | `integer` | No | Pagination offset. `default=0`, `minimum=0`, `maximum=100000` |
| `limit` | `integer` | No | Maximum page size. `default=100`, `minimum=1`, `maximum=1000` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `cues` | `array` | Yes | See the operation parameters.  |
| `total` | `integer` | Yes | See the operation parameters.  |
| `words` | `array` | Yes | See the operation parameters.  |
| `totalWords` | `integer` | Yes | See the operation parameters.  |
| `warnings` | `array` | Yes | See the operation parameters.  |
| `speakers` | `array` | No | See the operation parameters.  |
| `speakerLabels` | `boolean` | No | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation read_subtitles
```
