---
id: operation-check-diarization-access
title: check_diarization_access
description: Check existing protected Hugging Face credentials against the gated official revision. No token parameter.
section: Reference
order: 200
parent: operations
revision: 21372a706cd52924
---

Check existing protected Hugging Face credentials against the gated official revision. No token parameter.

## Parameters {#contract}

No named fields are declared at this level. Inspect the operation schema with `describe-operation` for its exact shape.
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `state` | `string` | Yes | See the operation parameters. `enum=["Accessible", "AccessRequired"]` |
| `source` | `string` | Yes | See the operation parameters.  |
| `message` | `string` | No | See the operation parameters.  |
| `reason` | `string` | No | See the operation parameters. `enum=["Authentication", "TokenPermissions", "Conditions"]` |

## Behaviour and access {#behaviour}

- Required permissions: `network`
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation check_diarization_access
```
