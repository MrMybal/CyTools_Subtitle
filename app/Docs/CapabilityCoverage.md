# Native capability coverage — CyTools_Subtitle 0.7.0

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
| Global speaker and exclusive timelines | transcribe.diarization, diarize_subtitles | Generation toggle / Speakers | Real CPU inference: one voice and four alternating turns with two synthetic voices; automatic count |
| Known count / count bounds | speaker_count, min_speakers, max_speakers | Speaker analysis settings | Schema bounds and argument construction |
| Segmentation / embedding batches | segmentation_batch_size, embedding_batch_size | Speaker analysis settings | Applied in real CPU pipeline runs |
| CPU threads | threads | Existing threads setting | Applied to optional PyTorch worker |
| Local checkpoint / offline inference | register_diarization_model; managed pinned model | Installation / local folder | Restricted config paths and SHA256 checks |
| Credentials / gated download | check_diarization_access, install_diarization_model | Protected token field / official conditions link | Real gated HTTP refusal, no token in business schema |
| Runtime installation | install_diarization_runtime | License review / install | Real hashed wheel installation and CPU import verified |
| Manual voice/name corrections | edit_subtitles speaker, rename_speakers | Cue speaker / names | Real runtime and GUI jobs, export and cleanup |
| Progress callback | No arbitrary callable input | Existing jobs/logs | Worker phase and native logs; not fabricated per-batch percentages |
| GPU / multi-GPU | Excluded for Community-1 | CPU explicitly shown | NVIDIA CUDA uses a separate engine below |
| Training, custom classes, biometric embeddings | Excluded | None | Outside file subtitle attribution; no arbitrary Python classes or code parameters |

All options are available in Advanced operations and generation configurations. Raw words and manual caption text are not overwritten by speaker attribution; explicit reflow/rebuild keeps its documented replacement behavior.

## Optional NVIDIA Nemotron 3 (0.6.0)

Inventory: official NeMo-Speech.cpp v0.2.0 CLI help/configuration and native diarization source, plus NVIDIA's Nemotron-3-Diarization model card. Only its pinned Windows CPU/CUDA diarization path is integrated; this is not NVIDIA speech transcription.

| Native capability | Operation / fields | Standalone | Evidence |
|---|---|---|---|
| Q8_0 Sortformer global activity | diarization_engine=nemotron3 | Engine selector | Same natural capture, CPU/CUDA/full runs |
| CPU / CUDA:0 | nemotron_device | Device selector | Native doctor and actual result device; no silent fallback |
| Streaming quality / low latency / full attention | nemotron_mode, nemotron_preset | Speaker settings | Chunked and full executed; full limited to 360 s |
| Custom cache/context geometry | nemotron_chunk/right_context/left_context/fifo/spkcache/update_period | Custom preset fields | Real custom preset run, exact CLI forwarding and compatibility checks |
| Activity thresholds and durations | nemotron_onset/offset/pad_onset/pad_offset/min_duration_on/min_duration_off | Advanced segmentation fields | Real nondefault thresholds/zero padding run; native flags |
| CPU resource cap | threads | CPU threads | Worker affinity inherited by real native child |
| Automatic speaker count, up to eight | Fixed native behavior | Explained in form | Count/batch overrides for Community-1 rejected |
| Overlapping activity | Raw segments + derived exclusiveSegments | Reviewable cue candidates | Overlap regression test; derived policy recorded |
| Verified runtime/model install, local reference | install_nemotron_*, register_nemotron_model | Installation | Both runtimes and model installed through authenticated operations |
| Hardware diagnostics | nemotron_diagnostics | Check selected runtime | Actual compatible GPU detected |
| Device memory, lifecycle | SDK reservations, ProcessWorker | Existing jobs/cancel | CUDA reservation and real native-child cancellation check |
| Other native ASR/translation/server functions | Excluded | None | Outside this optional voice-attribution component |

The same public schemas serve MCP and desktop. Run-time diagnostics, immutable words, renamed/manual voices, exports and task cleanup use the existing composable document contract. See [NVIDIA guide](NvidiaDiarization.md).

## Modular interface (0.7.0)

Core, Timeline, Inspector, Images, Diagnostics, Commands and Code/Python CodeEditor replace the covered local presentation. Canvas is their selected dependency. Engine decoding, validation, job operations and Undo history remain application-owned. No new model capability or platform support is declared. See [CyUIMigration.md](CyUIMigration.md) for the exact selection and validation evidence.
