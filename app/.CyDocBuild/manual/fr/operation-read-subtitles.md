---
id: operation-read-subtitles
title: read_subtitles
description: Lire un éventail paginé de cotes et des horodatages originaux des mots pour la correction de AI.
section: Référence
order: 200
parent: operations
sourceRevision: 145200797a2e5d38
---

Lire un éventail paginé de cotes et des horodatages originaux des mots pour la correction de AI.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `document` | `string` | Oui | Sous-titrer JSON. Les chemins locaux absolu sont acceptés ; importé automatiquement dans la tâche privée.  |
| `start` | `number` | Non | Temps de début en secondes depuis le début du média. `default=0`, `minimum=0`, `maximum=86400` |
| `end` | `number` | Non | Temps de fin exclusif en secondes depuis le début du média. `default=86400`, `minimum=0.001`, `maximum=86400` |
| `offset` | `integer` | Non | Décalage de pagination. `default=0`, `minimum=0`, `maximum=100000` |
| `limit` | `integer` | Non | Taille maximale de page. `default=100`, `minimum=1`, `maximum=1000` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `cues` | `array` | Oui | Voir les paramètres de l’opération.  |
| `total` | `integer` | Oui | Voir les paramètres de l’opération.  |
| `words` | `array` | Oui | Voir les paramètres de l’opération.  |
| `totalWords` | `integer` | Oui | Voir les paramètres de l’opération.  |
| `warnings` | `array` | Oui | Voir les paramètres de l’opération.  |
| `speakers` | `array` | Non | Voir les paramètres de l’opération.  |
| `speakerLabels` | `boolean` | Non | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation read_subtitles
```
