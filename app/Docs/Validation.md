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
