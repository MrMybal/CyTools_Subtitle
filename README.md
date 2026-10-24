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
- English/French UI, persistent preferences, configuration save/load, model installation and compatible local references.

## Windows setup

Python 3.11 is required. In PowerShell from this directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File app/install.ps1
```

Open **CyTools_Subtitle.exe**, then use **Installation** to review the model license and download a model. Choose your audio/video source and Generate subtitles. Review the result in the player and export the wanted files.

The environment is created privately in runtime/python. Source checkouts exclude model weights, installed environments, caches and generated results. The supplied venv setup requires machine Python; a portable interpreter is not bundled.

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

## License

Copyright (c) 2026 Cyberalien. CyTools_Subtitle is licensed under the GNU Affero General Public License, version 3 only (AGPL-3.0-only). The bundled CyToolsCore SDK remains MIT. Engines, libraries and model weights retain their separate licenses, including Apache-2.0, CC-BY-4.0 and the relevant FFmpeg build licenses. See [LICENSE](LICENSE), [LICENCES](LICENCES/SOURCES.txt) and app/LICENCES.
