---
id: operation-nemotron-status
title: nemotron_status
description: Local native CPU/CUDA runtime and model presence, without neural or UI imports.
section: Reference
order: 200
parent: operations
revision: 9ce851a6db7489a8
---

Local native CPU/CUDA runtime and model presence, without neural or UI imports.

## Parameters {#contract}

No named fields are declared at this level. Inspect the operation schema with `describe-operation` for its exact shape.
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
runtime\python\Scripts\python.exe app\tool.py describe-operation nemotron_status
```
