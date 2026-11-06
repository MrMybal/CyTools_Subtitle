---
id: operation-install-diarization-runtime
title: install_diarization_runtime
description: Download pinned, hashed Pyannote CPU dependencies into an isolated candidate. Preserve the prior active runtime on failure.
section: Reference
order: 200
parent: operations
revision: 758e09cef48ba867
---

Download pinned, hashed Pyannote CPU dependencies into an isolated candidate. Preserve the prior active runtime on failure.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | No | See the operation parameters. `default=false` |
| `repair` | `boolean` | No | See the operation parameters. `default=false` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `model` | `string` | Yes | See the operation parameters.  |
| `revision` | `string` | Yes | See the operation parameters.  |
| `runtimeReady` | `boolean` | Yes | See the operation parameters.  |
| `modelReady` | `boolean` | Yes | See the operation parameters.  |
| `ready` | `boolean` | Yes | See the operation parameters.  |
| `runtimePath` | `string` | Yes | See the operation parameters.  |
| `modelPath` | `string` | Yes | See the operation parameters.  |
| `state` | `string` | Yes | See the operation parameters. `enum=["Installed", "Missing"]` |
| `credentialAvailable` | `boolean` | Yes | See the operation parameters.  |
| `source` | `string` | Yes | See the operation parameters.  |
| `license` | `string` | Yes | See the operation parameters.  |
| `device` | `string` | Yes | See the operation parameters. `enum=["cpu"]` |

## Behaviour and access {#behaviour}

- Required permissions: `network`
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_diarization_runtime
```
