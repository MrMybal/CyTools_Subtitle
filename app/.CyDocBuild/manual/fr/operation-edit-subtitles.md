---
id: operation-edit-subtitles
title: edit_subtitles
description: Corrige le texte/courtes de la piste par le modèle stable ID, ajoute des descriptions sonores temporisées, supprime des pistes ou déplace la piste; crée un nouveau lot et conserve l'original.
section: Référence
order: 200
parent: operations
sourceRevision: 35b617df296f3938
---

Corrige le texte/courtes de la piste par le modèle stable ID, ajoute des descriptions sonores temporisées, supprime des pistes ou déplace la piste; crée un nouveau lot et conserve l'original.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `document` | `string` | Oui | Sous-titrer JSON. Les chemins locaux absolu sont acceptés ; importé automatiquement dans la tâche privée.  |
| `edits` | `array` | Non | Voir les paramètres de l’opération. `default=[]` |
| `offset_seconds` | `number` | Non | Écart de piste de la piste signée en secondes; les preuves de mots originaux sont conservées. `default=0`, `minimum=-86400`, `maximum=86400` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `document` | `string` | Oui | Sous-titres versionnés JSON, indications et horaires originaux des mots. Les chemins locaux absolus sont acceptés ; ils sont automatiquement importés dans la tâche privée.  |
| `srt` | `string` | Oui | UTF-8 Sous-titres SubRip. Chemins locaux absolus acceptés ; importés automatiquement dans la tâche privée.  |
| `vtt` | `string` | Oui | UTF-8 sous-titres WebVTT. Chemins locaux absolus acceptés ; importés automatiquement dans la tâche privée.  |
| `cueCount` | `integer` | Oui | Voir les paramètres de l’opération.  |
| `warnings` | `array` | Oui | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation edit_subtitles
```
