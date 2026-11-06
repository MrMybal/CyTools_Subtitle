---
id: operations
title: Automation and API
description: Connect a client and inspect the available operations.
section: Reference
order: 80
parent: overview
revision: bb824791d70b1993
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
