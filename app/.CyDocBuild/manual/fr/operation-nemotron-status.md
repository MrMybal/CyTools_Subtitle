---
id: operation-nemotron-status
title: nemotron_status
description: Runtime local natif CPU/CUDA et présence du modèle, sans importation de neural ou de UI.
section: Référence
order: 200
parent: operations
sourceRevision: 9ce851a6db7489a8
---

Runtime local natif CPU/CUDA et présence du modèle, sans importation de neural ou de UI.

## Paramètres {#contract}

Aucun champ nommé n’est déclaré à ce niveau. Consultez le schéma avec `describe-operation` pour connaître sa forme exacte.
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

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation nemotron_status
```
