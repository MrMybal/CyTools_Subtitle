---
id: operation-register-local-model
title: register_local_model
description: Verify and reference a local Phonon-2 family directory in place; no weights copied, no LoRA. Used by localmodel in transcribe.
section: Reference
order: 200
parent: operations
revision: 8e5fb184f875731f
---

Verify and reference a local Phonon-2 family directory in place; no weights copied, no LoRA. Used by local_model in transcribe.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `path` | `string` | Yes | See the operation parameters.  |
| `name` | `string` | Yes | See the operation parameters.  |
| `model` | `string` | No | See the operation parameters. `default="phonon-2"`, `enum=["phonon-2", "phonon-2.5", "phonon-2.5-en"]` |
| `license` | `string` | No | See the operation parameters. `default="Not declared"` |
| `source` | `string` | No | See the operation parameters. `default=""` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | Yes | See the operation parameters.  |
| `path` | `string` | Yes | See the operation parameters.  |
| `sha256` | `object` | Yes | See the operation parameters.  |
| `format` | `value` | Yes | See the operation parameters.  |
| `name` | `string` | Yes | See the operation parameters.  |
| `model` | `string` | Yes | See the operation parameters.  |
| `license` | `string` | Yes | See the operation parameters.  |
| `source` | `string` | Yes | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation register_local_model
```
