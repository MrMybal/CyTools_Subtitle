# Native capability coverage — CyTools_Subtitle 0.3.0

Inventory source: fermion-research 0.2.14 installed CLI help, fermion/_speech engine implementation, https://github.com/fermionresearch/phonon/blob/main/docs/cli.md and https://www.fermionresearch.com/docs/speech/. Scope: local file transcription and subtitle authoring. Status below distinguishes actual execution from available code.

| Native capability | Tool operation/field | Standalone | Evidence / status |
|---|---|---|---|
| Phonon-2 word-timed English | transcribe.model=phonon-2 | Model + Generate | Real English audio, segmented 5 s windows; real video through MCP |
| Phonon-2.5 multilingual | transcribe.model=phonon-2.5 | Model + Generate | Real French audio, 8 s windows, accents preserved |
| Phonon-2.5 English variant | transcribe.model=phonon-2.5-en | Model selection/install | Implemented, no separate inference run |
| Local compatible directory | transcribe.local_model, register_local_model | Local folder / Register / select | SHA256 + architecture-family validation; fixture tested |
| CPU and native thread kernels | device=cpu, threads | CPU threads | Actual engine=cpu in reports, non-default 2 threads tested |
| CUDA container / MLX engines | Unavailable | No GPU option | Excluded: no container ownership or Apple hardware integration in this Tool |
| Word and segment times / --json | transcribe outputs words/cues | Player and editor | Actual decoder timing; no invented uniform word timestamps |
| CPU --threads | threads 1..32 | Slider | Passed into native CLI; real non-default value tested |
| --hotwords / --hotword-lambda | hotwords array / hotword_lambda | Vocabulary and strength | Real French + video jobs with non-default vocabulary/strength |
| --hotwords-file / repeated flags | Serialized hotwords array | Same vocabulary form | Equivalent terms, excludes arbitrary @FILE indirection |
| --hotword-strength | Unavailable | None | Phonon-1 option; Phonon-1 excluded because it has no word timestamps |
| --download-only / repair | install_model | Installation | Both actual requested models downloaded; upstream archive pins + local container SHA256 |
| --verbose / timings | Worker diagnostics + chunk metadata | Application log | Raw third-party diagnostics retained, no fake token streaming |
| Greedy decoding / no samplers | Fixed native behavior | No sampler controls | Native engine has no transcription temperature/top-p knobs |
| Native long-file windows | Outer bounded sequential windows | Window / overlap sliders | 5 s and 8 s tests; absolute word timing restored using offsets; midpoint ownership |
| Audio input formats | media automatic import + FFmpeg PCM conversion | File picker/path | WAV and MP4 actual runs; other suffixes depend on installed FFmpeg and are unvalidated individually |
| Multitrack source | audio_stream ordinal | Audio-track slider | Passed to FFmpeg; non-default track test documented in test suite |
| Live microphone / listen / server | Unavailable | None | Outside local file subtitle task; SDK already supplies authenticated MCP/HTTP |
| Native bench / CPU describe | Not business operations | Logs / dependency status | Excluded from subtitle jobs; administrative benchmark not required for subtitle generation |
| LoRA / generic arbitrary models | Unavailable | Explicit explanation | Engine has no generic LoRA support; compatible directories only |
| Vocal source separation | Not claimed | Voice filter label | Implemented FFT denoise + bandpass, no neural separator model |
| Sound classification / descriptions | Reviewer edits, kind=sound | Add sound description | MCP sound edit tested. Native Phonon cannot identify non-speech events; inspect excerpt for external listening/classification |
| Forced alignment of arbitrary script | Not claimed | Cue text/start/end and shift | Manual/MCP retiming and original-word reflow available; no aligner model supplied |
| Translation | Unavailable | None | No translation model integrated |

All business fields and invocation envelopes are exposed through Advanced operations. The simplified form additionally provides the common controls. Schema field count is not a claim of universal native capability coverage. JSON/SRT/VTT outputs are private, composable artifacts; MIME types and seconds units are declared in the manifest. Every input-file field is configured for task-owned automatic import. Model references and export destinations are not task inputs.


0.2.0 adds Tool-owned timing repair, not a new Phonon model capability: repair_subtitles, automatic transcription/reflow postprocessing, bounded early/late shifts, reading speed, short-fragment merging and persistent anchors. The editor and MCP use the same isolated worker. Native words, sound captions and manual speech edits are retained; warnings that cannot be resolved within the bounds remain visible. Tested on a complete 58m56s French recording through MCP, with exact word/text preservation and task export/cleanup checks.

## Optional inference runtime in 0.3.0

| Capability | Operation | Standalone | Contract |
|---|---|---|---|
| PyTorch availability without importing the engine | runtime_status | Installation state / Check PyTorch installation | Installed/Missing, expected and detected package versions |
| Private CPU dependency installation | install_runtime | License review / Download or repair PyTorch | Authenticated network permission; license_accepted, repair; fixed package pins, verified candidate activation |

PyTorch and its specific math dependencies are absent from the Windows base archive. Model installation and optional runtime installation remain separate operations. Linux/macOS installation is not validated. See RuntimeInstallation.md and Validation.md.


## Optional Community-1 speaker analysis (0.5.0)

Native inventory: pyannote.audio 4.0.7 `Pipeline.from_pretrained` and `SpeakerDiarization.apply` signatures, packaged upstream sources and the official Community-1 model card. CPU PyTorch 2.8.0+cpu and torchaudio 2.8.0+cpu live in an isolated optional component; Phonon's runtime is unchanged.

| Native capability | Tool operation / fields | Standalone | Validation |
|---|---|---|---|
| Global speaker and exclusive timelines | transcribe.diarization, diarize_subtitles | Generation toggle / Speakers | Controller, attribution and preservation tests; real weight access gated |
| Known count / count bounds | speaker_count, min_speakers, max_speakers | Speaker analysis settings | Schema bounds and argument construction |
| Segmentation / embedding batches | segmentation_batch_size, embedding_batch_size | Speaker analysis settings | Passed to pipeline; full inference awaits weight access |
| CPU threads | threads | Existing threads setting | Applied to optional PyTorch worker |
| Local checkpoint / offline inference | register_diarization_model; managed pinned model | Installation / local folder | Restricted config paths and SHA256 checks |
| Credentials / gated download | check_diarization_access, install_diarization_model | Protected token field / official conditions link | Real gated HTTP refusal, no token in business schema |
| Runtime installation | install_diarization_runtime | License review / install | Real hashed wheel installation and CPU import verified |
| Manual voice/name corrections | edit_subtitles speaker, rename_speakers | Cue speaker / names | Real runtime and GUI jobs, export and cleanup |
| Progress callback | No arbitrary callable input | Existing jobs/logs | Worker phase and native logs; not fabricated per-batch percentages |
| GPU / multi-GPU | Excluded for this release | CPU explicitly shown | No GPU runtime path validated |
| Training, custom classes, biometric embeddings | Excluded | None | Outside file subtitle attribution; no arbitrary Python classes or code parameters |

All options are available in Advanced operations and generation configurations. Raw words and manual caption text are not overwritten by speaker attribution; explicit reflow/rebuild keeps its documented replacement behavior.
