# CyTools_Subtitle 0.7.0

Local Phonon subtitles, word timing, native audio/video preview, cue editor and MCP API. Built with the actual CyToolsCore 0.10.1 MIT wheel, without copying its runtime sources. No media, UI or ML imports enter the Core.

## Desktop

Version 0.5.1 keeps separately timestamped punctuation with its words and handles small ASR/voice-boundary offsets when laying out captions. Ambiguous word-boundary changes use nearby phrase context; original word timestamps and raw model timelines are retained. This improves caption segmentation and does not guarantee correct speaker clustering or transcription.

Version 0.4.1 fixes preview of videos with padded RGB rows, including arbitrary capture widths. Drop an audio/video file anywhere on the main window to load its preview; a subtitle JSON document can also be dropped. Invalid files show an error without closing the application.

The CyUI interface provides a sidebar workspace, resizable preview/inspector columns, caption search and a separate cue editor. Options offers five semantic themes, compact/comfortable density and persistent text size; legacy dark/light/classic preferences migrate automatically. English is the default; French remains selectable. Shortcuts: Ctrl+O media, Ctrl+Shift+O subtitle JSON, Ctrl+R reload preview, Space play/pause, Left arrow back two seconds and Ctrl+S save a new subtitle bundle. Shortcuts do not intercept text entry.

The Windows portable release includes Python and media/UI dependencies; PyTorch is downloaded separately from Installation: extract the complete archive, then launch ../CyTools_Subtitle.exe. Source checkouts require install.ps1 first. English is the default; French is selectable in Options. Select an audio/video source and Generate subtitles. The player streams decoding off the UI thread, overlays active captions and supports pause/seek. Source and preview pixel dimensions are displayed. The editor changes individual cue text/start/end, shifts the track, adds sound captions and exports SRT/VTT/JSON. Reflow explicitly rebuilds speech from original word timings, replacing manual speech edits while preserving sound captions.

Phonon-2 and Phonon-2.5 English: English only. Phonon-2.5: multilingual, including French. Phonon does not translate or classify background sounds. Speaker attribution is available through optional Community-1 (CPU) or NVIDIA Nemotron 3 (CPU/CUDA) components. Phonon transcription remains CPU-only; NVIDIA device selection applies to voice analysis. LoRA is unsupported. Voice filtering is highpass/lowpass plus FFT denoise, not neural vocal separation.

The model receives sequential bounded WAV windows, with overlap and word-midpoint ownership at boundaries. A window is deleted/reused rather than accumulating complete recording tensors. Transcription errors and boundary omissions/repetitions remain possible: review the result. Decoder timing uses native frame resolution; no timing precision or transcript completeness guarantee. Truncated inference fails explicitly and requests shorter windows.

## Operations

- transcribe: media, model/local directory, CPU threads, audio track, windows/overlap, filter, hotwords/strength and cue layout.
- inspect_media: source stream metadata, dimensions and optional bounded WAV excerpt/waveform.
- read_subtitles: paginated original words and current cues in a time range.
- edit_subtitles: stable-ID text/timing patches, delete/add cues, sound descriptions and global offset. Writes a new bundle.
- reflow_subtitles: rebuild speech cues from the original word timing evidence.
- runtime_status / install_runtime: inspect or download/repair the optional pinned CPU PyTorch component, with explicit license review and authenticated network permission.
- model_status / install_model / register_local_model: verify, download/repair and reference compatible local models.
- installation_storage_status: SDK cache and Toolkit diagnostics.

All declared parameters and invocation envelopes are accessible in Advanced operations, with validation, estimation, priorities and deadlines. The manifest is the common contract for standalone/CLI/MCP/HTTP. Estimates are conservative envelopes, not measured upper-bound guarantees.

## CLI and MCP

From the Tool root on Windows:

```powershell
.\runtime\python\Scripts\python.exe .\app\tool.py describe
.\runtime\python\Scripts\python.exe .\app\tool.py describe-operation transcribe
.\runtime\python\Scripts\python.exe .\app\tool.py --data-dir .\data\cli invoke transcribe --params-file .\app\params.json --timeout 3600
.\runtime\python\Scripts\python.exe .\app\tool.py --data-dir .\data\mcp mcp
```

Replace the example media path in params.json. MCP configuration example: mcp-config.example.json. Run the private Python with app/make_mcp_config.py to print the absolute paths for your installation. Operation calls have a parameters envelope, for example op_transcribe with {"parameters":{"media":"D:/clips/example.mp4","model":"phonon-2.5"}}. Poll cy_get_job until Completed; errors/cancellation are terminal outcomes requiring review. Inspect the operation output schema before chaining outputs.

AI workflow: op_inspect_media -> op_transcribe -> op_read_subtitles -> op_edit_subtitles -> cy_export_job -> cy_finish_task. Inspect audio excerpts with an audio-capable model or a classifier before adding sound descriptions. A cue with kind=sound is reviewer-supplied, not a Phonon detection. Times use seconds from the media start. JSON retains original words, chunks, source dimensions, settings and reading-speed/overlap warnings.

Absolute local paths are automatically privately imported, including spaces/Unicode. No manual input copies. Original files stay intact. MCP tasks are temporary: FinishTask/disconnect removes task imports and workspaces after real workers stop. Export wanted results first. Desktop and CLI invoke sessions explicitly retain outputs. Independent MCP processes have separate queues; use authenticated shared HTTP/bridge when sharing one scheduler. Clients cannot read another client's private artifacts. Paths refer to the Tool host.

Install operations require the authenticated network permission and explicit public model license review. Provision a credential using create-client --name installer --permission network, then pass the token through the local CYTOOLS_TOKEN environment or authenticated transport. No tokens in parameters, recipes or Git.

## Installation / updates

The local runtime uses the real wheel in app/packages. install.ps1 creates a private venv at its final path using Python 3.11, then installs the pinned Windows base requirements without PyTorch. Install PyTorch through Installation before inference. The full requirements.txt remains available for development environments. install.sh is provided for Linux but unvalidated. Local venvs are not portable; model weights and environments are excluded from source releases.

Model catalog pins are copied from fermion-research==0.2.14 into model-catalog.json. The upstream downloader verifies archive hashes and supports retries; the Tool additionally hashes the local container against packed_manifest.json. Repair preserves damaged managed weights in a neighbouring .invalid-* directory. References require config.json, packed_manifest.json and matching model.fermion for the Phonon-2 family. No LoRA. Configurations contain only references, never weights/secrets. Changing shared cache settings never moves models, Python, PyTorch libraries or the system driver.

Updates requires a configured owner/repository. Expected latest-release assets: cytools-app.zip and cytools-app.zip.sha256. Only confined app/ files are accepted; Tool ID, runtime ABI, platform, SHA256, size/count limits and Python syntax are checked. Dependencies remain fixed; new dependencies require a separately tested runtime. Activation at restart preserves a previous app for rollback, with data/ and runtime/ untouched. Co-published checksums are not independent signatures. No public application repository is configured; update tests use local fixtures.

## Verification and licenses

Private Python: -m pytest app/test_tool.py -q. app/validate_delivery.py runs actual video transcription through MCP, corrections/reflow/export/FinishTask, native audio/video playback and seek, and real cancellation. It requires local validation samples, installed models and an audio device. Evidence: data/reports/. Details: Docs/CapabilityCoverage.md and Docs/Validation.md.

Copyright (c) 2026 Cyberalien. CyTools_Subtitle is licensed under the GNU Affero General Public License, version 3 only (AGPL-3.0-only); see LICENSE for the complete terms. The CyToolsCore SDK remains MIT.

Windows x64 validated locally. Linux/macOS Unknown. Component declarations and full installed notices: licenses.json, LICENCES/, LICENSE and LICENSE-CyToolsCore.txt. Model weights keep CC-BY-4.0; the Phonon runtime keeps Apache-2.0; FFmpeg builds retain their GPL/LGPL obligations.


## Timing corrections in 0.2.0

Generation and reflow now enable auto_timing by default. repair_subtitles also repairs an existing document without rerunning recognition or discarding manual speech edits. The same operation is available through the editor button Repair reading time and overlaps and via MCP/CLI. All controls are in Segmentation & layout and Advanced operations, and participate in configuration save/load.

Defaults: target 22 characters/second and 0.8 s display; at most 0.25 s advance, 0.5 s onset delay, 2 s end extension, and a 40 ms speech-caption gap. Short, fast or overlapping fragments can merge if the result fits the chosen line count and duration. Environmental-sound captions stay unchanged. The original word evidence is retained byte-for-byte as JSON data. Repeated repairs use persistent timing anchors to avoid accumulating drift; an explicit manual edit establishes a new anchor for that edited cue.

An isolated, bounded SciPy/HiGHS worker allocates reading time while respecting synchronization and media-end limits. Remaining reading-speed violations are reported rather than hidden by shifting text farther from the voice. Constraints can be adjusted explicitly. If automatic postprocessing cannot satisfy the constraints, transcription still publishes its raw result with a visible unresolved repair record; an explicit repair fails without changing its source file. No generic forced alignment or corrected transcription accuracy is claimed.

A long-form French recording was repaired through real MCP in about 2.3 seconds without rerunning its 10-minute transcription: 629 cues -> 561, 102 reading-speed warnings -> 11, 2 overlaps -> 0. Every speech word and original word timestamp was preserved. The 11 remaining fast-dialogue cues require human review/condensed wording or an explicitly wider synchronization budget. The source recording and generated artifacts are not part of the distribution.


## Optional speaker diarization (0.5.0)

Community-1 attributes speech to anonymous speaker IDs. Phonon still supplies the text and original word timestamps. Enable **Identify different speakers** in generation, or open an existing JSON document in the editor and use **Speakers → Identify speakers in this document**. The editor lets you rename people and override the speaker of individual captions. Names are display labels; the software does not discover real identities or identify a person across unrelated recordings.

In **Installation**, scroll to **Speaker identification · Community-1**. Install the optional CPU runtime, open the official model page, accept its Hugging Face conditions, then download the model. An existing Hugging Face login is reused. On Windows, a read token can alternatively be stored in Windows Credential Manager; never put tokens in MCP parameters, generation JSON or chat. The isolated runtime and weights are downloaded separately; they do not enlarge the base package or replace Phonon's PyTorch libraries.

Generation options include a known speaker count (0 = automatic), minimum/maximum count, CPU threads, segmentation and embedding batch sizes, and a duration refusal limit of at most four hours. The waveform uses job-owned disk storage and model inference uses bounded batches. This limit does not certify accuracy, processing speed or memory use for every recording. Voices are analyzed globally rather than independently renumbered for each Phonon window.

Existing-document analysis preserves manual text, times, sound captions and original words by default. **Rebuild captions at speaker changes** explicitly recreates speech from original words and can replace manual speech edits; sound captions remain. Timing repair does not merge different speakers. Manual speaker overrides survive re-analysis unless replacement is explicitly requested. Speaker labels can be hidden; visible names count towards reading-speed checks. A caption spanning multiple voices remains reviewable.

The JSON document remains schemaVersion 1 with additive optional `speakers`, `diarization`, `speakerLabels` and per-cue attribution metadata. Exported SRT/VTT can include a plain `[Name]` prefix compatible with ordinary players; raw cue text and original words are stored unchanged. Speaker IDs are scoped to the analyzed recording.

CLI/MCP operations: `diarization_status`, `check_diarization_access`, `install_diarization_runtime`, `install_diarization_model`, `register_diarization_model`, `diarize_subtitles`, and `rename_speakers`. Network installation/access operations require an authenticated network permission and install operations require explicit license review. Local model registration references an official compatible Community-1 bundle in place and hashes its files. All file inputs are automatically imported privately; export wanted outputs before FinishTask.

Community-1 uses CPU/Windows. NVIDIA CUDA is provided by the separate component below. Speaker voiceprints, arbitrary diarization architectures and automatic person naming are not exposed. The optional pipeline's own telemetry is disabled. See [Diarization](Docs/Diarization.md) for the precise validation state.

## NVIDIA Nemotron 3 (0.6.0)

Install this optional engine separately in Installation after reviewing and explicitly accepting its runtime/model licenses. Select NVIDIA in the workspace, generation settings or editor Speakers panel, then choose CPU or CUDA. Phonon words/timestamps are unchanged. Voice identities are scoped to the engine and recording; switching engines does not reuse manually named identities silently.

Operations: `nemotron_status`, `nemotron_diagnostics`, `install_nemotron_runtime`, `install_nemotron_model`, `register_nemotron_model`. Use `diarization_engine: "nemotron3"` with `transcribe` or `diarize_subtitles`. Installation requires authenticated network permission and `license_accepted: true`; defaults do not accept terms. Both the selected runtime and the official pinned Q8_0 GGUF must be ready. Existing local weights can be referenced without moving them.

All NVIDIA mode, preset, custom geometry, segmentation and device fields are exposed through generation settings/configuration and the operation schemas. Community-1 count/batch settings must remain at their default values when using NVIDIA. A configuration load never starts inference. [NvidiaDiarization.md](Docs/NvidiaDiarization.md) describes limits, output metadata and evidence.

## Modular CyUI interface (0.7.0)

The subtitle timeline now uses the shared CyUI Timeline module: seek on the ruler, zoom with the wheel, pan with Shift+wheel, scroll voice lanes with Ctrl+wheel and drag clips/edges to move/trim. Escape cancels a gesture. The common Inspector validates caption drafts; Apply creates one correction. Ctrl+Z / Ctrl+Y (Ctrl+Shift+Z) restores document versions outside text entry. Ctrl+Shift+P opens the command palette.

Video preview uses CyUI Images with fit/zoom/pan. Diagnostics adds severity/search/follow and copy-visible controls while retaining full selectable log text and full-file copy. Advanced operations uses the shared JSON editor/syntax viewer. Existing business parameters, word evidence, model installations and MCP contracts are preserved. English/French, five themes and both densities remain available. See [migration details and validation](Docs/CyUIMigration.md).

CyUI 1.2.0 uses the [MIT license](https://github.com/MrMybal/CyUI/blob/ff023e646c6a3038b3dfbfd53f6d2b4a2f5955e3/LICENSE) from the [CyUI repository](https://github.com/MrMybal/CyUI). The repository is currently private; the complete notice is included in [LICENCES/CyUI-MIT.txt](LICENCES/CyUI-MIT.txt). The application remains AGPL-3.0-only.
