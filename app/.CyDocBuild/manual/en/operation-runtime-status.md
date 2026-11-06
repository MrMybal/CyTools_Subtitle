---
id: operation-runtime-status
title: runtime_status
description: Inspect private PyTorch package availability without importing Torch or downloading files.
section: Reference
order: 200
parent: operations
revision: 0c3d217a5e4894f1
---

Inspect private PyTorch package availability without importing Torch or downloading files.

## Parameters {#contract}

No named fields are declared at this level. Inspect the operation schema with `describe-operation` for its exact shape.
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

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation runtime_status
```
