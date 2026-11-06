---
id: operation-inspect-media
title: inspect_media
description: Lire les flux sources et les dimensions ; exporter optionnellement un extrait limité WAV et une forme d'onde pour l'écoute et la revue AI.
section: Référence
order: 200
parent: operations
sourceRevision: 8c1b2cebea7ce23e
---

Lire les flux sources et les dimensions ; exporter optionnellement un extrait limité WAV et une forme d'onde pour l'écoute et la revue AI.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `media` | `string` | Oui | Audio/vidéo local. Les chemins locaux absolus sont acceptés ; ils sont automatiquement importés dans la tâche privée.  |
| `start` | `number` | Non | Temps de début en secondes depuis le début du média. `default=0`, `minimum=0`, `maximum=86400` |
| `duration` | `number` | Non | Durée de l'extrait audio en secondes, au maximum 120. `default=15`, `minimum=0.1`, `maximum=120` |
| `audio_stream` | `integer` | Non | Ordinal de la piste sonore basé sur zéro, indépendant de l'indice global de flux. `default=0`, `minimum=0`, `maximum=31` |
| `excerpt` | `boolean` | Non | Écrire un extrait limité WAV pour l'écoute et un profil d'amplitude maximale. `default=true` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `durationSeconds` | `number` | Oui | Voir les paramètres de l’opération. `minimum=0` |
| `streams` | `array` | Oui | Voir les paramètres de l’opération.  |
| `excerpt` | `string` | Non | Fichier mono PCM WAV.  |
| `excerptStartSeconds` | `number` | Non | Voir les paramètres de l’opération.  |
| `waveform` | `array` | Non | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation inspect_media
```
