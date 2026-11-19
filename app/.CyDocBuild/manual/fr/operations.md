---
id: operations
title: Automatisation et API
description: Connectez un client et consultez les opérations disponibles.
section: Référence
order: 80
parent: overview
sourceRevision: d03e85247b6df3e0
---

## Ligne de commande {#cli}

Depuis la racine de l’application, utilisez son interpréteur Python privé. `describe` et `list-operations` examinent le contrat public.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe
runtime\python\Scripts\python.exe app\tool.py list-operations
runtime\python\Scripts\python.exe app\tool.py invoke model_status --params "{}"
```

## MCP {#mcp}

Configurez votre client MCP pour lancer l’interpréteur privé avec `app/tool.py mcp`, en utilisant le dossier de l’application comme dossier de travail. Reconnectez-le lorsque le catalogue d’opérations exposées change.

## Fichiers des tâches {#task-files}

Les entrées locales acceptent des chemins absolus lisibles et sont importées automatiquement dans l’espace de la tâche. Exportez les résultats utiles avant de terminer la tâche. Ne réutilisez pas les chemins temporaires après nettoyage.

## Opérations {#operations}

- [`transcribe`](doc:operation-transcribe)
- [`inspect_media`](doc:operation-inspect-media)
- [`read_subtitles`](doc:operation-read-subtitles)
- [`edit_subtitles`](doc:operation-edit-subtitles)
- [`reflow_subtitles`](doc:operation-reflow-subtitles)
- [`repair_subtitles`](doc:operation-repair-subtitles)
- [`model_status`](doc:operation-model-status)
- [`install_model`](doc:operation-install-model)
- [`register_local_model`](doc:operation-register-local-model)
- [`runtime_status`](doc:operation-runtime-status)
- [`install_runtime`](doc:operation-install-runtime)
- [`diarization_status`](doc:operation-diarization-status)
- [`check_diarization_access`](doc:operation-check-diarization-access)
- [`install_diarization_runtime`](doc:operation-install-diarization-runtime)
- [`install_diarization_model`](doc:operation-install-diarization-model)
- [`register_diarization_model`](doc:operation-register-diarization-model)
- [`diarize_subtitles`](doc:operation-diarize-subtitles)
- [`rename_speakers`](doc:operation-rename-speakers)
- [`nemotron_status`](doc:operation-nemotron-status)
- [`nemotron_diagnostics`](doc:operation-nemotron-diagnostics)
- [`install_nemotron_runtime`](doc:operation-install-nemotron-runtime)
- [`install_nemotron_model`](doc:operation-install-nemotron-model)
- [`register_nemotron_model`](doc:operation-register-nemotron-model)


## Communication native {#native-communication}

Le paquet Windows contient CyToolsCore 0.11.0 et la bibliothèque de communication
native CyMCPSDK 0.7.1. Les mêmes paramètres complets des opérations sont disponibles
pour les clients IA et l’application autonome. Lancez `ai_communication_status` avec
`includeOperations: true` pour consulter le catalogue effectif. Cette opération ne
contacte aucun fournisseur IA et ne génère pas de contenu.

Les fichiers générés par la CLI sont temporaires par défaut. Ajoutez `--export-dir`
suivi d’un dossier absolu hors du stockage des jobs pour les conserver. Par MCP,
exportez avec `cy_export_job` avant `cy_finish_task`. Le nettoyage des tâches ne
supprime pas les entrées originales, modèles installés, conversations et documents
de projet persistants.

Pour la première migration depuis Core 0.10.x, installez le paquet Windows complet.
Une mise à jour de l’application seule ne peut pas ajouter la bibliothèque native
au précédent runtime. Les intégrations de modèles et de fournisseurs conservent
leurs compatibilités et permissions : cette mise à jour ne rend pas compatible un
modèle ou une plateforme non pris en charge.
