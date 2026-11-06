---
id: operation-install-nemotron-runtime
title: install_nemotron_runtime
description: Installer un runtime Windows CPU ou CUDA téléchargé et verifié séparément dans un candidat isolé et vérifié.
section: Référence
order: 200
parent: operations
sourceRevision: 88c01b06539c4b70
---

Installer un runtime Windows CPU ou CUDA téléchargé et verifié séparément dans un candidat isolé et vérifié.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | Non | Examen explicite et acceptation par l'utilisateur du licence OpenMDW ou Apache/component applicable; ne jamais inférer. `default=false` |
| `repair` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
| `backend` | `string` | Non | Voir les paramètres de l’opération. `default="cpu"`, `enum=["cpu", "cuda"]` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `model` | `string` | Oui | Voir les paramètres de l’opération.  |
| `revision` | `string` | Oui | Voir les paramètres de l’opération.  |
| `quantization` | `string` | Oui | Voir les paramètres de l’opération.  |
| `license` | `string` | Oui | Voir les paramètres de l’opération.  |
| `source` | `string` | Oui | Voir les paramètres de l’opération.  |
| `runtimeVersion` | `string` | Oui | Voir les paramètres de l’opération.  |
| `cpuReady` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `cudaReady` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `modelReady` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `ready` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `modelPath` | `string` | Oui | Voir les paramètres de l’opération.  |
| `cpuRuntimePath` | `string` | Oui | Voir les paramètres de l’opération.  |
| `cudaRuntimePath` | `string` | Oui | Voir les paramètres de l’opération.  |
| `state` | `string` | Oui | Voir les paramètres de l’opération. `enum=["Installed", "Missing"]` |

## Comportement et accès {#behaviour}

- Autorisations requises : `network`
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_nemotron_runtime
```
