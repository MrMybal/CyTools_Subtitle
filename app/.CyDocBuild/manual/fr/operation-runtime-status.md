---
id: operation-runtime-status
title: runtime_status
description: Inspectez la disponibilité du paquet privé PyTorch sans importer Torch ou télécharger des fichiers.
section: Référence
order: 200
parent: operations
sourceRevision: 0c3d217a5e4894f1
---

Inspectez la disponibilité du paquet privé PyTorch sans importer Torch ou télécharger des fichiers.

## Paramètres {#contract}

Aucun champ nommé n’est déclaré à ce niveau. Consultez le schéma avec `describe-operation` pour connaître sa forme exacte.
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `component` | `value` | Oui | Voir les paramètres de l’opération.  |
| `state` | `value` | Oui | Voir les paramètres de l’opération. `enum=["Installed", "Missing"]` |
| `ready` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `expectedVersion` | `string` | Oui | Voir les paramètres de l’opération.  |
| `version` | `string` | Oui | Voir les paramètres de l’opération.  |
| `packages` | `array` | Oui | Voir les paramètres de l’opération.  |
| `path` | `string` | Oui | Voir les paramètres de l’opération.  |
| `source` | `string` | Oui | Voir les paramètres de l’opération.  |
| `license` | `string` | Oui | Voir les paramètres de l’opération.  |
| `licenseUrl` | `string` | Oui | Voir les paramètres de l’opération.  |
| `probeVerified` | `boolean` | Oui | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation runtime_status
```
