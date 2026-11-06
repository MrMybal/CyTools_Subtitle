---
id: operation-model-status
title: model_status
description: Report verified installed Phonon model references, dependencies and CPU transcription support.
section: Reference
order: 200
parent: operations
revision: ba6c12b6f492bd22
---

Report verified installed Phonon model references, dependencies and CPU transcription support.

## Parameters {#contract}

No named fields are declared at this level. Inspect the operation schema with `describe-operation` for its exact shape.
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `device` | `value` | Yes | See the operation parameters.  |
| `models` | `array` | Yes | See the operation parameters.  |
| `fermionVersion` | `string` | Yes | See the operation parameters.  |
| `loraSupported` | `value` | Yes | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: none declared.
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation model_status
```
