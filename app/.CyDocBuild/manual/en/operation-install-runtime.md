---
id: operation-install-runtime
title: install_runtime
description: Download fixed CPU PyTorch and its optional dependencies into a new private directory; verify before atomic activation. No models, drivers or CUDA libraries are moved.
section: Reference
order: 200
parent: operations
revision: 9dd4260cd87b08aa
---

Download fixed CPU PyTorch and its optional dependencies into a new private directory; verify before atomic activation. No models, drivers or CUDA libraries are moved.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | No | See the operation parameters. `default=false` |
| `repair` | `boolean` | No | See the operation parameters. `default=false` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `component` | `value` | Yes | See the operation parameters.  |
| `state` | `value` | Yes | See the operation parameters. `enum=["Installed", "Missing"]` |
| `ready` | `boolean` | Yes | See the operation parameters.  |
| `expectedVersion` | `string` | Yes | See the operation parameters.  |
| `version` | `string` | Yes | See the operation parameters.  |
| `packages` | `array` | Yes | See the operation parameters.  |
| `path` | `string` | Yes | See the operation parameters.  |
| `source` | `string` | Yes | See the operation parameters.  |
| `license` | `string` | Yes | See the operation parameters.  |
| `licenseUrl` | `string` | Yes | See the operation parameters.  |
| `probeVerified` | `boolean` | Yes | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: `network`
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_runtime
```
