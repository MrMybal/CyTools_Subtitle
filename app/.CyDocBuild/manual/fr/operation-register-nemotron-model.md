---
id: operation-register-nemotron-model
title: register_nemotron_model
description: Référence du runtime officiel compatible GGUF après vérification de sa taille exacte/hachage; aucune déplacement ou réseau.
section: Référence
order: 200
parent: operations
sourceRevision: 515f72820ff9b940
---

Référence du runtime officiel compatible GGUF après vérification de sa taille exacte/hachage; aucune déplacement ou réseau.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `path` | `string` | Oui | Fichier officiel local GGUF, référencé en place; pas une entrée de tâche.  |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation register_nemotron_model
```
