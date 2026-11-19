# Documentation integration notes for coding assistants

This file is for assistants working on the application's documentation. The human manual opens through Documentation.html. Do not import this file into its content, navigation or search index.

```json
{
  "application": "CyTools_Subtitle",
  "version": "0.7.2",
  "entry": "Documentation.html",
  "manifest": "DocData/manifest.json",
  "defaultLocale": "en",
  "publishedLocales": [
    "en",
    "fr"
  ],
  "modules": []
}
```

## Human reader first

Write the manual for people using the application: clear tasks, useful examples, readable media captions and accessible controls. Preserve the application's own terminology and logo. Show complete labels in tooltips when space requires truncation.

Keep documentation build instructions, AI instructions, migration inventories, audit results and verification history outside the human manual. Store assistant guidance in this DocAI.md sidecar, and keep private working records in the source repository. Mark existing internal Markdown with audience: internal or audience: ai to exclude it from an export.

## Languages

English is the source/default language; a complete French translation is mandatory. Keep the same page IDs and explicit anchors across translations. Translate prose, titles, descriptions, captions, annotations and media explanations; code and API identifiers retain their proper spelling. Do not copy original-language prose into another locale, use placeholders, or declare a partially translated manual complete.

The build fails before publishing when English or French has missing/empty pages or explicitly outdated sourceRevision values. Additional incomplete locales are withheld. This structural check cannot judge translation quality: read the translations before publishing. Do not restore a mixed-language fallback banner or expose incomplete languages in the selector.

## Files and integration

Ship Documentation.html, this DocAI.md, and the complete DocData directory together. The HTML is the reader itself; all runtime scripts, media, styles, notices, manifests and optional version exports are inside DocData. Open the HTML through file:// with no web server, runtime CDN or remote font.

Source Markdown, asset inputs, tooling and the build configuration belong in App/.CyDocBuild/. The CLI looks for .CyDocBuild/cydoc.config.json by default; its output is the sibling App/Documentation/. Edit those inputs and rebuild. Do not edit generated data.js or manifest.json by hand. Authored media and logos use logical assets/ paths; do not prepend DocData in the source content. Custom readers use context.assetUrl for display and retain logical paths for binary providers and annotation identities.

Review documentation against the application's current UI, behavior and public APIs, then correct obsolete descriptions. Organize topics and subpages as a tree. Public function APIs, signatures, includes, imports and modules may be documented; never publish raw source listings or implementation bodies. apiIndex creates API-only references; the legacy sourceIndex option does not restore source browsing. Keep source trees outside the manual's assets.

Select only useful optional modules. A gallery also needs each item's reader; only mesh requires Three.js. Keep image enlargement inside the documentation window and preserve keyboard, touch and Escape controls.

Use Documentation.html#/LOCALE/PAGE/ANCHOR for contextual help, with correctly encoded stable IDs. Preserve existing deep links or add validated aliases. Legacy index.html files may remain solely as compatibility redirects. Test the exported manual and the application's help entry on the target platform; report only checks actually performed.


# CyTools_Subtitle — application integration

Use the installed private Python interpreter and `app/tool.py`. CLI inspection: `describe`, `list-operations`, and `describe-operation OPERATION_ID`; MCP: `mcp`. File inputs accept readable absolute paths and are automatically imported into the task. Export wanted outputs before finishing a temporary task. Never accept a model licence or file modification confirmation for the user.

## Public operation contracts

```json
[
  {
    "id": "transcribe",
    "name": "Generate subtitles",
    "description": "Decode local audio/video, sequential bounded overlapping windows, Phonon word timing, SRT/VTT/JSON. No invented sound labels.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "media": {
          "type": "string",
          "minLength": 1,
          "description": "Source audio or video, up to 8 GiB. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "model": {
          "type": "string",
          "enum": [
            "phonon-2",
            "phonon-2.5",
            "phonon-2.5-en"
          ],
          "default": "phonon-2",
          "description": "Phonon-2 and 2.5-en: English only. Phonon-2.5: multilingual including French."
        },
        "local_model": {
          "type": "string",
          "default": "",
          "description": "Optional local Phonon-2-family model directory; referenced in place, not imported. No LoRA support."
        },
        "device": {
          "type": "string",
          "enum": [
            "cpu"
          ],
          "default": "cpu",
          "description": "Actually applied via FERMION_DEVICE. CUDA container and MLX are not integrated."
        },
        "threads": {
          "type": "integer",
          "default": 4,
          "minimum": 1,
          "maximum": 32,
          "description": "Phonon/Community-1 CPU threads; NVIDIA limits its worker and inherited native process to this many logical CPUs."
        },
        "audio_stream": {
          "type": "integer",
          "default": 0,
          "minimum": 0,
          "maximum": 31,
          "description": "Zero-based audio-track ordinal, independent of the global stream index."
        },
        "chunk_seconds": {
          "type": "number",
          "default": 24,
          "minimum": 5,
          "maximum": 28,
          "description": "Core window length in seconds; processed sequentially."
        },
        "overlap_seconds": {
          "type": "number",
          "default": 2,
          "minimum": 0.2,
          "maximum": 4,
          "description": "Total overlap context in seconds; half on each side of a core window."
        },
        "filter": {
          "type": "string",
          "enum": [
            "none",
            "voice",
            "denoise"
          ],
          "default": "none",
          "description": "voice: high-pass/low-pass and FFT denoise, NOT neural source separation."
        },
        "hotwords": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
            "pattern": "^[^,@\\r\\n]+$"
          },
          "maxItems": 25,
          "default": [],
          "description": "Up to 25 names or vocabulary terms to favour; no command/file indirection."
        },
        "hotword_lambda": {
          "type": "number",
          "default": 2,
          "minimum": 0,
          "maximum": 10,
          "description": "Per-token bonus strength for the supplied vocabulary."
        },
        "max_chars": {
          "type": "integer",
          "default": 42,
          "minimum": 10,
          "maximum": 100,
          "description": "Maximum characters per line; long unbreakable words are preserved."
        },
        "max_lines": {
          "type": "integer",
          "default": 2,
          "minimum": 1,
          "maximum": 4,
          "description": "Maximum lines per speech cue."
        },
        "max_duration": {
          "type": "number",
          "default": 6,
          "minimum": 0.5,
          "maximum": 20,
          "description": "Target maximum speech cue duration in seconds; a single word is never split."
        },
        "pause": {
          "type": "number",
          "default": 0.65,
          "minimum": 0.1,
          "maximum": 5,
          "description": "Split speech after a silence gap of at least this many seconds."
        },
        "auto_timing": {
          "type": "boolean",
          "default": true,
          "description": "Automatically repair reading time after transcription/reflow. Native word evidence stays unchanged; unresolved warnings remain visible."
        },
        "max_cps": {
          "type": "number",
          "default": 22,
          "minimum": 5,
          "maximum": 40,
          "description": "Target maximum readable characters per second. Unavoidable violations remain reported."
        },
        "min_duration": {
          "type": "number",
          "default": 0.8,
          "minimum": 0.2,
          "maximum": 3,
          "description": "Target minimum cue display duration in seconds, subject to synchronization limits."
        },
        "max_advance": {
          "type": "number",
          "default": 0.25,
          "minimum": 0,
          "maximum": 1,
          "description": "Maximum seconds a caption may start early or end earlier than its source cue."
        },
        "max_delay": {
          "type": "number",
          "default": 0.5,
          "minimum": 0,
          "maximum": 2,
          "description": "Maximum permitted delay of cue onset in seconds; never accumulated across the track."
        },
        "max_extension": {
          "type": "number",
          "default": 2,
          "minimum": 0,
          "maximum": 3,
          "description": "Maximum seconds to extend a cue end, without overlapping another speech caption or exceeding media duration."
        },
        "min_gap": {
          "type": "number",
          "default": 0.04,
          "minimum": 0,
          "maximum": 0.5,
          "description": "Minimum separation between speech captions in seconds."
        },
        "merge_fragments": {
          "type": "boolean",
          "default": true,
          "description": "Combine nearby short/fast/overlapping speech cues when the line and duration bounds permit; retain every word."
        },
        "diarization": {
          "type": "boolean",
          "default": false,
          "description": "Optional offline Community-1 CPU speaker attribution; requires separately installed runtime/model."
        },
        "speaker_count": {
          "type": "integer",
          "default": 0,
          "minimum": 0,
          "maximum": 32,
          "description": "Known number of voices; 0 enables automatic counting and min/max bounds. Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "min_speakers": {
          "type": "integer",
          "default": 1,
          "minimum": 1,
          "maximum": 32,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "max_speakers": {
          "type": "integer",
          "default": 16,
          "minimum": 1,
          "maximum": 32,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "diarization_max_seconds": {
          "type": "integer",
          "default": 14400,
          "minimum": 1,
          "maximum": 14400,
          "description": "Refuse longer audio before diarization; this is a processing bound, not an accuracy or performance guarantee."
        },
        "segmentation_batch_size": {
          "type": "integer",
          "default": 1,
          "minimum": 1,
          "maximum": 16,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "embedding_batch_size": {
          "type": "integer",
          "default": 8,
          "minimum": 1,
          "maximum": 64,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "speaker_labels": {
          "type": "boolean",
          "default": true,
          "description": "Include speaker display names in preview and SRT/VTT without changing cue text."
        },
        "diarization_engine": {
          "type": "string",
          "enum": [
            "community1",
            "nemotron3"
          ],
          "default": "community1",
          "description": "Optional speaker analysis engine; Phonon remains the text/timing engine."
        },
        "nemotron_device": {
          "type": "string",
          "enum": [
            "cpu",
            "cuda"
          ],
          "default": "cpu",
          "description": "NVIDIA analysis device. CUDA means native CUDA device 0; no silent CPU fallback."
        },
        "nemotron_mode": {
          "type": "string",
          "enum": [
            "chunked",
            "full"
          ],
          "default": "chunked",
          "description": "Stateful chunked inference keeps global identities; full attention refuses audio over 360 seconds."
        },
        "nemotron_preset": {
          "type": "string",
          "enum": [
            "v3-offline",
            "v3-streaming",
            "custom"
          ],
          "default": "v3-offline",
          "description": "Quality-oriented chunked geometry, low-latency geometry, or explicit custom geometry. Full attention requires the default sentinel."
        },
        "nemotron_chunk": {
          "type": "integer",
          "default": 340,
          "minimum": 1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_right_context": {
          "type": "integer",
          "default": 40,
          "minimum": 0,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_left_context": {
          "type": "integer",
          "default": -1,
          "minimum": -1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_fifo": {
          "type": "integer",
          "default": 40,
          "minimum": 0,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_spkcache": {
          "type": "integer",
          "default": 264,
          "minimum": 1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_update_period": {
          "type": "integer",
          "default": 300,
          "minimum": 1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_onset": {
          "type": "number",
          "default": 0.641,
          "minimum": 0.001,
          "maximum": 1,
          "description": "Native NVIDIA onset probability."
        },
        "nemotron_offset": {
          "type": "number",
          "default": 0.561,
          "minimum": 0.001,
          "maximum": 1,
          "description": "Native NVIDIA offset probability."
        },
        "nemotron_pad_onset": {
          "type": "number",
          "default": 0.229,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA pad onset in seconds; zero is preserved."
        },
        "nemotron_pad_offset": {
          "type": "number",
          "default": 0.079,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA pad offset in seconds; zero is preserved."
        },
        "nemotron_min_duration_on": {
          "type": "number",
          "default": 0.511,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA min duration on in seconds; zero is preserved."
        },
        "nemotron_min_duration_off": {
          "type": "number",
          "default": 0.296,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA min duration off in seconds; zero is preserved."
        }
      },
      "required": [
        "media"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "diarization_engine": {
                "const": "nemotron3"
              }
            },
            "required": [
              "diarization_engine"
            ]
          },
          "then": {
            "properties": {
              "speaker_count": {
                "const": 0
              },
              "min_speakers": {
                "const": 1
              },
              "max_speakers": {
                "const": 16
              },
              "segmentation_batch_size": {
                "const": 1
              },
              "embedding_batch_size": {
                "const": 8
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "diarization_engine": {
                "const": "nemotron3"
              },
              "nemotron_mode": {
                "const": "full"
              }
            },
            "required": [
              "diarization_engine",
              "nemotron_mode"
            ]
          },
          "then": {
            "properties": {
              "nemotron_preset": {
                "const": "v3-offline"
              },
              "nemotron_chunk": {
                "const": 340
              },
              "nemotron_right_context": {
                "const": 40
              },
              "nemotron_left_context": {
                "const": -1
              },
              "nemotron_fifo": {
                "const": 40
              },
              "nemotron_spkcache": {
                "const": 264
              },
              "nemotron_update_period": {
                "const": 300
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "diarization_engine": {
                "const": "nemotron3"
              },
              "nemotron_preset": {
                "enum": [
                  "v3-offline",
                  "v3-streaming"
                ]
              }
            },
            "required": [
              "diarization_engine",
              "nemotron_preset"
            ]
          },
          "then": {
            "properties": {
              "nemotron_chunk": {
                "const": 340
              },
              "nemotron_right_context": {
                "const": 40
              },
              "nemotron_left_context": {
                "const": -1
              },
              "nemotron_fifo": {
                "const": 40
              },
              "nemotron_spkcache": {
                "const": 264
              },
              "nemotron_update_period": {
                "const": 300
              }
            }
          }
        }
      ]
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Versioned subtitle JSON, cues and original word timings. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "srt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 SubRip subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "vtt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 WebVTT subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "cueCount": {
          "type": "integer"
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      },
      "required": [
        "document",
        "srt",
        "vtt",
        "cueCount",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 4294967296,
      "diskBytes": 134217728,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "exclusiveGroups": [
      "phonon",
      "speaker-diarization"
    ],
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU",
          "CUDA"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [
      {
        "id": "srt",
        "type": "File",
        "mimeType": "application/x-subrip",
        "fileExtension": ".srt",
        "description": "UTF-8 SubRip subtitles; timing in seconds."
      },
      {
        "id": "vtt",
        "type": "File",
        "mimeType": "text/vtt",
        "fileExtension": ".vtt",
        "description": "UTF-8 WebVTT subtitles."
      },
      {
        "id": "document",
        "type": "File",
        "mimeType": "application/json",
        "fileExtension": ".json",
        "description": "cytools-subtitles v1; words, cues, source stream metadata and warnings."
      }
    ]
  },
  {
    "id": "inspect_media",
    "name": "Inspect media / audio excerpt",
    "description": "Read source streams and dimensions; optionally export a bounded WAV excerpt and waveform for listening and AI review.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "media": {
          "type": "string",
          "minLength": 1,
          "description": "Local audio/video. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "start": {
          "type": "number",
          "default": 0,
          "minimum": 0,
          "maximum": 86400,
          "description": "Start time in seconds from media start."
        },
        "duration": {
          "type": "number",
          "default": 15,
          "minimum": 0.1,
          "maximum": 120,
          "description": "Audio excerpt duration in seconds, at most 120."
        },
        "audio_stream": {
          "type": "integer",
          "default": 0,
          "minimum": 0,
          "maximum": 31,
          "description": "Zero-based audio-track ordinal, independent of the global stream index."
        },
        "excerpt": {
          "type": "boolean",
          "default": true,
          "description": "Write a bounded WAV excerpt for listening and a peak waveform."
        }
      },
      "required": [
        "media"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "durationSeconds": {
          "type": "number",
          "minimum": 0
        },
        "streams": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "index": {
                "type": "integer"
              },
              "type": {
                "type": "string",
                "enum": [
                  "audio",
                  "video"
                ]
              },
              "codec": {
                "type": "string"
              },
              "width": {
                "type": "integer"
              },
              "height": {
                "type": "integer"
              },
              "sampleRate": {
                "type": "integer"
              },
              "channels": {
                "type": "integer"
              }
            },
            "required": [
              "index",
              "type",
              "codec"
            ],
            "additionalProperties": false
          }
        },
        "excerpt": {
          "type": "string",
          "x-cy-kind": "File",
          "description": "Mono PCM WAV file."
        },
        "excerptStartSeconds": {
          "type": "number"
        },
        "waveform": {
          "type": "array",
          "items": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        }
      },
      "required": [
        "durationSeconds",
        "streams"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 67108864,
      "diskBytes": 134217728,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [
      {
        "id": "excerpt",
        "type": "File",
        "mimeType": "audio/wav",
        "fileExtension": ".wav",
        "optional": true,
        "description": "Bounded mono 16 kHz PCM excerpt; original start in excerptStartSeconds."
      }
    ]
  },
  {
    "id": "read_subtitles",
    "name": "Read subtitle cues",
    "description": "Read a paginated time range of cues and original word timings for AI correction.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Subtitle JSON. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "start": {
          "type": "number",
          "default": 0,
          "minimum": 0,
          "maximum": 86400,
          "description": "Start time in seconds from media start."
        },
        "end": {
          "type": "number",
          "default": 86400,
          "minimum": 0.001,
          "maximum": 86400,
          "description": "Exclusive end time in seconds from media start."
        },
        "offset": {
          "type": "integer",
          "default": 0,
          "minimum": 0,
          "maximum": 100000,
          "description": "Pagination offset."
        },
        "limit": {
          "type": "integer",
          "default": 100,
          "minimum": 1,
          "maximum": 1000,
          "description": "Maximum page size."
        }
      },
      "required": [
        "document"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "cues": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              },
              "start": {
                "type": "number",
                "minimum": 0
              },
              "end": {
                "type": "number",
                "exclusiveMinimum": 0
              },
              "text": {
                "type": "string"
              },
              "kind": {
                "type": "string",
                "enum": [
                  "speech",
                  "sound"
                ]
              },
              "speaker": {
                "type": [
                  "string",
                  "null"
                ]
              },
              "speakerManual": {
                "type": "boolean"
              },
              "speakerCandidates": {
                "type": "array",
                "items": {
                  "type": "string"
                },
                "maxItems": 32
              },
              "speakerOverlapFraction": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
              }
            },
            "required": [
              "id",
              "start",
              "end",
              "text"
            ],
            "additionalProperties": false
          }
        },
        "total": {
          "type": "integer"
        },
        "words": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "text": {
                "type": "string"
              },
              "start": {
                "type": "number",
                "minimum": 0,
                "description": "Seconds from source start."
              },
              "end": {
                "type": "number",
                "minimum": 0,
                "description": "Seconds from source start."
              }
            },
            "required": [
              "text",
              "start",
              "end"
            ],
            "additionalProperties": false
          }
        },
        "totalWords": {
          "type": "integer"
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object"
          }
        },
        "speakers": {
          "type": "array",
          "items": {
            "type": "object"
          }
        },
        "speakerLabels": {
          "type": "boolean"
        }
      },
      "required": [
        "cues",
        "total",
        "words",
        "totalWords",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 67108864,
      "diskBytes": 134217728,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": []
  },
  {
    "id": "edit_subtitles",
    "name": "Edit / retime / add sounds",
    "description": "Patch cue text/times by stable ID, add timed sound descriptions, delete cues or shift the track; creates a new bundle and preserves the original.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Subtitle JSON. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "edits": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string",
                "minLength": 1
              },
              "start": {
                "type": "number",
                "minimum": 0
              },
              "end": {
                "type": "number",
                "exclusiveMinimum": 0
              },
              "text": {
                "type": "string",
                "minLength": 1,
                "maxLength": 10000
              },
              "kind": {
                "type": "string",
                "enum": [
                  "speech",
                  "sound"
                ]
              },
              "delete": {
                "type": "boolean"
              },
              "speaker": {
                "type": [
                  "string",
                  "null"
                ],
                "maxLength": 64,
                "description": "Speaker registry ID, or null to clear. Marks a manual assignment."
              }
            },
            "required": [
              "id"
            ],
            "additionalProperties": false
          },
          "default": [],
          "maxItems": 10000
        },
        "offset_seconds": {
          "type": "number",
          "default": 0,
          "minimum": -86400,
          "maximum": 86400,
          "description": "Signed cue-track offset in seconds; original word evidence is retained."
        }
      },
      "required": [
        "document"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Versioned subtitle JSON, cues and original word timings. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "srt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 SubRip subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "vtt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 WebVTT subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "cueCount": {
          "type": "integer"
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      },
      "required": [
        "document",
        "srt",
        "vtt",
        "cueCount",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 67108864,
      "diskBytes": 134217728,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [
      {
        "id": "srt",
        "type": "File",
        "mimeType": "application/x-subrip",
        "fileExtension": ".srt",
        "description": "UTF-8 SubRip subtitles; timing in seconds."
      },
      {
        "id": "vtt",
        "type": "File",
        "mimeType": "text/vtt",
        "fileExtension": ".vtt",
        "description": "UTF-8 WebVTT subtitles."
      },
      {
        "id": "document",
        "type": "File",
        "mimeType": "application/json",
        "fileExtension": ".json",
        "description": "cytools-subtitles v1; words, cues, source stream metadata and warnings."
      }
    ]
  },
  {
    "id": "reflow_subtitles",
    "name": "Rebuild cue layout",
    "description": "Rebuild readable cues from original word timestamps while preserving manually added sound descriptions. Manual speech text changes are replaced by original words.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Subtitle JSON. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "max_chars": {
          "type": "integer",
          "default": 42,
          "minimum": 10,
          "maximum": 100,
          "description": "Maximum characters per line; long unbreakable words are preserved."
        },
        "max_lines": {
          "type": "integer",
          "default": 2,
          "minimum": 1,
          "maximum": 4,
          "description": "Maximum lines per speech cue."
        },
        "max_duration": {
          "type": "number",
          "default": 6,
          "minimum": 0.5,
          "maximum": 20,
          "description": "Target maximum speech cue duration in seconds; a single word is never split."
        },
        "pause": {
          "type": "number",
          "default": 0.65,
          "minimum": 0.1,
          "maximum": 5,
          "description": "Split speech after a silence gap of at least this many seconds."
        },
        "auto_timing": {
          "type": "boolean",
          "default": true,
          "description": "Automatically repair reading time after transcription/reflow. Native word evidence stays unchanged; unresolved warnings remain visible."
        },
        "max_cps": {
          "type": "number",
          "default": 22,
          "minimum": 5,
          "maximum": 40,
          "description": "Target maximum readable characters per second. Unavoidable violations remain reported."
        },
        "min_duration": {
          "type": "number",
          "default": 0.8,
          "minimum": 0.2,
          "maximum": 3,
          "description": "Target minimum cue display duration in seconds, subject to synchronization limits."
        },
        "max_advance": {
          "type": "number",
          "default": 0.25,
          "minimum": 0,
          "maximum": 1,
          "description": "Maximum seconds a caption may start early or end earlier than its source cue."
        },
        "max_delay": {
          "type": "number",
          "default": 0.5,
          "minimum": 0,
          "maximum": 2,
          "description": "Maximum permitted delay of cue onset in seconds; never accumulated across the track."
        },
        "max_extension": {
          "type": "number",
          "default": 2,
          "minimum": 0,
          "maximum": 3,
          "description": "Maximum seconds to extend a cue end, without overlapping another speech caption or exceeding media duration."
        },
        "min_gap": {
          "type": "number",
          "default": 0.04,
          "minimum": 0,
          "maximum": 0.5,
          "description": "Minimum separation between speech captions in seconds."
        },
        "merge_fragments": {
          "type": "boolean",
          "default": true,
          "description": "Combine nearby short/fast/overlapping speech cues when the line and duration bounds permit; retain every word."
        }
      },
      "required": [
        "document"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Versioned subtitle JSON, cues and original word timings. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "srt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 SubRip subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "vtt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 WebVTT subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "cueCount": {
          "type": "integer"
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      },
      "required": [
        "document",
        "srt",
        "vtt",
        "cueCount",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 67108864,
      "diskBytes": 134217728,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [
      {
        "id": "srt",
        "type": "File",
        "mimeType": "application/x-subrip",
        "fileExtension": ".srt",
        "description": "UTF-8 SubRip subtitles; timing in seconds."
      },
      {
        "id": "vtt",
        "type": "File",
        "mimeType": "text/vtt",
        "fileExtension": ".vtt",
        "description": "UTF-8 WebVTT subtitles."
      },
      {
        "id": "document",
        "type": "File",
        "mimeType": "application/json",
        "fileExtension": ".json",
        "description": "cytools-subtitles v1; words, cues, source stream metadata and warnings."
      }
    ]
  },
  {
    "id": "repair_subtitles",
    "name": "Repair subtitle reading time",
    "description": "Preserve current speech text and original words, merge compatible fragments and fix overlaps/short display within explicit synchronization limits. Sound captions stay unchanged; remaining fast dialogue is reported.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Subtitle JSON. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "max_chars": {
          "type": "integer",
          "default": 42,
          "minimum": 10,
          "maximum": 100,
          "description": "Maximum characters per line; long unbreakable words are preserved."
        },
        "max_lines": {
          "type": "integer",
          "default": 2,
          "minimum": 1,
          "maximum": 4,
          "description": "Maximum lines per speech cue."
        },
        "max_duration": {
          "type": "number",
          "default": 6,
          "minimum": 0.5,
          "maximum": 20,
          "description": "Target maximum speech cue duration in seconds; a single word is never split."
        },
        "pause": {
          "type": "number",
          "default": 0.65,
          "minimum": 0.1,
          "maximum": 5,
          "description": "Split speech after a silence gap of at least this many seconds."
        },
        "max_cps": {
          "type": "number",
          "default": 22,
          "minimum": 5,
          "maximum": 40,
          "description": "Target maximum readable characters per second. Unavoidable violations remain reported."
        },
        "min_duration": {
          "type": "number",
          "default": 0.8,
          "minimum": 0.2,
          "maximum": 3,
          "description": "Target minimum cue display duration in seconds, subject to synchronization limits."
        },
        "max_advance": {
          "type": "number",
          "default": 0.25,
          "minimum": 0,
          "maximum": 1,
          "description": "Maximum seconds a caption may start early or end earlier than its source cue."
        },
        "max_delay": {
          "type": "number",
          "default": 0.5,
          "minimum": 0,
          "maximum": 2,
          "description": "Maximum permitted delay of cue onset in seconds; never accumulated across the track."
        },
        "max_extension": {
          "type": "number",
          "default": 2,
          "minimum": 0,
          "maximum": 3,
          "description": "Maximum seconds to extend a cue end, without overlapping another speech caption or exceeding media duration."
        },
        "min_gap": {
          "type": "number",
          "default": 0.04,
          "minimum": 0,
          "maximum": 0.5,
          "description": "Minimum separation between speech captions in seconds."
        },
        "merge_fragments": {
          "type": "boolean",
          "default": true,
          "description": "Combine nearby short/fast/overlapping speech cues when the line and duration bounds permit; retain every word."
        }
      },
      "required": [
        "document"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Versioned subtitle JSON, cues and original word timings. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "srt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 SubRip subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "vtt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 WebVTT subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "cueCount": {
          "type": "integer"
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      },
      "required": [
        "document",
        "srt",
        "vtt",
        "cueCount",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 134217728,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [
      {
        "id": "srt",
        "type": "File",
        "mimeType": "application/x-subrip",
        "fileExtension": ".srt",
        "description": "UTF-8 SubRip subtitles; timing in seconds."
      },
      {
        "id": "vtt",
        "type": "File",
        "mimeType": "text/vtt",
        "fileExtension": ".vtt",
        "description": "UTF-8 WebVTT subtitles."
      },
      {
        "id": "document",
        "type": "File",
        "mimeType": "application/json",
        "fileExtension": ".json",
        "description": "cytools-subtitles v1; words, cues, source stream metadata and warnings."
      }
    ]
  },
  {
    "id": "model_status",
    "name": "Model status",
    "description": "Report verified installed Phonon model references, dependencies and CPU transcription support.",
    "inputSchema": {
      "type": "object",
      "properties": {},
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "device": {
          "const": "cpu"
        },
        "models": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              },
              "installed": {
                "type": "boolean"
              }
            },
            "required": [
              "id",
              "installed"
            ]
          }
        },
        "fermionVersion": {
          "type": "string"
        },
        "loraSupported": {
          "const": false
        }
      },
      "required": [
        "device",
        "models",
        "fermionVersion",
        "loraSupported"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 67108864,
      "diskBytes": 134217728,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": []
  },
  {
    "id": "install_model",
    "name": "Download / repair model",
    "description": "Explicit public CC-BY-4.0 model download, verification and reference registration using pinned Fermion. No credentials in parameters.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string",
          "enum": [
            "phonon-2",
            "phonon-2.5",
            "phonon-2.5-en"
          ],
          "default": "phonon-2",
          "description": "Phonon-2 and 2.5-en: English only. Phonon-2.5: multilingual including French."
        },
        "license_accepted": {
          "type": "boolean",
          "default": false
        }
      },
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string"
        },
        "sha256": {
          "type": "object",
          "additionalProperties": {
            "type": "string",
            "pattern": "^[a-f0-9]{64}$"
          }
        },
        "format": {
          "const": "fermion-five-value-parakeet-v1"
        },
        "verifiedBy": {
          "type": "string"
        },
        "license": {
          "type": "string"
        }
      },
      "required": [
        "path",
        "sha256",
        "format",
        "verifiedBy",
        "license"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 4294967296,
      "diskBytes": 2147483648,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [
      "network"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "exclusiveGroups": [
      "phonon"
    ],
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": []
  },
  {
    "id": "register_local_model",
    "name": "Register local Phonon model",
    "description": "Verify and reference a local Phonon-2 family directory in place; no weights copied, no LoRA. Used by local_model in transcribe.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "minLength": 1
        },
        "name": {
          "type": "string",
          "minLength": 1
        },
        "model": {
          "type": "string",
          "enum": [
            "phonon-2",
            "phonon-2.5",
            "phonon-2.5-en"
          ],
          "default": "phonon-2"
        },
        "license": {
          "type": "string",
          "default": "Not declared"
        },
        "source": {
          "type": "string",
          "default": ""
        }
      },
      "required": [
        "path",
        "name"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string"
        },
        "path": {
          "type": "string"
        },
        "sha256": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        },
        "format": {
          "const": "fermion-five-value-parakeet-v1"
        },
        "name": {
          "type": "string"
        },
        "model": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "source": {
          "type": "string"
        }
      },
      "required": [
        "id",
        "path",
        "sha256",
        "format",
        "name",
        "model",
        "license",
        "source"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 33554432,
      "diskBytes": 1048576
    },
    "supportedBackends": [],
    "permissions": [],
    "exclusiveGroups": [
      "phonon"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": []
  },
  {
    "id": "runtime_status",
    "name": "Check PyTorch installation",
    "description": "Inspect private PyTorch package availability without importing Torch or downloading files.",
    "inputSchema": {
      "type": "object",
      "properties": {},
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "component": {
          "const": "pytorch"
        },
        "state": {
          "enum": [
            "Installed",
            "Missing"
          ]
        },
        "ready": {
          "type": "boolean"
        },
        "expectedVersion": {
          "type": "string"
        },
        "version": {
          "type": "string"
        },
        "packages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string"
              },
              "expectedVersion": {
                "type": "string"
              },
              "version": {
                "type": "string"
              },
              "installed": {
                "type": "boolean"
              }
            },
            "required": [
              "name",
              "expectedVersion",
              "version",
              "installed"
            ],
            "additionalProperties": false
          }
        },
        "path": {
          "type": "string"
        },
        "source": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "licenseUrl": {
          "type": "string"
        },
        "probeVerified": {
          "type": "boolean"
        }
      },
      "required": [
        "component",
        "state",
        "ready",
        "expectedVersion",
        "version",
        "packages",
        "path",
        "source",
        "license",
        "licenseUrl",
        "probeVerified"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 16777216,
      "diskBytes": 0,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": []
  },
  {
    "id": "install_runtime",
    "name": "Download / repair PyTorch",
    "description": "Download fixed CPU PyTorch and its optional dependencies into a new private directory; verify before atomic activation. No models, drivers or CUDA libraries are moved.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "license_accepted": {
          "type": "boolean",
          "default": false
        },
        "repair": {
          "type": "boolean",
          "default": false
        }
      },
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "component": {
          "const": "pytorch"
        },
        "state": {
          "enum": [
            "Installed",
            "Missing"
          ]
        },
        "ready": {
          "type": "boolean"
        },
        "expectedVersion": {
          "type": "string"
        },
        "version": {
          "type": "string"
        },
        "packages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string"
              },
              "expectedVersion": {
                "type": "string"
              },
              "version": {
                "type": "string"
              },
              "installed": {
                "type": "boolean"
              }
            },
            "required": [
              "name",
              "expectedVersion",
              "version",
              "installed"
            ],
            "additionalProperties": false
          }
        },
        "path": {
          "type": "string"
        },
        "source": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "licenseUrl": {
          "type": "string"
        },
        "probeVerified": {
          "type": "boolean"
        }
      },
      "required": [
        "component",
        "state",
        "ready",
        "expectedVersion",
        "version",
        "packages",
        "path",
        "source",
        "license",
        "licenseUrl",
        "probeVerified"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 2147483648,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [
      "network"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "phonon"
    ]
  },
  {
    "id": "diarization_status",
    "name": "Speaker diarization status",
    "description": "Optional Community-1 CPU runtime/model state; no engine imports and no network.",
    "inputSchema": {
      "type": "object",
      "properties": {},
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "runtimeReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "runtimePath": {
          "type": "string"
        },
        "modelPath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        },
        "credentialAvailable": {
          "type": "boolean"
        },
        "source": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "device": {
          "type": "string",
          "enum": [
            "cpu"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "runtimeReady",
        "modelReady",
        "ready",
        "runtimePath",
        "modelPath",
        "state",
        "credentialAvailable",
        "source",
        "license",
        "device"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 2147483648,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": []
  },
  {
    "id": "check_diarization_access",
    "name": "Check Community-1 access",
    "description": "Check existing protected Hugging Face credentials against the gated official revision. No token parameter.",
    "inputSchema": {
      "type": "object",
      "properties": {},
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "state": {
          "type": "string",
          "enum": [
            "Accessible",
            "AccessRequired"
          ]
        },
        "source": {
          "type": "string"
        },
        "message": {
          "type": "string"
        },
        "reason": {
          "type": "string",
          "enum": [
            "Authentication",
            "TokenPermissions",
            "Conditions"
          ]
        }
      },
      "required": [
        "state",
        "source"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 2147483648,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [
      "network"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "install_diarization_runtime",
    "name": "Install CPU diarization runtime",
    "description": "Download pinned, hashed Pyannote CPU dependencies into an isolated candidate. Preserve the prior active runtime on failure.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "license_accepted": {
          "type": "boolean",
          "default": false
        },
        "repair": {
          "type": "boolean",
          "default": false
        }
      },
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "runtimeReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "runtimePath": {
          "type": "string"
        },
        "modelPath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        },
        "credentialAvailable": {
          "type": "boolean"
        },
        "source": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "device": {
          "type": "string",
          "enum": [
            "cpu"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "runtimeReady",
        "modelReady",
        "ready",
        "runtimePath",
        "modelPath",
        "state",
        "credentialAvailable",
        "source",
        "license",
        "device"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 8589934592,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [
      "network"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "install_diarization_model",
    "name": "Install Community-1 model",
    "description": "Download the pinned official gated model after explicit conditions/license review. Uses protected local credentials; no token parameter.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "license_accepted": {
          "type": "boolean",
          "default": false
        },
        "repair": {
          "type": "boolean",
          "default": false
        }
      },
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "runtimeReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "runtimePath": {
          "type": "string"
        },
        "modelPath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        },
        "credentialAvailable": {
          "type": "boolean"
        },
        "source": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "device": {
          "type": "string",
          "enum": [
            "cpu"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "runtimeReady",
        "modelReady",
        "ready",
        "runtimePath",
        "modelPath",
        "state",
        "credentialAvailable",
        "source",
        "license",
        "device"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 8589934592,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [
      "network"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "register_diarization_model",
    "name": "Register local Community-1 model",
    "description": "Reference an official compatible local bundle in place; verify its files and checkpoint configuration.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "minLength": 1,
          "description": "Local model directory; model reference, not an input artifact."
        }
      },
      "required": [
        "path"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "runtimeReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "runtimePath": {
          "type": "string"
        },
        "modelPath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        },
        "credentialAvailable": {
          "type": "boolean"
        },
        "source": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "device": {
          "type": "string",
          "enum": [
            "cpu"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "runtimeReady",
        "modelReady",
        "ready",
        "runtimePath",
        "modelPath",
        "state",
        "credentialAvailable",
        "source",
        "license",
        "device"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 2147483648,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "diarize_subtitles",
    "name": "Identify subtitle speakers",
    "description": "Analyze voices globally with the selected local speaker engine and attach identities to a new subtitle bundle. Raw words and sound captions are preserved.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "media": {
          "type": "string",
          "minLength": 1,
          "x-cy-kind": "File",
          "description": "Source audio/video used for these subtitles. Absolute local paths are automatically imported privately."
        },
        "document": {
          "type": "string",
          "minLength": 1,
          "x-cy-kind": "File",
          "description": "Existing subtitle JSON; manual text and times are preserved unless rebuild is explicitly true. Absolute local paths are automatically imported privately."
        },
        "audio_stream": {
          "type": "integer",
          "default": 0,
          "minimum": 0,
          "maximum": 31,
          "description": "Zero-based audio-track ordinal, independent of the global stream index."
        },
        "threads": {
          "type": "integer",
          "default": 4,
          "minimum": 1,
          "maximum": 32,
          "description": "Phonon/Community-1 CPU threads; NVIDIA limits its worker and inherited native process to this many logical CPUs."
        },
        "speaker_count": {
          "type": "integer",
          "default": 0,
          "minimum": 0,
          "maximum": 32,
          "description": "Known number of voices; 0 enables automatic counting and min/max bounds. Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "min_speakers": {
          "type": "integer",
          "default": 1,
          "minimum": 1,
          "maximum": 32,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "max_speakers": {
          "type": "integer",
          "default": 16,
          "minimum": 1,
          "maximum": 32,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "diarization_max_seconds": {
          "type": "integer",
          "default": 14400,
          "minimum": 1,
          "maximum": 14400,
          "description": "Refuse longer audio before diarization; this is a processing bound, not an accuracy or performance guarantee."
        },
        "segmentation_batch_size": {
          "type": "integer",
          "default": 1,
          "minimum": 1,
          "maximum": 16,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "embedding_batch_size": {
          "type": "integer",
          "default": 8,
          "minimum": 1,
          "maximum": 64,
          "description": " Community-1 only; retain the default sentinel for NVIDIA, which automatically handles up to eight voices."
        },
        "speaker_labels": {
          "type": "boolean",
          "default": true,
          "description": "Include speaker display names in preview and SRT/VTT without changing cue text."
        },
        "rebuild": {
          "type": "boolean",
          "default": false,
          "description": "Rebuild speech from original word timings, splitting at voice changes. Replaces manual speech text/layout."
        },
        "replace_manual": {
          "type": "boolean",
          "default": false,
          "description": "Replace manually assigned cue speakers."
        },
        "max_chars": {
          "type": "integer",
          "default": 42,
          "minimum": 10,
          "maximum": 100,
          "description": "Maximum characters per line; long unbreakable words are preserved."
        },
        "max_lines": {
          "type": "integer",
          "default": 2,
          "minimum": 1,
          "maximum": 4,
          "description": "Maximum lines per speech cue."
        },
        "max_duration": {
          "type": "number",
          "default": 6,
          "minimum": 0.5,
          "maximum": 20,
          "description": "Target maximum speech cue duration in seconds; a single word is never split."
        },
        "pause": {
          "type": "number",
          "default": 0.65,
          "minimum": 0.1,
          "maximum": 5,
          "description": "Split speech after a silence gap of at least this many seconds."
        },
        "diarization_engine": {
          "type": "string",
          "enum": [
            "community1",
            "nemotron3"
          ],
          "default": "community1",
          "description": "Optional speaker analysis engine; Phonon remains the text/timing engine."
        },
        "nemotron_device": {
          "type": "string",
          "enum": [
            "cpu",
            "cuda"
          ],
          "default": "cpu",
          "description": "NVIDIA analysis device. CUDA means native CUDA device 0; no silent CPU fallback."
        },
        "nemotron_mode": {
          "type": "string",
          "enum": [
            "chunked",
            "full"
          ],
          "default": "chunked",
          "description": "Stateful chunked inference keeps global identities; full attention refuses audio over 360 seconds."
        },
        "nemotron_preset": {
          "type": "string",
          "enum": [
            "v3-offline",
            "v3-streaming",
            "custom"
          ],
          "default": "v3-offline",
          "description": "Quality-oriented chunked geometry, low-latency geometry, or explicit custom geometry. Full attention requires the default sentinel."
        },
        "nemotron_chunk": {
          "type": "integer",
          "default": 340,
          "minimum": 1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_right_context": {
          "type": "integer",
          "default": 40,
          "minimum": 0,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_left_context": {
          "type": "integer",
          "default": -1,
          "minimum": -1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_fifo": {
          "type": "integer",
          "default": 40,
          "minimum": 0,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_spkcache": {
          "type": "integer",
          "default": 264,
          "minimum": 1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_update_period": {
          "type": "integer",
          "default": 300,
          "minimum": 1,
          "maximum": 1024,
          "description": "Custom NVIDIA geometry in 80 ms encoder frames; only with the custom chunked preset. Otherwise keep its default."
        },
        "nemotron_onset": {
          "type": "number",
          "default": 0.641,
          "minimum": 0.001,
          "maximum": 1,
          "description": "Native NVIDIA onset probability."
        },
        "nemotron_offset": {
          "type": "number",
          "default": 0.561,
          "minimum": 0.001,
          "maximum": 1,
          "description": "Native NVIDIA offset probability."
        },
        "nemotron_pad_onset": {
          "type": "number",
          "default": 0.229,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA pad onset in seconds; zero is preserved."
        },
        "nemotron_pad_offset": {
          "type": "number",
          "default": 0.079,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA pad offset in seconds; zero is preserved."
        },
        "nemotron_min_duration_on": {
          "type": "number",
          "default": 0.511,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA min duration on in seconds; zero is preserved."
        },
        "nemotron_min_duration_off": {
          "type": "number",
          "default": 0.296,
          "minimum": 0,
          "maximum": 2,
          "description": "Native NVIDIA min duration off in seconds; zero is preserved."
        }
      },
      "required": [
        "media",
        "document"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "diarization_engine": {
                "const": "nemotron3"
              }
            },
            "required": [
              "diarization_engine"
            ]
          },
          "then": {
            "properties": {
              "speaker_count": {
                "const": 0
              },
              "min_speakers": {
                "const": 1
              },
              "max_speakers": {
                "const": 16
              },
              "segmentation_batch_size": {
                "const": 1
              },
              "embedding_batch_size": {
                "const": 8
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "diarization_engine": {
                "const": "nemotron3"
              },
              "nemotron_mode": {
                "const": "full"
              }
            },
            "required": [
              "diarization_engine",
              "nemotron_mode"
            ]
          },
          "then": {
            "properties": {
              "nemotron_preset": {
                "const": "v3-offline"
              },
              "nemotron_chunk": {
                "const": 340
              },
              "nemotron_right_context": {
                "const": 40
              },
              "nemotron_left_context": {
                "const": -1
              },
              "nemotron_fifo": {
                "const": 40
              },
              "nemotron_spkcache": {
                "const": 264
              },
              "nemotron_update_period": {
                "const": 300
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "diarization_engine": {
                "const": "nemotron3"
              },
              "nemotron_preset": {
                "enum": [
                  "v3-offline",
                  "v3-streaming"
                ]
              }
            },
            "required": [
              "diarization_engine",
              "nemotron_preset"
            ]
          },
          "then": {
            "properties": {
              "nemotron_chunk": {
                "const": 340
              },
              "nemotron_right_context": {
                "const": 40
              },
              "nemotron_left_context": {
                "const": -1
              },
              "nemotron_fifo": {
                "const": 40
              },
              "nemotron_spkcache": {
                "const": 264
              },
              "nemotron_update_period": {
                "const": 300
              }
            }
          }
        }
      ]
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Versioned subtitle JSON, cues and original word timings. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "srt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 SubRip subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "vtt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 WebVTT subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "cueCount": {
          "type": "integer"
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      },
      "required": [
        "document",
        "srt",
        "vtt",
        "cueCount",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 6442450944,
      "diskBytes": 2147483648,
      "cpuThreads": 4
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU",
          "CUDA"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [
      {
        "id": "srt",
        "type": "File",
        "mimeType": "application/x-subrip",
        "fileExtension": ".srt",
        "description": "UTF-8 SubRip subtitles; timing in seconds."
      },
      {
        "id": "vtt",
        "type": "File",
        "mimeType": "text/vtt",
        "fileExtension": ".vtt",
        "description": "UTF-8 WebVTT subtitles."
      },
      {
        "id": "document",
        "type": "File",
        "mimeType": "application/json",
        "fileExtension": ".json",
        "description": "cytools-subtitles v1; words, cues, source stream metadata and warnings."
      }
    ],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "rename_speakers",
    "name": "Rename subtitle speakers",
    "description": "Rename speaker display names and toggle labels without altering words, cue text or timing.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "x-cy-kind": "File",
          "description": "Subtitle JSON with speaker registry. Absolute local paths are automatically imported privately."
        },
        "names": {
          "type": "object",
          "maxProperties": 32,
          "additionalProperties": {
            "type": "string",
            "minLength": 1,
            "maxLength": 80
          }
        },
        "show_labels": {
          "type": "boolean",
          "default": true
        }
      },
      "required": [
        "document",
        "names"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "document": {
          "type": "string",
          "minLength": 1,
          "description": "Versioned subtitle JSON, cues and original word timings. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "srt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 SubRip subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "vtt": {
          "type": "string",
          "minLength": 1,
          "description": "UTF-8 WebVTT subtitles. Absolute local paths accepted; automatically imported into the private task.",
          "x-cy-kind": "File"
        },
        "cueCount": {
          "type": "integer"
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object"
          }
        }
      },
      "required": [
        "document",
        "srt",
        "vtt",
        "cueCount",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 2147483648,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "Linux",
        "architecture": "x64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      },
      {
        "os": "macOS",
        "architecture": "ARM64",
        "status": "Unknown",
        "computeBackends": [
          "CPU"
        ]
      }
    ],
    "outputs": [
      {
        "id": "srt",
        "type": "File",
        "mimeType": "application/x-subrip",
        "fileExtension": ".srt",
        "description": "UTF-8 SubRip subtitles; timing in seconds."
      },
      {
        "id": "vtt",
        "type": "File",
        "mimeType": "text/vtt",
        "fileExtension": ".vtt",
        "description": "UTF-8 WebVTT subtitles."
      },
      {
        "id": "document",
        "type": "File",
        "mimeType": "application/json",
        "fileExtension": ".json",
        "description": "cytools-subtitles v1; words, cues, source stream metadata and warnings."
      }
    ],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "nemotron_status",
    "name": "NVIDIA speaker engine status",
    "description": "Local native CPU/CUDA runtime and model presence, without neural or UI imports.",
    "inputSchema": {
      "type": "object",
      "properties": {},
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "quantization": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "source": {
          "type": "string"
        },
        "runtimeVersion": {
          "type": "string"
        },
        "cpuReady": {
          "type": "boolean"
        },
        "cudaReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "modelPath": {
          "type": "string"
        },
        "cpuRuntimePath": {
          "type": "string"
        },
        "cudaRuntimePath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "quantization",
        "license",
        "source",
        "runtimeVersion",
        "cpuReady",
        "cudaReady",
        "modelReady",
        "ready",
        "modelPath",
        "cpuRuntimePath",
        "cudaRuntimePath",
        "state"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 1073741824,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU",
          "CUDA"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": []
  },
  {
    "id": "nemotron_diagnostics",
    "name": "NVIDIA compute diagnostics",
    "description": "Probe the selected native runtime and report actual device and driver compatibility.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "backend": {
          "type": "string",
          "enum": [
            "cpu",
            "cuda"
          ],
          "default": "cpu"
        }
      },
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "version": {
          "type": "string"
        },
        "cudaAvailable": {
          "type": "boolean"
        },
        "devices": {
          "type": "array",
          "items": {
            "type": "object"
          }
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "required": [
        "version",
        "cudaAvailable",
        "devices",
        "warnings"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 1073741824,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU",
          "CUDA"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "install_nemotron_runtime",
    "name": "Install NVIDIA native runtime",
    "description": "Install a separately downloaded, pinned, hashed Windows CPU or CUDA runtime into an isolated verified candidate.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "license_accepted": {
          "type": "boolean",
          "default": false,
          "description": "Explicit user review/acceptance of the applicable OpenMDW or Apache/component license; never inferred."
        },
        "repair": {
          "type": "boolean",
          "default": false
        },
        "backend": {
          "type": "string",
          "enum": [
            "cpu",
            "cuda"
          ],
          "default": "cpu"
        }
      },
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "quantization": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "source": {
          "type": "string"
        },
        "runtimeVersion": {
          "type": "string"
        },
        "cpuReady": {
          "type": "boolean"
        },
        "cudaReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "modelPath": {
          "type": "string"
        },
        "cpuRuntimePath": {
          "type": "string"
        },
        "cudaRuntimePath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "quantization",
        "license",
        "source",
        "runtimeVersion",
        "cpuReady",
        "cudaReady",
        "modelReady",
        "ready",
        "modelPath",
        "cpuRuntimePath",
        "cudaRuntimePath",
        "state"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 1073741824,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [
      "network"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU",
          "CUDA"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "install_nemotron_model",
    "name": "Install NVIDIA Nemotron 3 model",
    "description": "Separately download the official pinned Q8_0 GGUF; preserve prior models and reject installation without explicit license acceptance.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "license_accepted": {
          "type": "boolean",
          "default": false,
          "description": "Explicit user review/acceptance of the applicable OpenMDW or Apache/component license; never inferred."
        },
        "repair": {
          "type": "boolean",
          "default": false
        }
      },
      "required": [],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "quantization": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "source": {
          "type": "string"
        },
        "runtimeVersion": {
          "type": "string"
        },
        "cpuReady": {
          "type": "boolean"
        },
        "cudaReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "modelPath": {
          "type": "string"
        },
        "cpuRuntimePath": {
          "type": "string"
        },
        "cudaRuntimePath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "quantization",
        "license",
        "source",
        "runtimeVersion",
        "cpuReady",
        "cudaReady",
        "modelReady",
        "ready",
        "modelPath",
        "cpuRuntimePath",
        "cudaRuntimePath",
        "state"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 1073741824,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [
      "network"
    ],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU",
          "CUDA"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  },
  {
    "id": "register_nemotron_model",
    "name": "Register local NVIDIA model",
    "description": "Reference the official compatible GGUF in place after verifying its exact size/hash; no move or network.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "minLength": 1,
          "description": "Local official GGUF file, referenced in place; not a task input."
        }
      },
      "required": [
        "path"
      ],
      "additionalProperties": false
    },
    "outputSchema": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string"
        },
        "revision": {
          "type": "string"
        },
        "quantization": {
          "type": "string"
        },
        "license": {
          "type": "string"
        },
        "source": {
          "type": "string"
        },
        "runtimeVersion": {
          "type": "string"
        },
        "cpuReady": {
          "type": "boolean"
        },
        "cudaReady": {
          "type": "boolean"
        },
        "modelReady": {
          "type": "boolean"
        },
        "ready": {
          "type": "boolean"
        },
        "modelPath": {
          "type": "string"
        },
        "cpuRuntimePath": {
          "type": "string"
        },
        "cudaRuntimePath": {
          "type": "string"
        },
        "state": {
          "type": "string",
          "enum": [
            "Installed",
            "Missing"
          ]
        }
      },
      "required": [
        "model",
        "revision",
        "quantization",
        "license",
        "source",
        "runtimeVersion",
        "cpuReady",
        "cudaReady",
        "modelReady",
        "ready",
        "modelPath",
        "cpuRuntimePath",
        "cudaRuntimePath",
        "state"
      ],
      "additionalProperties": false
    },
    "resourceRequirements": {
      "ramBytes": 536870912,
      "diskBytes": 1073741824,
      "cpuThreads": 1
    },
    "supportedBackends": [],
    "permissions": [],
    "canRunAsync": true,
    "canCancel": true,
    "supportsProgress": true,
    "platforms": [
      {
        "os": "Windows",
        "architecture": "x64",
        "status": "Experimental",
        "computeBackends": [
          "CPU",
          "CUDA"
        ]
      }
    ],
    "outputs": [],
    "exclusiveGroups": [
      "speaker-diarization"
    ]
  }
]
```

## Host project instructions

# Creating and maintaining CyTools_Subtitle

Mesh Tools must follow Docs/MeshViewer.md: use --desktop --mesh-viewer, open completed
results in the embedded viewport, provide orbit/free mouse-keyboard navigation,
close inspection, scene presets and studio/sun lighting. Static images are insufficient.

Read Docs/SharedInstallation.md. Provide configurable local/shared download storage
and explicit versioned CUDA Toolkit selection. Keep Python private, never move
existing models or accept provider terms implicitly. Expose access-required states
and official links to users and AI clients. Ship without weights and heavy caches.

Read README.md, CyTool.json and tool.py before modifying this tool.
Read Docs/Localization.md. English is the default UI language; French is selectable
and persisted. Options includes language, theme, text scale and component licenses.
Add every new visible string to app/locales/ui.json (en/fr); never translate user data.
Read Docs/GenerationConfigurations.md. Save/load configuration and optional generation
autosave are mandatory. Use explicit configure_generation callbacks; exclude secrets.
For desktop layout these files are inside app/. Read Docs/StandaloneDelivery.md too.
Every user-facing Tool must ship a usable Dear ImGui UI, a Windows .exe and a suitable
Linux launcher. Final root: launcher(s), LISEZ-MOI.md, app/, data/, runtime/ only.
Provide guided model access/download/resume in the UI and staged GitHub updates with
rollback and data preservation. Do not claim a scaffold is a finished application.
Read CyToolsGuide.md (local copy) or CyToolsCore Docs/AgentGuide.md as the implementation contract.
Run `cytools docs` to locate the complete documentation installed with the SDK.

1. Declare every operation in CyTool.json: inputSchema, outputSchema, supportedBackends,
   permissions, resourceRequirements and actual platform support.
2. Register one handler per declared operation in create_runtime().
3. Handler signature: handler(context, parameters) -> JSON-serializable outputs.
4. Check context.cancellation during loops; use context.cancellation.sleep() for waits.
5. Create outputs using context.path('outputs/name.ext'). Never share a fixed output path.
6. Use context.progress(percent, currentStep='...') when supportsProgress is true.
7. Use runtime.register(id, handler, estimate=...) for parameter-dependent RAM/VRAM.
8. Do not implement a second scheduler, job registry, authentication system or MCP parser.
9. No UI, specific AI model or external CLI is required by the core.
10. Treat external files and executable arguments as untrusted; use argv, never shell interpolation.
11. Add real operation tests (invalid inputs, failure, cancellation, output validity).
12. Run: cytools validate CyTool.json; python -m unittest -v; python tool.py describe;
    python tool.py invoke echo --params-file params.json.
13. Document dependencies, model licenses, platform verification and limitations honestly.
14. A descriptor does not implement a backend. Do not claim a capability without code and tests.

User operation parameters cannot choose clientId, owner or a different session.
Permissions belong to the authenticated transport context. Heavy/untrusted runtimes
belong in ProcessWorker; in-process cancellation is cooperative, not forcible.
# Standalone diagnostics and model extensions

Read Docs/StandaloneDiagnosticsAndModels.md. Ship a selectable/copyable application log,
explicit planned/actual video resolution, a local model library and compatible LoRA/device
controls. Save the effective selections in generation recipes. Do not claim unsupported
CPU paths, arbitrary architecture compatibility or generic four-step acceleration.


Lire [Docs/FullOperationAccess.md](Docs/FullOperationAccess.md) : inventaire des capacités natives, parité complète des options métier entre IA et standalone, contrats de sorties composables et preuves de validation. Un formulaire simplifié ne limite pas le contrat du Tool.

Lire Docs/AutomaticInputs.md (AutomaticInputs.md depuis Docs) : chemins absolus acceptés pour les entrées locales, copie automatique privée par job, aucune copie manuelle exigée de l’IA.


## Task-owned files (SDK 0.9.0)

Read Docs/TaskFiles.md (TaskFiles.md from this Docs directory). Configure input roots and all file fields for automatic imports; AI sessions are temporary by default. FinishTask removes imported copies and generated workspaces after workers stop; export wanted results first. Standalone sessions explicitly use temporary=False.

## Operation exclusion groups (SDK 0.10.0)

Read Docs/Scheduler.md. Declare operations[].exclusiveGroups for operations that must
serialize, including conflicting model maintenance. Use the SDK queue and keep RAM/VRAM
estimates; do not add another in-handler queue for the same Runtime. Test independent
operations and hold exclusion until execution/cleanup actually stops on cancellation.
Groups are runtime-local; keep interprocess locks when separate runtimes need them.
Require SDK 0.10.0 or later; older SDKs do not enforce this field.


## Native AI communication (Core 0.11.0)

The packaged CyMCPSDK 0.7.1 library implements CLI, JSONL, HTTP and MCP.
Call `ai_communication_status` with `includeOperations: true` for the effective complete
operation schemas, backends, permissions and resources. Use `DescribeOperation`,
`CanRun` and `EstimateResources` before `SubmitJob`; poll `GetJob` or consume `GetEvents`.
MCP provides `op_<operationId>` and the generic `cy_submit_job`; do not flatten or omit
advanced parameters. Absolute readable input paths are imported automatically.
AI sessions are temporary: export wanted results with `cy_export_job` before
`cy_finish_task`; a CLI invocation uses `--export-dir` to retain files.
Never use temporary output paths after task cleanup. Preserve explicit consent for
licences and destructive business actions; discovery does not grant permissions.
Existing application-owned model/provider adapters remain application-owned.
The native communication upgrade does not grant an agent extra filesystem rights.
For the first upgrade from Core 0.10.x use the full Windows package, which includes
the native library. Linux/macOS native builds require validation on those platforms.
