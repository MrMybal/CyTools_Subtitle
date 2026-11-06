---
id: operation-register-nemotron-model
title: register_nemotron_model
description: Reference the official compatible GGUF in place after verifying its exact size/hash; no move or network.
section: Reference
order: 200
parent: operations
revision: 515f72820ff9b940
---

Reference the official compatible GGUF in place after verifying its exact size/hash; no move or network.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `path` | `string` | Yes | Local official GGUF file, referenced in place; not a task input.  |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `model` | `string` | Yes | See the operation parameters.  |
| `revision` | `string` | Yes | See the operation parameters.  |
| `quantization` | `string` | Yes | See the operation parameters.  |
| `license` | `string` | Yes | See the operation parameters.  |
| `source` | `string` | Yes | See the operation parameters.  |
| `runtimeVersion` | `string` | Yes | See the operation parameters.  |
| `cpuReady` | `boolean` | Yes | See the operation parameters.  |
| `cudaReady` | `boolean` | Yes | See the operation parameters.  |
| `modelReady` | `boolean` | Yes | See the operation parameters.  |
| `ready` | `boolean` | Yes | See the operation parameters.  |
| `modelPath` | `string` | Yes | See the operation parameters.  |
| `cpuRuntimePath` | `string` | Yes | See the operation parameters.  |
| `cudaRuntimePath` | `string` | Yes | See the operation parameters.  |
| `state` | `string` | Yes | See the operation parameters. `enum=["Installed", "Missing"]` |

## Behaviour and access {#behaviour}

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation register_nemotron_model
```
