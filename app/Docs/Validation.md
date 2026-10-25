# Validation — 2026-10-24, Windows x64

Actual Python 3.11 private runtime with CyToolsCore 0.10.1 MIT wheel, Fermion 0.2.14, imgui-bundle 1.93.0, PyAV 18.1.0, sounddevice 0.5.6 and imageio-ffmpeg 0.6.0.

Executed evidence in ../../data/reports/:

- real-inference.json: Phonon-2 English, synthesized local speech, 5-second core windows, 2-second overlap, voice filter, 32-character layout and 2 CPU threads. All reference words recovered in this sample; no cue warnings.
- real-inference-fr.json: Phonon-2.5 French speech, 8-second windows, explicit Bonjour vocabulary and strength 1.5. French accents preserved in UTF-8 subtitles.
- delivery-integration.json: 640x360 video, physical audio output, pause/seek; actual MCP transcription and metadata/excerpt, read/edit/add sound/reflow/export, task cleanup; real inference cancellation with worker termination before reservations release.
- preview.png and options EN/FR captures: actual Dear ImGui rendering with video subtitle overlay, persistent preference controls and configuration controls.
- test_tool.py: cue timing/layout/export, malformed documents, private imports/client isolation, export/FinishTask, invalid schemas/media, missing model, worker diagnostics, cancellation, independent operations, generation configuration round trip, confined update archive/activation/rollback and data preservation.
- SDK regression suite: 135 passed. SDK distribution build succeeded; wheel contains portable schemas and templates.

The transcript checks cover short synthetic samples, not a large quality benchmark or difficult audio. Window memory is bounded by construction; 24-hour recordings have not been stress-tested. Preview clock behavior was exercised on this machine, not certified across all audio drivers/codecs. Linux/macOS, CUDA and MLX have not been validated. The English-specific Phonon-2.5-en variant is offered but has no separate real inference result. No public application GitHub repository is configured; updater verification used local archive fixtures rather than a live public release. The source-installation venv depends on system Python. Version 0.2.2 also supplies the separately validated Windows portable runtime described below.


## Timing repair 0.2.0

Actual private SDK remains MIT 0.10.1. Timing uses the already-installed SciPy 1.17.1, now explicitly pinned as a direct dependency.

The repair operation was exercised on a long-form French recording through a real MCP stdio client, followed by export and FinishTask. Original word timestamps and normalized speech text are identical before/after. Caption count 629 -> 561, reading-speed warnings 102 -> 11, overlaps 2 -> 0. Remaining fast dialogue stays flagged within the default synchronization limits; a structural test does not establish audio or linguistic accuracy. Source recordings, generated subtitles and local reports are not distributed.


Tests cover hard early/late/end bounds, rounded output/media end, raw-word/sound/manual-text preservation, repeated repairs without drift, malformed timing policy, legacy configuration loading, and real private-input/export/cleanup. SDK regression suite: 135 passed.


## Windows portable release 0.2.2

A new application-local CPython 3.11.9 x64 embeddable runtime was built from the official python.org archive with a pinned SHA256. Dependencies were installed into a clean directory using windows-constraints.txt; the development venv was not copied. Native Windows launcher rebuilt with Visual Studio 2022. The Tool and its application sources use AGPL-3.0-only; the SDK and third-party components retain their original licenses.

The complete directory was moved to a different path containing spaces and an accented character. Python runs in isolated mode; Torch, NumPy, SciPy, PyAV, MCP, sounddevice, ImGui and Windows integration imported from that moved runtime. CLI describe returned the application manifest. The actual .exe was launched from another working directory: the English Options render closed after 16 frames and the GUI timing-repair operation completed through a worker.

A real MCP stdio session using the relocated interpreter inspected a 640x360 video and transcribed its audio into 27 words and 5 cues in approximately 11.2 seconds on this test machine. The test edited a cue, exported the result, finished the temporary task and verified that only the exported result remained. Preview opened physical audio output, decoded video pixels, played and sought successfully. Installed local models were referenced for this test; weights and test media are not included in the release.

The 21 Tool tests passed after switching the worker to module-based Phonon invocation. These checks cover this Windows machine; they do not establish portability across every Windows version, codec or audio device. The repository is private at this delivery: releases can be downloaded through an authenticated browser, while the in-app updater currently expects public release URLs. Update activation/rollback remain validated with local fixtures rather than a private authenticated download.


## Optional PyTorch download — 0.3.0

The Windows base runtime was rebuilt without Torch, SymPy, NetworkX and mpmath. A relocated clean installation returned Missing and could not resolve the torch module. The actual Windows .exe rendered the Installation tab in English and French without Torch, showing the license review and download controls.

A real authenticated MCP session checked runtime_status, verified refusal without explicit license review, started install_runtime and cancelled after observing the pip child process. The job reached Cancelled only after that child stopped; no active component pointer was created. A subsequent real PyPI installation downloaded PyTorch 2.14.1 and its fixed private math dependencies, passed a separate CPU import check and activated the component in about 62.7 seconds on this machine. Existing model files were referenced in place. Video transcription then produced 27 words and 5 cues, followed by export and temporary-task cleanup.

The automated suite now has 24 passing tests. New coverage checks missing runtime status, path confinement, authenticated network and license requirements, and preservation of the previous active installation when candidate verification fails. Downloaded component directories and caches are excluded from base packaging even after successful local tests. Guided component installation is Windows/CPython 3.11 CPU only; Linux/macOS remain unvalidated.


## CyUI desktop — 0.4.0 (2026-10-25)

The Tool integrates the author-provided CyUI Python port, with its MIT notice and source fingerprints. The local backup commit before integration is recorded in Git. The only vendor adjustments adapt draw flags and text pointer arguments to imgui-bundle 1.93.0; the upstream framework directory is unchanged.

Windows GUI checks exercised all five themes and compact/comfortable density, English/French, a 1024×768 window, real video playback with subtitle overlay, cue search layout, a timing repair through the existing runtime, Options configuration save/load, selectable logs and native clipboard round trip, and complete advanced-operation access. The 24 existing Tool/timing tests passed using the delivered CPython 3.11.9 and private development test tools. No inference algorithm or operation contract changed. Legacy theme preferences and language/text-size persistence were checked.

A fresh portable product without PyTorch or model weights launched through its actual EXE from another working directory. Its workspace rendered the guided missing-PyTorch state and remained usable. The private installed product retains its separately downloaded runtime and models. Linux/macOS and higher-DPI hardware were not exercised; DPI scaling uses the platform factor supplied by HelloImGui.


## Video preview and native file drop — 0.4.1 (2026-10-25)

A real 1676×992 screen capture reproduced the preview failure: PyAV exposed RGB rows with padding, while the image binding requires packed C-contiguous memory. Initial probe and subsequent decode/seek now use the same bounded RGB conversion; the UI holds one frame reference through its draw and reports rendering errors without closing the application. The capture was exercised through playback, seek and pause after the fix.

External file drops are connected to the existing bundled GLFW window, with callback lifetime and cleanup before window destruction. The callback queues UTF-8 paths for processing on a normal UI frame, through the same opener as the file picker. Windows tests verified the Explorer acceptance style and delivered actual WM_DROPFILES events to that window: video, an accented audio path, video with subtitle JSON, and a refused text file. Tests did not synthesize a mouse drag gesture. Files remain at their original locations, and dropping does not submit generation.

The suite passed 30 tests, including four padded capture widths, first-frame and seek-frame packing, and invalid video error handling. No model or PyTorch dependency was added. Windows x64 was exercised; native drop integration on Linux/macOS remains unvalidated.


## Optional speaker diarization — 0.5.0 (2026-10-25)

The isolated Windows CPU runtime installed successfully from 95 pinned, hashed wheels. A fresh process imported Pyannote 4.0.7 with torch/torchaudio 2.8.0+cpu. The separate Phonon torch 2.14.1+cpu installation was preserved; a subsequent real Phonon transcription produced 26 words and 5 cues.

The product suite passes 48 tests. Speaker coverage includes preservation of words/manual text/times/sounds, voice-change layout, visible-name reading speed, manual attribution, reduced-speaker reanalysis, local reference hashes and preflight, malformed metadata, missing access, authenticated license/permission checks, failed candidate activation and job scratch cleanup. The operation test uses a declared timeline worker fixture; it does not establish neural recognition accuracy.

Actual Windows GUI jobs renamed people and changed a cue's speaker in English and French. A real MCP stdio session discovered the new operations, renamed a speaker, exported subtitles and finished its temporary task, verifying cleanup while preserving the exported files and original document. Installation and Options were rendered with the optional runtime present and model absent.

After explicit acceptance of the official conditions, Community-1 downloaded at the pinned revision and passed its catalog/hash checks. Actual CPU inference succeeded on the original one-voice recording. Combined Phonon-2.5 transcription plus Community-1 analysis of a 44.55-second synthetic English/French conversation took 69.34 seconds with two threads. Automatic count (1–4) found two speakers and correctly associated each of the four alternating turns with its voice. A real MCP re-analysis took 57.33 seconds and preserved words, caption text and times; renaming, export and FinishTask cleanup also passed. The installed model/runtime state rendered through the actual Windows launcher.

These are short synthetic integration samples, not a quality benchmark for natural dialogue, simultaneous speakers or background noise. They do not establish a general processing-speed guarantee. See [Diarization](Diarization.md) for the execution contract and limits. No gated weights or optional runtime are included in the base release.

A clean relocated 0.5.0 base package launched through its actual Windows EXE from a different working directory without torch, the optional diarization runtime or model weights. Its editor completed real rename/manual-assignment jobs, and its French Installation page rendered both missing-component states and guided installation controls.
