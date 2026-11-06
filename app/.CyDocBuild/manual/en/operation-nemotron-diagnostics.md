---
id: operation-nemotron-diagnostics
title: nemotron_diagnostics
description: Probe the selected native runtime and report actual device and driver compatibility.
section: Reference
order: 200
parent: operations
revision: 02ccb20e1981643a
---

Probe the selected native runtime and report actual device and driver compatibility.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `backend` | `string` | No | See the operation parameters. `default="cpu"`, `enum=["cpu", "cuda"]` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `version` | `string` | Yes | See the operation parameters.  |
| `cudaAvailable` | `boolean` | Yes | See the operation parameters.  |
| `devices` | `array` | Yes | See the operation parameters.  |
| `warnings` | `array` | Yes | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation nemotron_diagnostics
```
