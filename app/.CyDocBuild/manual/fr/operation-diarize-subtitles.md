---
id: operation-diarize-subtitles
title: diarize_subtitles
description: Analysez les voix à l’échelle mondiale avec le moteur de locuteur sélectionné et attachez des identités à un nouveau bundle de sous-titres. Les mots bruts et les sous-titres sonores sont préservés.
section: Référence
order: 200
parent: operations
sourceRevision: 363a58e9277679bf
---

Analysez les voix à l’échelle mondiale avec le moteur de locuteur sélectionné et attachez des identités à un nouveau bundle de sous-titres. Les mots bruts et les sous-titres sonores sont préservés.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `media` | `string` | Oui | Le son d’origine audio/video utilisé pour ces sous-titres. Les chemins locaux absolus sont automatiquement importés de manière privée.  |
| `document` | `string` | Oui | Sous-titres existants JSON ; les textes et les horodatages manuels sont préservés sauf si rebuild est explicitement vrai. Les chemins locaux absolus sont automatiquement importés de manière privée.  |
| `audio_stream` | `integer` | Non | Ordinal de la piste sonore basé sur zéro, indépendant de l'indice global de flux. `default=0`, `minimum=0`, `maximum=31` |
| `threads` | `integer` | Non | Phonon/Community-1 CPU fils de discussion; NVIDIA limite le nombre de processeurs logiques auxquels est assigné le travail et le processus natif hérité. `default=4`, `minimum=1`, `maximum=32` |
| `speaker_count` | `integer` | Non | Nombre connu de voix ; 0 active le comptage automatique et les limites min/max. Seulement pour Community-1 ; conserve le sentinelle par défaut pour NVIDIA, qui gère automatiquement jusqu'à huit voix. `default=0`, `minimum=0`, `maximum=32` |
| `min_speakers` | `integer` | Non | Seulement pour Community-1 ; conserve le sentinelle par défaut pour NVIDIA, qui gère automatiquement jusqu'à huit voix. `default=1`, `minimum=1`, `maximum=32` |
| `max_speakers` | `integer` | Non | Seulement pour Community-1 ; conserve le sentinelle par défaut pour NVIDIA, qui gère automatiquement jusqu'à huit voix. `default=16`, `minimum=1`, `maximum=32` |
| `diarization_max_seconds` | `integer` | Non | Refuser un audio plus long avant la diarisation ; ceci est une limite de traitement, pas une garantie d'exactitude ou de performance. `default=14400`, `minimum=1`, `maximum=14400` |
| `segmentation_batch_size` | `integer` | Non | Seulement pour Community-1 ; conserve le sentinelle par défaut pour NVIDIA, qui gère automatiquement jusqu'à huit voix. `default=1`, `minimum=1`, `maximum=16` |
| `embedding_batch_size` | `integer` | Non | Seulement pour Community-1 ; conserve le sentinelle par défaut pour NVIDIA, qui gère automatiquement jusqu'à huit voix. `default=8`, `minimum=1`, `maximum=64` |
| `speaker_labels` | `boolean` | Non | Inclure les noms d'affichage des locuteurs dans la prévisualisation et SRT/VTT sans modifier le texte de l'indication. `default=true` |
| `rebuild` | `boolean` | Non | Reconstruisez l’speech à partir des horodatages originaux des mots, en divisant au changement de voix. Remplace le texte et le layout manuel de l’speech. `default=false` |
| `replace_manual` | `boolean` | Non | Remplacez les locuteurs de cahier de charges manuellement assignés. `default=false` |
| `max_chars` | `integer` | Non | Nombre maximum de caractères par ligne; les mots longs non brisables sont conservés. `default=42`, `minimum=10`, `maximum=100` |
| `max_lines` | `integer` | Non | Nombre maximum de lignes par indicateur de parole. `default=2`, `minimum=1`, `maximum=4` |
| `max_duration` | `number` | Non | Cible durée maximale en secondes d'un indicateur de parole; un mot ne est jamais divisé. `default=6`, `minimum=0.5`, `maximum=20` |
| `pause` | `number` | Non | Diviser la parole après un silence d'au moins cette durée en secondes. `default=0.65`, `minimum=0.1`, `maximum=5` |
| `diarization_engine` | `string` | Non | Optionnel moteur d'analyse vocale ; Phonon reste le moteur textes/temps. `default="community1"`, `enum=["community1", "nemotron3"]` |
| `nemotron_device` | `string` | Non | NVIDIA analyseur. CUDA signifie appareil natif CUDA 0 ; pas de rechute silencieuse CPU. `default="cpu"`, `enum=["cpu", "cuda"]` |
| `nemotron_mode` | `string` | Non | L'inference en morceaux étatue conserve les identités globales ; l'attention totale refuse l'audio au-delà de 360 secondes. `default="chunked"`, `enum=["chunked", "full"]` |
| `nemotron_preset` | `string` | Non | Géométrie en morceaux orientée vers la qualité, géométrie à faible latence, ou géométrie personnalisée explicite. L'attention totale nécessite le sentinel default. `default="v3-offline"`, `enum=["v3-offline", "v3-streaming", "custom"]` |
| `nemotron_chunk` | `integer` | Non | Géométrie en morceaux personnalisée NVIDIA dans des cadres d'encodeur de 80 ms ; uniquement avec la préétablie personnalisée chunked. Sinon, conservez sa valeur par défaut. `default=340`, `minimum=1`, `maximum=1024` |
| `nemotron_right_context` | `integer` | Non | Géométrie en morceaux personnalisée NVIDIA dans des cadres d'encodeur de 80 ms ; uniquement avec la préétablie personnalisée chunked. Sinon, conservez sa valeur par défaut. `default=40`, `minimum=0`, `maximum=1024` |
| `nemotron_left_context` | `integer` | Non | Géométrie en morceaux personnalisée NVIDIA dans des cadres d'encodeur de 80 ms ; uniquement avec la préétablie personnalisée chunked. Sinon, conservez sa valeur par défaut. `default=-1`, `minimum=-1`, `maximum=1024` |
| `nemotron_fifo` | `integer` | Non | Géométrie en morceaux personnalisée NVIDIA dans des cadres d'encodeur de 80 ms ; uniquement avec la préétablie personnalisée chunked. Sinon, conservez sa valeur par défaut. `default=40`, `minimum=0`, `maximum=1024` |
| `nemotron_spkcache` | `integer` | Non | Géométrie en morceaux personnalisée NVIDIA dans des cadres d'encodeur de 80 ms ; uniquement avec la préétablie personnalisée chunked. Sinon, conservez sa valeur par défaut. `default=264`, `minimum=1`, `maximum=1024` |
| `nemotron_update_period` | `integer` | Non | Géométrie en morceaux personnalisée NVIDIA dans des cadres d'encodeur de 80 ms ; uniquement avec la préétablie personnalisée chunked. Sinon, conservez sa valeur par défaut. `default=300`, `minimum=1`, `maximum=1024` |
| `nemotron_onset` | `number` | Non | Probabilité d'arrivée native NVIDIA. `default=0.641`, `minimum=0.001`, `maximum=1` |
| `nemotron_offset` | `number` | Non | Probabilité de fin native NVIDIA. `default=0.561`, `minimum=0.001`, `maximum=1` |
| `nemotron_pad_onset` | `number` | Non | Durée en secondes de l'encrage d'arrivée native NVIDIA ; la valeur zéro est préservée. `default=0.229`, `minimum=0`, `maximum=2` |
| `nemotron_pad_offset` | `number` | Non | Décalage natif NVIDIA en secondes; zéro est préservé. `default=0.079`, `minimum=0`, `maximum=2` |
| `nemotron_min_duration_on` | `number` | Non | Durée minimale native NVIDIA en secondes; zéro est préservé. `default=0.511`, `minimum=0`, `maximum=2` |
| `nemotron_min_duration_off` | `number` | Non | Durée minimale native NVIDIA de départ en secondes ; zéro est conservé. `default=0.296`, `minimum=0`, `maximum=2` |
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
runtime\python\Scripts\python.exe app\tool.py describe-operation diarize_subtitles
```
