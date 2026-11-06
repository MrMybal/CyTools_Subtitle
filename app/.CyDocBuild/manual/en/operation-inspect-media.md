---
id: operation-inspect-media
title: inspect_media
description: Read source streams and dimensions; optionally export a bounded WAV excerpt and waveform for listening and AI review.
section: Reference
order: 200
parent: operations
revision: 8c1b2cebea7ce23e
---

Read source streams and dimensions; optionally export a bounded WAV excerpt and waveform for listening and AI review.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `media` | `string` | Yes | Local audio/video. Absolute local paths accepted; automatically imported into the private task.  |
| `start` | `number` | No | Start time in seconds from media start. `default=0`, `minimum=0`, `maximum=86400` |
| `duration` | `number` | No | Audio excerpt duration in seconds, at most 120. `default=15`, `minimum=0.1`, `maximum=120` |
| `audio_stream` | `integer` | No | Zero-based audio-track ordinal, independent of the global stream index. `default=0`, `minimum=0`, `maximum=31` |
| `excerpt` | `boolean` | No | Write a bounded WAV excerpt for listening and a peak waveform. `default=true` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `durationSeconds` | `number` | Yes | See the operation parameters. `minimum=0` |
| `streams` | `array` | Yes | See the operation parameters.  |
| `excerpt` | `string` | No | Mono PCM WAV file.  |
| `excerptStartSeconds` | `number` | No | See the operation parameters.  |
| `waveform` | `array` | No | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation inspect_media
```
