---
id: guide-app-docs-nvidiadiarization
title: Optional NVIDIA Nemotron 3 — 0.6.0
description: Optional NVIDIA Nemotron 3 — 0.6.0
section: Guide
order: 40
parent: guide-lisez-moi
revision: 62c78e00a36441de
---

## Optional NVIDIA Nemotron 3 {#optional-nvidia-nemotron-3-0-6-0}

This component attributes voices; Phonon still supplies recognized text and original word timestamps. Community-1 remains available separately. NVIDIA uses the official native [NeMo-Speech.cpp v0.2.0](https://github.com/NVIDIA/NeMo-Speech.cpp/tree/v0.2.0) runtime, not another Python ML environment.

## Installation and licenses {#installation-and-licenses}

The base archive contains no NVIDIA runtime or model weights. Installation offers independent Windows x64 CPU and CUDA runtime downloads, native diagnostics, model download and compatible local GGUF reference. Review the Apache 2.0 runtime and [OpenMDW 1.1](https://openmdw.ai/license/1-1/) model terms and explicitly select the acceptance checkbox. Network operations require authenticated network permission and `license_accepted: true`; default false never accepts terms implicitly. No access token is required for this ungated model.

The official [model](https://huggingface.co/nvidia/Nemotron-3-Diarization) is pinned to revision `f667ed73aee57d40cc39428eb768b4fd87a0a29e`, file `Nemotron-3-Diarization.q8_0.gguf`, 107,012,128 bytes, SHA256 `08456d9e22cd9a323c0364d98375f3746d6e68507ebb705cd46438c534c7a3a1`. This is Q8_0 quantization. Runtime archive hashes, sizes and URLs are in `nemotron-catalog.json`. CPU download is about 6 MB, CUDA about 102 MB. Each native archive carries its component notices; root LICENCES includes runtime, third-party and model terms with upstream links.

SDK InstallationStorage supplies the verified resumable download cache. Active installations remain private in runtime/components/nemotron and data/models/nemotron; sharing a download cache does not share the active installation. A fresh candidate is version/probe/hash checked before atomic activation. Failure or cancellation preserves the previous active candidate. Local registration verifies the exact official GGUF without moving it. No driver changes, global PATH edits, Phonon/Pyannote torch replacements or model relocation occur.

## Options and processing {#options-and-processing}

Enable Identify different speakers and select NVIDIA Nemotron 3, then CPU or CUDA. The same fields exist in transcribe, diarize_subtitles, Advanced operations and versioned configuration JSON. Loading a configuration never starts a job. `nemotron_status` reports local presence without engine imports; `nemotron_diagnostics` checks the selected native runtime and actual hardware compatibility. A CUDA selection fails explicitly if unavailable rather than silently falling back to CPU.

The default chunked `v3-offline` quality preset uses stateful Sortformer caches across the recording. `v3-streaming` favors lower latency; `custom` exposes chunk, right/left context, FIFO, speaker-cache and update-period geometry in native 80 ms frames. Native activity options are onset, offset, onset/offset padding and minimum on/off durations. Zero padding/duration values are valid. Geometry overrides require the custom chunked preset; incompatible options are rejected before submission. Full attention uses `--offline`, is limited to 360 seconds, and cannot combine with a custom/streaming preset. The overall configured refusal limit is at most four hours; memory, time and accuracy at that bound are not certified.

The engine automatically detects up to eight anonymous voices. Community-1 speaker-count/batch fields must remain at their default sentinel values when NVIDIA is selected. CPU threads caps the one-shot worker's CPU affinity, inherited by the native child, rather than claiming a nonexistent native CLI thread flag. The actual device and CPU cap are recorded. SDK resources reserve CPU/RAM and estimated CUDA VRAM before execution. CUDA estimates are 2 GiB for named chunked presets and 6 GiB for full/custom; actual memory is workload-dependent.

Job-owned mono 16 kHz PCM16 and result scratch files use JobContext.path. ProcessWorker owns the native descendant, keeps reservations until shutdown, and removes scratch after stopping. No UI or neural imports enter the Core or Tool module import. Native logs remain available in selectable/copyable diagnostics. Task inputs import automatically; export wanted results before FinishTask. Desktop sessions retain their data.

## Outputs and review {#outputs-and-review}

Raw overlapping NVIDIA segments remain intact. A derived single-caption timeline chooses the previously active voice while it remains active, otherwise the earliest active region. This policy is recorded as `previous-active-then-earliest`; it is a Tool layout decision, not a native exclusive-speaker prediction. Cues retain raw overlap candidates. Uncovered speech remains unassigned and the desktop displays its count.

Original words/timestamps and existing caption text/times are preserved by attribution. Explicit rebuild recreates speech captions from original words; sound captions remain. Switching models creates new anonymous identities instead of inheriting the previous engine's names. Existing manual speaker assignments require explicit replacement before such a switch. Same-engine manual overrides retain the existing behavior. Names are display labels, not biometric recognition.

Operations: nemotron_status, nemotron_diagnostics, install_nemotron_runtime, install_nemotron_model, register_nemotron_model; common diarize_subtitles, rename_speakers, edit_subtitles, read_subtitles and export operations remain available.
