---
id: operations
title: Automation and API
description: Connect a client and inspect the available operations.
section: Reference
order: 80
parent: overview
revision: 961fb828285bf7e1
---

## Command line {#cli}

From the application root, use the private Python interpreter. `describe` and `list-operations` inspect the public contract.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe
runtime\python\Scripts\python.exe app\tool.py list-operations
runtime\python\Scripts\python.exe app\tool.py invoke model_status --params "{}"
```

## MCP {#mcp}

Configure your MCP client to start the private interpreter with `app/tool.py mcp`, using the application folder as its working directory. Restart the connection when its exposed operation catalogue changes.

## Task files {#task-files}

Local file inputs accept absolute readable paths and are imported into the task workspace automatically. Export wanted results before finishing the task. Do not rely on temporary paths after task cleanup.

## Operations {#operations}

- [`transcribe`](doc:operation-transcribe)
- [`inspect_media`](doc:operation-inspect-media)
- [`read_subtitles`](doc:operation-read-subtitles)
- [`edit_subtitles`](doc:operation-edit-subtitles)
- [`reflow_subtitles`](doc:operation-reflow-subtitles)
- [`repair_subtitles`](doc:operation-repair-subtitles)
- [`model_status`](doc:operation-model-status)
- [`install_model`](doc:operation-install-model)
- [`register_local_model`](doc:operation-register-local-model)
- [`runtime_status`](doc:operation-runtime-status)
- [`install_runtime`](doc:operation-install-runtime)
- [`diarization_status`](doc:operation-diarization-status)
- [`check_diarization_access`](doc:operation-check-diarization-access)
- [`install_diarization_runtime`](doc:operation-install-diarization-runtime)
- [`install_diarization_model`](doc:operation-install-diarization-model)
- [`register_diarization_model`](doc:operation-register-diarization-model)
- [`diarize_subtitles`](doc:operation-diarize-subtitles)
- [`rename_speakers`](doc:operation-rename-speakers)
- [`nemotron_status`](doc:operation-nemotron-status)
- [`nemotron_diagnostics`](doc:operation-nemotron-diagnostics)
- [`install_nemotron_runtime`](doc:operation-install-nemotron-runtime)
- [`install_nemotron_model`](doc:operation-install-nemotron-model)
- [`register_nemotron_model`](doc:operation-register-nemotron-model)


## Native communication {#native-communication}

The Windows package includes CyToolsCore 0.12.0 and the native CyMCPSDK 0.7.1
communication library. The same complete operation parameters are available to AI
clients and the standalone application. Run `ai_communication_status` with
`includeOperations: true` to inspect the effective catalogue. This does not contact
an AI provider or generate content.

CLI-generated files are temporary by default. Add `--export-dir` followed by an
absolute destination outside the job store when you want to keep them. In MCP,
export with `cy_export_job` before `cy_finish_task`. The original input file, installed
models, conversations and project documents are not removed by task cleanup.

For the first upgrade from a 0.10.x Core, install the full Windows package.
Application-only updates cannot add the required native library to an older runtime.
Model and provider integrations keep their existing compatibility and permissions;
this upgrade does not make an unsupported model or platform supported.


## Local MCP access {#local-mcp-access}

Core **0.12.0** embeds native CyMCPSDK commit **`34d4bca`**. From the Tool root, start
the local service explicitly:

```powershell
runtime/python/Scripts/python.exe app/tool.py --data-dir data/jobs serve --port 8766
```

Free is the initial profile: connect using only `http://127.0.0.1:8766/mcp`. All exposed
operations are callable without a token or additional transport approval. Arguments,
licence acceptance and explicit destructive-action confirmations remain business rules.
The portable API is at `/v1`; the listener binds only to 127.0.0.1.

Missing choices migrate to Free; explicit profiles are preserved. Use the server option
`--access-profile free`, `--access-profile local_controlled`, `--access-profile token_only`
or `--access-profile protected_access`. Local controlled applies host-selected permissions.
Token only and Protected require a valid token; Protected retains credential permissions.
With the command above, the choice persists in `data/jobs/communication.json`. Restart
the service to change the active profile. CLI/embedded and chat-provider permissions
are unchanged. Use `ai_communication_status` with `includeOperations: true` for discovery.

Install the full Windows package for this native runtime update; app-only updates reject
the old runtime ABI. For a local source upgrade, install the bundled wheel:

```powershell
runtime/python/Scripts/python.exe -m pip install --no-deps app/packages/cytools_core-0.12.0-py3-none-win_amd64.whl
```

Export wanted task files before `cy_finish_task`. Task cleanup preserves original inputs,
installed models, conversations and persistent project documents. Windows x64 is the
validated platform for this update; Linux/macOS native builds require target validation.
