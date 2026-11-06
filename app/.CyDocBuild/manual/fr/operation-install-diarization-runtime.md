---
id: operation-install-diarization-runtime
title: install_diarization_runtime
description: Téléchargez les dépendances hachées Pyannote CPU fixées dans un candidat isolé. Gardez le runtime actif précédent en cas d'échec.
section: Référence
order: 200
parent: operations
sourceRevision: 758e09cef48ba867
---

Téléchargez les dépendances hachées Pyannote CPU fixées dans un candidat isolé. Gardez le runtime actif précédent en cas d'échec.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
| `repair` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
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

- Autorisations requises : `network`
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_diarization_runtime
```
