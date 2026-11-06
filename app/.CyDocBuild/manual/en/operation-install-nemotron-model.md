---
id: operation-install-nemotron-model
title: install_nemotron_model
description: Separately download the official pinned Q80 GGUF; preserve prior models and reject installation without explicit license acceptance.
section: Reference
order: 200
parent: operations
revision: 27bd80d570498a52
---

Separately download the official pinned Q8_0 GGUF; preserve prior models and reject installation without explicit license acceptance.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | No | Explicit user review/acceptance of the applicable OpenMDW or Apache/component license; never inferred. `default=false` |
| `repair` | `boolean` | No | See the operation parameters. `default=false` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation install_nemotron_model
```
