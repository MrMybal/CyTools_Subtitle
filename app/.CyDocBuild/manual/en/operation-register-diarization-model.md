---
id: operation-register-diarization-model
title: register_diarization_model
description: Reference an official compatible local bundle in place; verify its files and checkpoint configuration.
section: Reference
order: 200
parent: operations
revision: ee621d225e0361d7
---

Reference an official compatible local bundle in place; verify its files and checkpoint configuration.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `path` | `string` | Yes | Local model directory; model reference, not an input artifact.  |
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

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation register_diarization_model
```
