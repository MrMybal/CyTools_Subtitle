---
id: guide-lisez-moi
title: User guide
description: Use the application step by step.
section: Guide
order: 10
parent: overview
revision: 0c6b4d312febec88
---

## CyTools_Subtitle {#cytools-subtitle}

Portable Windows archive: extract all of ZIP into a writable folder, then launch CyTools_Subtitle.exe. Python and the reader and interface libraries are included. In Installation, review the license of PyTorch and click Download / repair PyTorch, then download the models in the Installation tab after reviewing their license. For a source installation, run app/install.ps1 first.

1. Open your audio or video in Media & generation.
2. Choose phonon-2 for English or phonon-2.5 for French and multilingual.
3. Click Generate subtitles. The audio windows are processed one by one.
4. Control playback/pause and the timeline. The subtitle editor allows you to modify texts, starts/ends, and sound descriptions.
5. Choose an export folder then Export SRT / VTT / JSON.

Options: French/English, theme, text size, licenses, JSON configurations, and optional autosave. Loading a configuration does not start any processing.

Installation: download, resume, repair, and reference compatible local models. The vocal filter reduces noise; it does not separate voices from music. Sound descriptions are added by the user or the AI after listening.

AI/MCP: consult [app/README.md](doc:operations) and app/mcp-config.example.json. Absolute paths are accepted without manual copying. Export the desired results before the end of a temporary AI task.

Windows x64 and CPU testing done. Linux/macOS not validated. The portable Windows package includes its own Python 3.11.9. Source installation requires Python 3.11 and app/install.ps1 or app/install.sh.

The GitHub repository is configured in Updates; no presumed public repository. The app/ updates are active on restart with restoration, preserving data/ and runtime/.

Version 0.2.0: the correction of durations and overlaps is now automatic for new generations. In Subtitle editor, the Repair reading time and overlaps button also fixes an old result without restarting Phonon. Settings for limits are in Segmentation & layout; very fast cases are still flagged to preserve synchronization and full text.

Version 0.2.1: the application is under GNU Affero General Public License version 3 only (AGPL-3.0-only), copyright (c) 2026 Cyberalien. See LICENSE. The SDK CyToolsCore remains MIT; libraries and models retain their respective licenses.

Version 0.2.2: a portable Windows package with private runtime included. Models are downloaded separately. Private releases are downloaded in the browser with an authorized account; the integrated updater currently requires a public release.

Version 0.3.0: PyTorch, SymPy, NetworkX, and mpmath are no longer included in the base ZIP. Installation offers their private download, verification, and repair. The reader and editor function without PyTorch. To migrate from 0.2.x, extract the new package in a separate folder and reference existing models without moving them.

Version 0.4.0: interface CyUI with side navigation, synchronized reader, search in replays, and timing editing. Five themes, two densities, and text size in Options. English is default, French is selectable. PyTorch and models are still downloaded separately.

Version 0.4.1: correction of the preview crash with certain capture widths. Drop an audio/video file or a JSON subtitle document from Explorer into the window to open it.

Version 0.5.0: optional speaker identification with Community-1, modifiable names, attribution by line, and exports with names. Install the engine CPU and weights separately in Installation after accepting the Hugging Face terms. No token in configurations or settings MCP.

0.5.1 : correction of the subtitles reduced to punctuation and parasitic cuts at the edge of the word. The words and the raw model detections are kept; the transcription and speaker errors must always be re-read.

Version 0.6.0 : optional engine NVIDIA Nemotron 3 to assign voices, on CPU or CUDA. In Installation, consult and explicitly accept OpenMDW 1.1 (model) and Apache 2.0 (runtime) licenses, and download the chosen runtime as well as the model Q8_0. In Generation or in Speakers, choose NVIDIA and CPU/CUDA. Phonon continues to produce the text and its timings; here GPU NVIDIA concerns voice assignment. The model (~107 Mo) and the runtime (~6 Mo CPU / ~102 Mo CUDA) are downloaded separately. Some passages may remain without a speaker and must be reread. See [the guide NVIDIA](doc:guide-app-docs-nvidiadiarization).
