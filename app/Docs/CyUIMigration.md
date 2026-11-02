# Modular CyUI interface — 0.7.0

CyTools_Subtitle uses the unmodified Python implementation of [CyUI 1.2.0](https://github.com/MrMybal/CyUI/tree/ff023e646c6a3038b3dfbfd53f6d2b4a2f5955e3), revision `ff023e646c6a3038b3dfbfd53f6d2b4a2f5955e3`. The previous application state is retained in local checkpoint `52980f1` (parent `3a08752`). No SDK/model/runtime migration is required.

## Modules and ownership

| Selected family | Application use | Replaced presentation |
| --- | --- | --- |
| Core | Shell, palette, fonts, widgets, notifications, EN/FR localization | Older patched CyUI file and duplicated label/translation identity implementation |
| Timeline | Speech, speaker and sound lanes; ruler seeking, range selection, zoom/pan, move/trim, Delete | Subtitle playback slider; adds direct caption timing gestures |
| Inspector | Typed start/end/text/type drafts, validation and cancellation | Individual hand-built caption property fields |
| Images | GPU video texture surface with fit, pointer zoom and pan | immvision image widget and local aspect-fit canvas |
| Diagnostics | Bounded cached log rows, filters, severity, follow, row selection, copy visible | Local full-file-only log presentation |
| Commands | Ctrl+Shift+P palette, keyboard navigation and disabled actions | Centralizes access to existing file/playback/view/history actions |
| Code / Python CodeEditor | Searchable syntax views for contracts/results; JSON editing and native text Undo | Plain JSON multiline readers/editors |
| Canvas | Automatic dependency of Timeline and Images | Shared clipping and coordinate/navigation surface |

Only 13 required Python source files are vendored in app/cyui.py and app/cyui_modules. Each is byte-checked against cyui-source.json. No Audio, AudioViews, Plots, Curves, Nodes, Diff, Assets, Viewport, DocumentViews, Gallery, Web or CEF module is shipped. Playback uses the existing application decoder/audio engine; this product had no waveform/spectrum/DSP editor to migrate. The static caption list and model/provider installation forms remain application-specific data views using Core widgets. There is no Web/Unreal integration.

Read-only JSON views retain a Selectable JSON text mode for partial selection/copy in addition to full-copy actions. Python CodeEditor uses the common ImGui multiline editor plus syntax preview; it does not expose the C++ TextEditor multiple-cursor/completion backend. No native Lexilla, CEF, TextEditor, Audio/Gallery library, NumPy replacement, OpenGL package or second Dear ImGui instance is added. The one imgui-bundle 1.93.0 renderer and existing media dependencies remain pinned. This Python host has no CyUI CMake target; CYUI_MODULES/CYUI_IMGUI_TARGET apply to native consumers, not this adapter. The Windows launcher remains a small C++17 program.

## Reproduce and verify the integration

```powershell
.\runtime\python\Scripts\python.exe app/sync_cyui.py --check
# Restore the exact selected blobs from a local checkout containing the pinned commit:
.\runtime\python\Scripts\python.exe app/sync_cyui.py --sync --source PATH_TO_CYUI
.\runtime\python\Scripts\python.exe -m pytest app/test_modular_ui.py -q
```

The sync tool reads committed Git blobs without modifying the reference checkout, rejects hash changes and verifies selected Python import dependencies. It performs no automatic network fetch or install. .gitattributes preserves LF bytes for the vendored snapshot. To update CyUI deliberately, review the new revision/modules, update the pins and rerun the same checks. Do not patch copied library files; application adapters belong in subtitle_ui.py. Existing source/portable builders include the selected source package and complete CyUI MIT notice in root/app LICENCES.

Compile the launcher with app/build_launcher.ps1 in an x64 MSVC developer environment. Build a fresh Windows base with app/build_windows.py, validate the resulting directory, then package it using --package-only. Existing Python/media dependencies are unchanged. App update archives can carry this migration under the existing runtime ABI; installation data, models and optional engines remain separate.

## Transactions, identity and review

Each timeline has independent state and stable nonzero uint64 IDs derived from the document's string cue/speaker IDs. Label changes never change identity. The Tool retains original string IDs in JSON/MCP. Visible clip sets are indexed/cached by document revision; a range containing more than 3,000 visible captions prompts zooming rather than silently dropping data. Full text remains available in the caption list/inspector. Clip labels use Core's clipping helper.

Timeline begin/update events are previews. Only commit sends one existing edit_subtitles operation for the entire gesture, after domain validation. Escape or a revision/view change cancels previews. Invalid or negative timing rejects the complete proposal. Moving between voice/sound lanes makes an explicit speaker/type patch; same-lane timing edits preserve text, original words, sound descriptions and voice metadata. Original media/documents are never overwritten.

Inspector edits remain drafts until Apply cue edit. Native text Undo belongs to that focused field. Invalid drafts do not enable Apply. Outside text input, Ctrl+Z / Ctrl+Y (or Ctrl+Shift+Z) traverse application-owned retained document versions; a completed gesture is one history step. History is bounded to 40 versions / 32 MiB (the current document is always retained). A no-op Save changes the exportable bundle without adding a spurious Undo step. Undo/Redo retain the matching output job, so export uses the selected version. A late correction result remains saved but does not replace a different document opened while it ran.

File rotation/discovery, redaction, authenticated job events and full-log reading remain in standalone_log.py. Diagnostics supplies rows/filter/follow/copy-visible. The app retains Copy entire log and a selectable raw-text section; refresh pauses while selecting raw text. Video decoding stays bounded/off the UI thread. The UI uploads/retires GPU textures and releases them before renderer shutdown. Images supplies fit/zoom/pan; subtitle overlays remain domain presentation using palette/dp.

English remains the default; French selection persists. Application catalogs are registered with the common CyUI locale API. User text, names, paths, IDs and protocol values are never translated. All dimensions/colors in the adapters use CyUI metrics/roles. Existing configuration callbacks, optional engine installation, GPU selection, exports and MCP operations are retained.

## Verification

Windows x64: 86 tests pass, including real ImGui move/trim/commit/cancel/revision gestures, typed-field cancellation, keyboard command execution, stable language IDs, snapshot hashes/import closure, atomic patches, history branching/budgets and unchanged word evidence. Existing preview, timing, diarization, security/resource and configuration tests remain in the suite.

The actual EXE rendered all eight views in English and French across five themes and both densities. A synthetic padded-width video and subtitle document exercised the texture surface and a real edit job followed by Undo/Redo. Headless ImGui frames also rendered adapters at 100%, 125%, 150% and 200% style DPI. This does not certify moving a native window between physical monitors. The rebuilt native launcher and real WM_DROPFILES input loaded the synthetic media/document, played, sought and paused without decoder/texture errors. Actual MCP stdio retained 45 tools and completed read/edit/export/FinishTask with original words, voices and inputs preserved. Private reports/captures are retained in data/reports. Linux/macOS execution is unvalidated, matching the product's prior platform status.

No transcription-quality improvement is implied by this interface migration. Phonon, Community-1 and NVIDIA inference logic, downloads and installed weights are unchanged.

CyUI license: [https://github.com/MrMybal/CyUI/blob/main/LICENSE](https://github.com/MrMybal/CyUI/blob/main/LICENSE). The complete MIT text ships with the application, including when the upstream repository is private.
