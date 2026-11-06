---
id: operation-install-model
title: install_model
description: Explicit public CC-BY-4.0 model download, verification and reference registration using pinned Fermion. No credentials in parameters.
section: Reference
order: 200
parent: operations
revision: 293ea7fb9a55b2b4
---

Explicit public CC-BY-4.0 model download, verification and reference registration using pinned Fermion. No credentials in parameters.

## Parameters {#contract}

| Name | Type | Required | Description |
|---|---|---|---|
| `model` | `string` | No | Phonon-2 and 2.5-en: English only. Phonon-2.5: multilingual including French. `default="phonon-2"`, `enum=["phonon-2", "phonon-2.5", "phonon-2.5-en"]` |
| `license_accepted` | `boolean` | No | See the operation parameters. `default=false` |
## Returns {#returns}

| Name | Type | Required | Description |
|---|---|---|---|
| `path` | `string` | Yes | See the operation parameters.  |
| `sha256` | `object` | Yes | See the operation parameters.  |
| `format` | `value` | Yes | See the operation parameters.  |
| `verifiedBy` | `string` | Yes | See the operation parameters.  |
| `license` | `string` | Yes | See the operation parameters.  |

## Behaviour and access {#behaviour}

- Required permissions: `network`
- Backends: none declared.
- Cancellation: supported.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_model
```
