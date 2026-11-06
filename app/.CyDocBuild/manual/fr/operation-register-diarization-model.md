---
id: operation-register-diarization-model
title: register_diarization_model
description: Référencez un ensemble local compatible officiel en place; vérifiez ses fichiers et la configuration du checkpoint.
section: Référence
order: 200
parent: operations
sourceRevision: ee621d225e0361d7
---

Référencez un ensemble local compatible officiel en place; vérifiez ses fichiers et la configuration du checkpoint.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `path` | `string` | Oui | Répertoire de modèles local; référence de modèle, pas un artefact d'entrée.  |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `model` | `string` | Oui | Voir les paramètres de l’opération.  |
| `revision` | `string` | Oui | Voir les paramètres de l’opération.  |
| `runtimeReady` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `modelReady` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `ready` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `runtimePath` | `string` | Oui | Voir les paramètres de l’opération.  |
| `modelPath` | `string` | Oui | Voir les paramètres de l’opération.  |
| `state` | `string` | Oui | Voir les paramètres de l’opération. `enum=["Installed", "Missing"]` |
| `credentialAvailable` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `source` | `string` | Oui | Voir les paramètres de l’opération.  |
| `license` | `string` | Oui | Voir les paramètres de l’opération.  |
| `device` | `string` | Oui | Voir les paramètres de l’opération. `enum=["cpu"]` |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation register_diarization_model
```
