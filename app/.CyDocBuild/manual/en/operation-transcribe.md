---
id: operation-transcribe
title: transcribe
description: Decode local audio/video, sequential bounded overlapping windows, Phonon word timing, SRT/VTT/JSON. No invented sound labels.
section: Reference
order: 200
parent: operations
revision: b9f6d2fae89fdef5
---

Decode local audio/video, sequential bounded overlapping windows, Phonon word timing, SRT/VTT/JSON. No invented sound labels.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `media` | `string` | Yes | Source audio or video, up to 8 GiB. Absolute local paths accepted; automatically imported into the private task.  |
| `model` | `string` | No | Phonon-2 and 2.5-en: English only. Phonon-2.5: multilingual including French. `default="phonon-2"`, `enum=["phonon-2", "phonon-2.5", "phonon-2.5-en"]` |
| `local_model` | `string` | No | Optional local Phonon-2-family model directory; referenced in place, not imported. No LoRA support. `default=""` |
| `device` | `string` | No | Actually applied via FERMION_DEVICE. CUDA container and MLX are not integrated. `default="cpu"`, `enum=["cpu"]` |
| `threads` | `integer` | No | Phonon/Community-1 CPU threads; NVIDIA limits its worker and inherited native process to this many logical CPUs. `default=4`, `minimum=1`, `maximum=32` |
| `audio_stream` | `integer` | No | Zero-based audio-track ordinal, independent of the global stream index. `default=0`, `minimum=0`, `maximum=31` |
| `chunk_seconds` | `number` | No | Core window length in seconds; processed sequentially. `default=24`, `minimum=5`, `maximum=28` |
| `overlap_seconds` | `number` | No | Total overlap context in seconds; half on each side of a core window. `default=2`, `minimum=0.2`, `maximum=4` |
| `filter` | `string` | No | voice: high-pass/low-pass and FFT denoise, NOT neural source separation. `default="none"`, `enum=["none", "voice", "denoise"]` |
| `hotwords` | `array` | No | Up to 25 names or vocabulary terms to favour; no command/file indirection. `default=[]` |
| `hotword_lambda` | `number` | No | Per-token bonus strength for the supplied vocabulary. `default=2`, `minimum=0`, `maximum=10` |
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
| `diarization` | `boolean` | No | Optional offline Community-1 CPU speaker attribution; requires separately installed runtime/model. `default=false` |
| `speaker_count` | `integer` | No | Known number of voices; 0 enables automatic counting and min/max bounds. Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=0`, `minimum=0`, `maximum=32` |
| `min_speakers` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=1`, `minimum=1`, `maximum=32` |
| `max_speakers` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=16`, `minimum=1`, `maximum=32` |
| `diarization_max_seconds` | `integer` | No | Refuse longer audio before diarization; this is a processing bound, not an accuracy or performance guarantee. `default=14400`, `minimum=1`, `maximum=14400` |
| `segmentation_batch_size` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=1`, `minimum=1`, `maximum=16` |
| `embedding_batch_size` | `integer` | No |  Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices. `default=8`, `minimum=1`, `maximum=64` |
| `speaker_labels` | `boolean` | No | Include speaker display names in preview and SRT/VTT without changing cue text. `default=true` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation transcribe
```
