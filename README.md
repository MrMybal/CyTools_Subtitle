# CyTools_Subtitle

Local subtitle generation from audio and video, with a Dear ImGui media player, cue editor, and MCP/CLI API.

[Français](LISEZ-MOI.md) · [Detailed guide](app/README.md) · [Capabilities](app/Docs/CapabilityCoverage.md)

## Features

- Phonon-2 for English; Phonon-2.5 for multilingual transcription, including French.
- Sequential bounded audio windows and native word timestamps.
- Phrase-based SRT, WebVTT and editable JSON subtitles.
- Audio/video playback with caption overlays, pause and seek.
- Cue text/timing edits, track offset and reviewer-supplied sound descriptions.
- Automatic reading-time/overlap repair with explicit synchronization limits and visible unresolved warnings.
- The same operations through the desktop editor, MCP, CLI and authenticated HTTP service.
- English/French UI, persistent preferences, configuration save/load, separate PyTorch/model installation and compatible local references.

## Windows portable download

Download `CyTools_Subtitle-0.4.0-windows-x64.zip` from [Releases](https://github.com/MrMybal/CyTools_Subtitle/releases/latest), extract the entire archive to a writable folder, and open **CyTools_Subtitle.exe**. Python and the media/UI dependencies are included. No system Python installation is required. In **Installation**, review the PyTorch license and click **Download / repair PyTorch**, then review the model license and download Phonon-2 or Phonon-2.5. PyTorch and model weights are downloaded separately.

English is the default interface language; French is selectable in Options. Keep app/ and runtime/ next to the executable. Settings, models and outputs are created in data/. Private release downloads require a GitHub account with access to the repository. The in-app updater currently supports public release downloads; use the browser while this repository is private.

## Windows source setup

Python 3.11 is required. In PowerShell from this directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File app/install.ps1
```

Open **CyTools_Subtitle.exe**, then use **Installation** to review the model license and download a model. Choose your audio/video source and Generate subtitles. Review the result in the player and export the wanted files.

The environment is created privately in runtime/python. Source checkouts exclude model weights, installed environments, caches and generated results. The source setup creates a venv and requires machine Python. The Windows portable release includes its own interpreter. PyTorch is installed separately through Installation.

CPU inference is implemented and tested on Windows x64. The Linux installer/launcher is supplied but unvalidated; Linux/macOS status remains Unknown. GPU, neural vocal separation, translation, diarization and automatic environmental-sound classification are not implemented. Voice filtering is bandpass plus FFT denoise.

## MCP and CLI

```powershell
.\runtime\python\Scripts\python.exe .\app\make_mcp_config.py
.\runtime\python\Scripts\python.exe .\app\tool.py describe
.\runtime\python\Scripts\python.exe .\app\tool.py --data-dir .\data\mcp mcp
```

The first command prints an MCP configuration with paths for your installation. Absolute local media/document paths are imported automatically; no manual staging is required. MCP task files are temporary: export wanted results before cy_finish_task or disconnect. Desktop sessions retain their outputs.

See [the operation guide](app/README.md) for transcription, inspection, editing, timing repair, models and exports.

## Development

The actual MIT CyToolsCore 0.10.1 wheel is included in app/packages. Business contracts are in app/CyTool.json. Native launcher sources and its build script are in app/. Heavy model/media/UI dependencies remain outside the Core.

```powershell
.\runtime\python\Scripts\python.exe -m pip install pytest
.\runtime\python\Scripts\python.exe -m pytest app/test_tool.py app/test_timing.py -q
.\runtime\python\Scripts\cytools.exe validate app/CyTool.json
```

The optional delivery integration script requires locally generated sample clips, installed models and an audio device. Test evidence and platform limits are described in [Validation](app/Docs/Validation.md).

## Windows release build

Build from a Windows x64 CPython 3.11 environment with the pinned dependencies. Compile the launcher with `app/build_launcher.ps1` from a Visual Studio developer prompt. Run `python app/build_windows.py`, validate and relocate the generated directory, then run `python app/build_windows.py --package-only --directory PATH`. The builder downloads the official Python embeddable package, verifies its pinned SHA256 and installs dependencies into a fresh directory using `app/windows-constraints.txt` and `app/requirements-base-windows.txt`. PyTorch, SymPy, NetworkX and mpmath are excluded from the base ZIP and installed privately on request. It does not copy an existing venv. `app/build_release.py` builds the app update and corresponding application source archives.

## Optional PyTorch runtime

The base application opens without PyTorch: preview, subtitle editing and timing repair remain available. In Installation, review the PyTorch license and use **Download / repair PyTorch**. This installs pinned CPU PyTorch and its specific math dependencies into a private component directory. A new candidate is verified before activation; a failed or cancelled download does not replace an existing active component. Model files and CUDA/system drivers are not moved.

MCP/CLI clients use **runtime_status** and **install_runtime**. Installation requires the authenticated `network` permission and `license_accepted: true`; `repair: true` builds a new candidate. See [Runtime installation](app/Docs/RuntimeInstallation.md). PyTorch is checked before inference and missing prerequisites produce an actionable error.

The 0.3.0 base runtime uses a new update ABI. For a 0.2.x installation, extract the new full Windows ZIP into a separate directory. Existing Phonon model folders can be referenced through Installation without moving them; keep existing data and results.

## CyUI desktop

Version 0.4.0 uses CyUI with a sidebar, synchronized player, searchable phrase captions and an inspector for edits. Choose Mid Grey, Light Grey, Amber Night, Violet or Navy in Options, with compact/comfortable density and text scaling. English remains the default, with French selectable. PyTorch and models are still separate downloads.

CyUI is MIT-licensed by Cyberalien; its full notice is in [LICENCES/CyUI-MIT.txt](LICENCES/CyUI-MIT.txt). Application code remains AGPL-3.0-only. The vendored Python source fingerprint and binding compatibility adjustment are documented in app/cyui-source.json.

## License

Copyright (c) 2026 Cyberalien. CyTools_Subtitle is licensed under the GNU Affero General Public License, version 3 only (AGPL-3.0-only). The bundled CyToolsCore SDK remains MIT. Engines, libraries and model weights retain their separate licenses, including Apache-2.0, CC-BY-4.0 and the relevant FFmpeg build licenses. See [LICENSE](LICENSE), [LICENCES](LICENCES/SOURCES.txt) and app/LICENCES.
