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
