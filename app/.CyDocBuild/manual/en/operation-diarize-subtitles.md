---
id: operation-diarize-subtitles
title: diarize_subtitles
description: Analyze voices globally with the selected local speaker engine and attach identities to a new subtitle bundle. Raw words and sound captions are preserved.
section: Reference
order: 200
parent: operations
revision: 363a58e9277679bf
---

Analyze voices globally with the selected local speaker engine and attach identities to a new subtitle bundle. Raw words and sound captions are preserved.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `media` | `string` | Yes | Source audio/video used for these subtitles. Absolute local paths are automatically imported privately.  |
| `document` | `string` | Yes | Existing subtitle JSON; manual text and times are preserved unless rebuild is explicitly true. Absolute local paths are automatically imported privately.  |
| `audio_stream` | `integer` | No | Zero-based audio-track ordinal, independent of the global stream index. `default=0`, `minimum=0`, `maximum=31` |
| `threads` | `integer` | No | Phonon/Community-1 CPU threads; NVIDIA limits its worker and inherited native process to this many logical CPUs. `default=4`, `minimum=1`, `maximum=32` |
| `speaker_count` | `integer` | No | Known number of voices; 0 enables automatic counting and min/max bounds. Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=0`, `minimum=0`, `maximum=32` |
| `min_speakers` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=1`, `minimum=1`, `maximum=32` |
| `max_speakers` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=16`, `minimum=1`, `maximum=32` |
| `diarization_max_seconds` | `integer` | No | Refuse longer audio before diarization; this is a processing bound, not an accuracy or performance guarantee. `default=14400`, `minimum=1`, `maximum=14400` |
| `segmentation_batch_size` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=1`, `minimum=1`, `maximum=16` |
| `embedding_batch_size` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=8`, `minimum=1`, `maximum=64` |
| `speaker_labels` | `boolean` | No | Include speaker display names in preview and SRT/VTT without changing cue text. `default=true` |
| `rebuild` | `boolean` | No | Rebuild speech from original word timings, splitting at voice changes. Replaces manual speech text/layout. `default=false` |
| `replace_manual` | `boolean` | No | Replace manually assigned cue speakers. `default=false` |
| `max_chars` | `integer` | No | Maximum characters per line; long unbreakable words are preserved. `default=42`, `minimum=10`, `maximum=100` |
| `max_lines` | `integer` | No | Maximum lines per speech cue. `default=2`, `minimum=1`, `maximum=4` |
| `max_duration` | `number` | No | Target maximum speech cue duration in seconds; a single word is never split. `default=6`, `minimum=0.5`, `maximum=20` |
| `pause` | `number` | No | Split speech after a silence gap of at least this many seconds. `default=0.65`, `minimum=0.1`, `maximum=5` |
| `diarization_engine` | `string` | No | Optional speaker analysis engine; Phonon remains the text/timing engine. `default="community1"`, `enum=["community1", "nemotron3"]` |
| `nemotron_device` | `string` | No | NVIDIA analysis device. CUDA means native CUDA device 0; no silent CPU fallback. `default="cpu"`, `enum=["cpu", "cuda"]` |
| `nemotron_mode` | `string` | No | Stateful chunked inference keeps global identities; full attention refuses audio over 360 seconds. `default="chunked"`, `enum=["chunked", "full"]` |
| `nemotron_preset` | `string` | No | Quality-oriented chunked geometry, low-latency geometry, or explicit custom geometry. Full attention requires the default sentinel. `default="v3-offline"`, `enum=["v3-offline", "v3-streaming", "custom"]` |
| `nemotron_chunk` | `integer` | No | Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default. `default=340`, `minimum=1`, `maximum=1024` |
| `nemotron_right_context` | `integer` | No | Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default. `default=40`, `minimum=0`, `maximum=1024` |
| `nemotron_left_context` | `integer` | No | Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default. `default=-1`, `minimum=-1`, `maximum=1024` |
| `nemotron_fifo` | `integer` | No | Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default. `default=40`, `minimum=0`, `maximum=1024` |
| `nemotron_spkcache` | `integer` | No | Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default. `default=264`, `minimum=1`, `maximum=1024` |
| `nemotron_update_period` | `integer` | No | Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default. `default=300`, `minimum=1`, `maximum=1024` |
| `nemotron_onset` | `number` | No | Native NVIDIA onset probability. `default=0.641`, `minimum=0.001`, `maximum=1` |
| `nemotron_offset` | `number` | No | Native NVIDIA offset probability. `default=0.561`, `minimum=0.001`, `maximum=1` |
| `nemotron_pad_onset` | `number` | No | Native NVIDIA pad onset in seconds; zero is preserved. `default=0.229`, `minimum=0`, `maximum=2` |
| `nemotron_pad_offset` | `number` | No | Native NVIDIA pad offset in seconds; zero is preserved. `default=0.079`, `minimum=0`, `maximum=2` |
| `nemotron_min_duration_on` | `number` | No | Native NVIDIA min duration on in seconds; zero is preserved. `default=0.511`, `minimum=0`, `maximum=2` |
| `nemotron_min_duration_off` | `number` | No | Native NVIDIA min duration off in seconds; zero is preserved. `default=0.296`, `minimum=0`, `maximum=2` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation diarize_subtitles
```
