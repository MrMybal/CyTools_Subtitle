# CyTools_Subtitle 0.2.0

Local Phonon subtitles, word timing, native audio/video preview, cue editor and MCP API. Built with the actual CyToolsCore 0.10.1 MIT wheel, without copying its runtime sources. No media, UI or ML imports enter the Core.

## Desktop

Launch ../CyTools_Subtitle.exe. English is the default; French is selectable in Options. Select an audio/video source and Generate subtitles. The player streams decoding off the UI thread, overlays active captions and supports pause/seek. Source and preview pixel dimensions are displayed. The editor changes individual cue text/start/end, shifts the track, adds sound captions and exports SRT/VTT/JSON. Reflow explicitly rebuilds speech from original word timings, replacing manual speech edits while preserving sound captions.

Phonon-2 and Phonon-2.5 English: English only. Phonon-2.5: multilingual, including French. These models do not translate, diarize speakers or classify background sounds. CPU is the only integrated execution device; no unused GPU/LoRA controls. Voice filtering is highpass/lowpass plus FFT denoise, not neural vocal separation.

The model receives sequential bounded WAV windows, with overlap and word-midpoint ownership at boundaries. A window is deleted/reused rather than accumulating complete recording tensors. Transcription errors and boundary omissions/repetitions remain possible: review the result. Decoder timing uses native frame resolution; no timing precision or transcript completeness guarantee. Truncated inference fails explicitly and requests shorter windows.

## Operations

- transcribe: media, model/local directory, CPU threads, audio track, windows/overlap, filter, hotwords/strength and cue layout.
- inspect_media: source stream metadata, dimensions and optional bounded WAV excerpt/waveform.
- read_subtitles: paginated original words and current cues in a time range.
- edit_subtitles: stable-ID text/timing patches, delete/add cues, sound descriptions and global offset. Writes a new bundle.
- reflow_subtitles: rebuild speech cues from the original word timing evidence.
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

The local runtime uses the real wheel in app/packages. install.ps1 creates a private venv at its final path using Python 3.11, then installs pinned top-level requirements. install.sh is provided for Linux but unvalidated. Local venvs are not portable; model weights and environments are excluded from source releases.

Model catalog pins are copied from fermion-research==0.2.14 into model-catalog.json. The upstream downloader verifies archive hashes and supports retries; the Tool additionally hashes the local container against packed_manifest.json. Repair preserves damaged managed weights in a neighbouring .invalid-* directory. References require config.json, packed_manifest.json and matching model.fermion for the Phonon-2 family. No LoRA. Configurations contain only references, never weights/secrets. Changing shared cache settings never moves models, Python, PyTorch libraries or the system driver.

Updates requires a configured owner/repository. Expected latest-release assets: cytools-app.zip and cytools-app.zip.sha256. Only confined app/ files are accepted; Tool ID, runtime ABI, platform, SHA256, size/count limits and Python syntax are checked. Dependencies remain fixed; new dependencies require a separately tested runtime. Activation at restart preserves a previous app for rollback, with data/ and runtime/ untouched. Co-published checksums are not independent signatures. No public application repository is configured; update tests use local fixtures.

## Verification and licenses

Private Python: -m pytest app/test_tool.py -q. app/validate_delivery.py runs actual video transcription through MCP, corrections/reflow/export/FinishTask, native audio/video playback and seek, and real cancellation. It requires local validation samples, installed models and an audio device. Evidence: data/reports/. Details: Docs/CapabilityCoverage.md and Docs/Validation.md.

Windows x64 validated locally. Linux/macOS Unknown. Component declarations and full installed notices: licenses.json, LICENCES/, LICENSE and LICENSE-CyToolsCore.txt. Model weights keep CC-BY-4.0; the Phonon runtime keeps Apache-2.0; FFmpeg builds retain their GPL/LGPL obligations.


## Timing corrections in 0.2.0

Generation and reflow now enable auto_timing by default. repair_subtitles also repairs an existing document without rerunning recognition or discarding manual speech edits. The same operation is available through the editor button Repair reading time and overlaps and via MCP/CLI. All controls are in Segmentation & layout and Advanced operations, and participate in configuration save/load.

Defaults: target 22 characters/second and 0.8 s display; at most 0.25 s advance, 0.5 s onset delay, 2 s end extension, and a 40 ms speech-caption gap. Short, fast or overlapping fragments can merge if the result fits the chosen line count and duration. Environmental-sound captions stay unchanged. The original word evidence is retained byte-for-byte as JSON data. Repeated repairs use persistent timing anchors to avoid accumulating drift; an explicit manual edit establishes a new anchor for that edited cue.

An isolated, bounded SciPy/HiGHS worker allocates reading time while respecting synchronization and media-end limits. Remaining reading-speed violations are reported rather than hidden by shifting text farther from the voice. Constraints can be adjusted explicitly. If automatic postprocessing cannot satisfy the constraints, transcription still publishes its raw result with a visible unresolved repair record; an explicit repair fails without changing its source file. No generic forced alignment or corrected transcription accuracy is claimed.

A long-form French recording was repaired through real MCP in about 2.3 seconds without rerunning its 10-minute transcription: 629 cues -> 561, 102 reading-speed warnings -> 11, 2 overlaps -> 0. Every speech word and original word timestamp was preserved. The 11 remaining fast-dialogue cues require human review/condensed wording or an explicitly wider synchronization budget. The source recording and generated artifacts are not part of the distribution.
