---
id: operation-install-nemotron-runtime
title: install_nemotron_runtime
description: Install a separately downloaded, pinned, hashed Windows CPU or CUDA runtime into an isolated verified candidate.
section: Reference
order: 200
parent: operations
revision: 88c01b06539c4b70
---

Install a separately downloaded, pinned, hashed Windows CPU or CUDA runtime into an isolated verified candidate.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | No | Explicit user review/acceptance of the applicable OpenMDW or Apache/component license; never inferred. `default=false` |
| `repair` | `boolean` | No | See the operation parameters. `default=false` |
| `backend` | `string` | No | See the operation parameters. `default="cpu"`, `enum=["cpu", "cuda"]` |
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

- Required permissions: `network`
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_nemotron_runtime
```
