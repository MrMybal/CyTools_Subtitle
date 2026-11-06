---
id: operation-reflow-subtitles
title: reflow_subtitles
description: Reconstitue des indices de piste lus à partir des marques de temps de mots originaux tout en conservant les descriptions sonores manuellement ajoutées. Les modifications de texte de la parole manuelles sont remplacées par les…
section: Référence
order: 200
parent: operations
sourceRevision: 3ceb856787cdc7d0
---

Reconstitue des indices de piste lus à partir des marques de temps de mots originaux tout en conservant les descriptions sonores manuellement ajoutées. Les modifications de texte de la parole manuelles sont remplacées par les mots originaux.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `document` | `string` | Oui | Sous-titrer JSON. Les chemins locaux absolu sont acceptés ; importé automatiquement dans la tâche privée.  |
| `max_chars` | `integer` | Non | Nombre maximum de caractères par ligne; les mots longs non brisables sont conservés. `default=42`, `minimum=10`, `maximum=100` |
| `max_lines` | `integer` | Non | Nombre maximum de lignes par indicateur de parole. `default=2`, `minimum=1`, `maximum=4` |
| `max_duration` | `number` | Non | Cible durée maximale en secondes d'un indicateur de parole; un mot ne est jamais divisé. `default=6`, `minimum=0.5`, `maximum=20` |
| `pause` | `number` | Non | Diviser la parole après un silence d'au moins cette durée en secondes. `default=0.65`, `minimum=0.1`, `maximum=5` |
| `auto_timing` | `boolean` | Non | Réparer automatiquement le temps de lecture après la transcription/reflow. Les preuves de mots natifs restent inchangées; les avertissements non résolus restent visibles. `default=true` |
| `max_cps` | `number` | Non | Cible nombre maximum de caractères lisibles par seconde. Les violations inévitables restent signalées. `default=22`, `minimum=5`, `maximum=40` |
| `min_duration` | `number` | Non | Durée minimale cible d'affichage d'un indicateur, soumise aux limites de synchronisation. `default=0.8`, `minimum=0.2`, `maximum=3` |
| `max_advance` | `number` | Non | Secondes maximales d'avance possible d'un sous-titre par rapport à son indicateur source. `default=0.25`, `minimum=0`, `maximum=1` |
| `max_delay` | `number` | Non | Délai maximal d'attente de l'indicateur en secondes; ne jamais accumulé au fil de la piste. `default=0.5`, `minimum=0`, `maximum=2` |
| `max_extension` | `number` | Non | Secondes maximales pour étendre la fin d'une indication sonore, sans chevaucher une autre indication de parole ou dépasser la durée du média. `default=2`, `minimum=0`, `maximum=3` |
| `min_gap` | `number` | Non | Séparation minimale entre les indications de parole en secondes. `default=0.04`, `minimum=0`, `maximum=0.5` |
| `merge_fragments` | `boolean` | Non | Combiner les indications de parole voisines courtes/vite/chevauchantes lorsque les limites de ligne et de durée le permettent ; conserver chaque mot. `default=true` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation reflow_subtitles
```
