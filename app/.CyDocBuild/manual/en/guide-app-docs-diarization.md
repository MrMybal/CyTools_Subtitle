---
id: guide-app-docs-diarization
title: Optional Community-1 speaker diarization
description: Optional Community-1 speaker diarization
section: Guide
order: 40
parent: guide-lisez-moi
revision: 1a321103eec12eb4
---

## Optional Community-1 speaker diarization {#optional-community-1-speaker-diarization}

NVIDIA Nemotron 3 is a separate optional CPU/CUDA alternative: see [NvidiaDiarization.md](doc:guide-app-docs-nvidiadiarization). This page describes Community-1.

Community-1 supplies global regular and exclusive speaker timelines. Phonon remains the transcription engine. Model: `pyannote/speaker-diarization-community-1`, pinned revision `3533c8cf8e369892e6b79ff1bf80f7b0286a54ee`, CC-BY-4.0. Source: https://huggingface.co/pyannote/speaker-diarization-community-1.

## Installation and credentials {#installation-and-credentials}

The Windows base archive contains no weights or diarization runtime. Installation downloads pinned, hashed wheels into a fresh `runtime/components/diarization` candidate, verifies imports in a fresh CPU process, then atomically activates it. Failed or cancelled candidates do not replace an earlier working component. Private Phonon dependencies are unchanged. Full package pins and official URLs are in `diarization-runtime-lock.json`; installed wheels retain their own license notices.

Open the model page, accept its conditions with your own account, then download through Installation. The Tool never accepts those conditions automatically. Its protected Windows read credential takes precedence over an existing Hugging Face login. The token is never a business parameter, command argument, saved generation field or model metadata entry. Community-1's telemetry is disabled for this Tool.

Local registration references the model directory in place, verifies the fixed Community-1 pipeline class and contained `$model` assets, and stores file hashes in the Tool registry. Custom Python classes and external asset references are rejected. Files are not moved.

## Execution and outputs {#execution-and-outputs}

The optional CPU worker uses a separate dependency path with Pyannote 4.0.7, torch 2.8.0+cpu and torchaudio 2.8.0+cpu. It converts job-owned mono PCM16 audio into a disk-backed float waveform one minute at a time. Pyannote's own sliding analysis and bounded batch sizes analyze the complete recording with global speaker clustering; independent Phonon windows never restart speaker numbering. An explicit duration policy refuses audio longer than four hours at most. Native memory/time behavior on long files remains workload-dependent and has not been certified at that limit.

Original word text/timestamps remain immutable. Generation/reflow can split speech at speaker changes using temporary attributed word copies. Existing-document analysis keeps manual cue text/times by default. Manual speaker assignments persist unless replacement is requested. A duration mismatch, or a changed source hash after a prior analysis, is rejected. This does not prove that an unanalyzed old JSON document matches an arbitrary same-length media file; the user must select the matching recording.

JSON schemaVersion 1 gains optional `speakers`, `diarization`, `speakerLabels`, and per-cue `speaker`, `speakerManual`, `speakerCandidates`, `speakerOverlapFraction`. The fraction measures temporal overlap with an exclusive speaker region, not calibrated model confidence. Uncovered speech stays unassigned. A cue spanning multiple voices keeps reviewable candidates; explicit rebuild can split it using original words. Sound descriptions are never treated as speech.

SRT/VTT can display a plain `[Name]` prefix. Raw cue text stays separate. Visible names count towards reading-speed checks and bounded timing repair, which does not merge cues belonging to different speakers. Renaming does not change words or timing. Speaker labels are per-recording anonymous identities, not person recognition across files.

## Public operations {#public-operations}

- `diarization_status`: local readiness without importing the neural engine.
- `check_diarization_access`: structured Accessible/AccessRequired; authenticated network permission.
- `install_diarization_runtime`, `install_diarization_model`: explicit license review and network permission; candidate activation, private lock and retained diagnostics.
- `register_diarization_model`: compatible local directory reference with hashes.
- `diarize_subtitles`: original media plus document, count/bounds, threads, duration, batch sizes, labels and explicit rebuild/manual replacement flags.
- `rename_speakers`: name map and label display preference; creates a new bundle.
- `edit_subtitles`: optional speaker ID or null on each cue patch.

All media/document file fields participate in automatic private task import. Job workspaces and intermediates use JobContext.path; workers stop before reservations release and scratch files are removed. Export wanted bundles before FinishTask. The standalone uses retained sessions. All native business settings are exposed through generation configuration or Advanced operations.

## Caption boundary repair {#caption-boundary-repair-0-5-1}

Separate closing punctuation is grouped with its preceding word before layout, respecting the configured pause. Word/voice alignment may use a nearest region only within 250 ms when there is no direct overlap; long uncovered gaps stay unassigned. A weak mixed boundary (under 60% dominant word coverage) can retain the previous voice when that voice still overlaps at least 25% of the word. A nearby fallback without direct overlap can follow a well-covered next word in the same unfinished phrase. Fully covered short replies retain their own speaker.

These rules affect temporary layout copies, never original words or raw regular/exclusive model timelines. They prevent timestamp jitter and separately timed punctuation from fragmenting captions. They cannot repair an incorrect neural speaker clustering decision or recover missed/wrong transcription. Existing-document analysis still preserves manual cue text and timing unless rebuild is requested.
