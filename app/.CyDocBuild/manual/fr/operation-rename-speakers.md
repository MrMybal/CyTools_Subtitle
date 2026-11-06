---
id: operation-rename-speakers
title: rename_speakers
description: Renommez les noms d’affichage des locuteurs et activez/désactivez les étiquettes sans modifier les mots, le texte de cahier de charges ou les horodatages.
section: Référence
order: 200
parent: operations
sourceRevision: d2dc5c46b3a114e3
---

Renommez les noms d’affichage des locuteurs et activez/désactivez les étiquettes sans modifier les mots, le texte de cahier de charges ou les horodatages.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `document` | `string` | Oui | Sous-titres JSON avec registre de locuteurs. Les chemins locaux absolus sont automatiquement importés de manière privée.  |
| `names` | `object` | Oui | Voir les paramètres de l’opération.  |
| `show_labels` | `boolean` | Non | Voir les paramètres de l’opération. `default=true` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation rename_speakers
```
