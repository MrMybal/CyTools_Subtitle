---
id: guide-app-docs-nvidiadiarization
title: Optionnel NVIDIA Nemotron 3 — 0.6.0
description: Optionnel NVIDIA Nemotron 3 — 0.6.0
section: Guide
order: 40
parent: guide-lisez-moi
sourceRevision: 62c78e00a36441de
---

## Optionnel NVIDIA Nemotron 3 {#optional-nvidia-nemotron-3-0-6-0}

Ce composant attribue les voix ; Phonon fournit toujours le texte reconnu et les timestamps des mots originaux. Community-1 reste disponible séparément. NVIDIA utilise la runtime officielle native [NeMo-Speech.cpp v0.2.0](https://github.com/NVIDIA/NeMo-Speech.cpp/tree/v0.2.0), pas un autre environnement Python ML.

## Installation et licences {#installation-and-licenses}

L'archive de base ne contient aucun runtime ou poids de modèle NVIDIA. L'installation propose des téléchargements indépendants Windows x64 CPU et CUDA, des diagnostics natifs, un téléchargement de modèle et des références locales compatibles GGUF. Examinez les termes du runtime Apache 2.0 et le modèle [OpenMDW 1.1](https://openmdw.ai/license/1-1/) et cochez explicitement la case d'acceptation. Les opérations réseau nécessitent une autorisation réseau authentifiée et `license_accepted: true`; par défaut, false ne accepte pas les termes implicitement. Aucun accès token n'est requis pour ce modèle non encadré.

Le modèle officiel [modèle](https://huggingface.co/nvidia/Nemotron-3-Diarization) est fixé à la révision `f667ed73aee57d40cc39428eb768b4fd87a0a29e`, le fichier `Nemotron-3-Diarization.q8_0.gguf`, 107 012 128 octets, SHA256 `08456d9e22cd9a323c0364d98375f3746d6e68507ebb705cd46438c534c7a3a1`. C'est la quantisation Q8_0. Les hachages, les tailles et les URL du runtime archive sont dans `nemotron-catalog.json`. Le téléchargement CPU est d'environ 6 MB, CUDA d'environ 102 MB. Chaque archive native porte ses propres avis; la racine LICENCES inclut les termes de runtime, tierces parties et modèle avec des liens vers les sources upstream.

SDK InstallationStorage fournit un cache de téléchargement reprise vérifié. Les installations actives restent privées dans runtime/components/nemotron et data/models/nemotron; le partage du cache de téléchargement ne partage pas l'installation active. Un candidat frais est vérifié version/probe/hash avant l'activation atomique. Les échecs ou les annulations conservent le candidat actif précédent. L'enregistrement local vérifie l'exacte officielle GGUF sans la déplacer. Aucune modification de pilote, éditions globales PATH, remplacement Phonon/Pyannote torch ou déplacement du modèle ne se produisent.

## Options et traitement {#options-and-processing}

Activer l'identification de différents locuteurs et sélectionnez NVIDIA Nemotron 3, puis CPU ou CUDA. Les mêmes champs existent dans transcribe, diarize_subtitles, opérations avancées et configuration versionnée JSON. Charger une configuration ne démarre jamais une tâche. `nemotron_status` rapporte la présence locale sans importations d'engine; `nemotron_diagnostics` vérifie le runtime natif sélectionné et la compatibilité réelle du matériel. Une sélection CUDA échoue explicitement si elle n'est pas disponible plutôt que de retomber silencieusement sur CPU.

La qualité par défaut chunked `v3-offline` utilise des caches stateful Sortformer à travers l'enregistrement. `v3-streaming` favorise une latence plus basse; `custom` expose la taille du chunk, le contexte gauche/droite FIFO, la cache du locuteur et la géométrie de mise à jour dans des cadres natifs de 80 ms. Les options d'activité natives sont l'entrée, l'offset, l'entrée/offset padding et les durées minimales on/off. Les valeurs de padding/duration nulles sont valides. Les géométries surchargées nécessitent la préselection du chunked preset personnalisé; les options incompatibles sont rejetées avant soumission. L'attention totale utilise `--offline`, est limitée à 360 secondes et ne peut pas combiner avec un preset personnalisé/streaming. La limite totale de refus configurée est de quatre au maximum heures ; la mémoire, le temps et la précision au-delà ne sont pas certifiés.

L'engine détecte automatiquement jusqu'à huit voix anonymes. Les champs speaker-count/batch de Community-1 doivent rester à leurs valeurs sentinelles par défaut lorsque NVIDIA est sélectionné. Les threads de CPU définissent la capabilité de l'ouvrier one-shot en termes d'affinité CPU, héritée par le fils natif, plutôt que de prétendre à un flag de thread natif CLI inexistant. Le véritable appareil et la capabilité CPU sont enregistrés. Les ressources SDK réservent CPU/RAM et une estimation de CUDA VRAM avant l'exécution. Les estimations CUDA sont de 2 GiB pour les préréglages en morceaux nommés et de 6 GiB pour les complets/custumes ; la mémoire réelle dépend du travail.

Les fichiers mono 16 kHz PCM16 appartenant au travail et les fichiers de résultat temporaires utilisent JobContext.path. ProcessWorker possède le descendant natif, conserve les réservations jusqu'à l'arrêt et supprime les fichiers temporaires après l'arrêt. Aucun UI ou importation neuronale ne pénètre dans le module Core ou Tool. Les journaux natifs restent disponibles dans les diagnostics sélectionnables/copiés. Les entrées de la tâche s'importent automatiquement ; exportez les résultats souhaités avant FinishTask. Les sessions de bureau conservent leurs données.

## Sorties et revue {#outputs-and-review}

Les segments superposés NVIDIA non transformés restent intacts. Une ligne temporelle unique choisit la voix précédemment active tant qu'elle est active, sinon la région active la plus ancienne. Cette politique est enregistrée sous le numéro `previous-active-then-earliest` ; il s'agit d'une décision de disposition du logiciel, pas d'une prédiction exclusive du locuteur. Les indices conservent les candidats d'overlap non transformés. Le discours non couvert reste non attribué et l'écran affiche son nombre.

Les mots/temps originaux et le texte des sous-titres existants sont conservés par attribution. La reconstruction explicite recrée les sous-titres de parole à partir des mots originaux ; les sous-titres sonores restent inchangés. Le passage à un modèle crée de nouvelles identités anonymes au lieu de hériter des noms de l'ancien moteur. Les attributions manuelles de locuteurs existantes nécessitent une remplacement explicite avant un tel changement. Les surécris manuels de la même engine conservent le comportement existant. Les noms sont des étiquettes d'affichage, pas des reconnaissances biométriques.

Opérations : nemotron_status, nemotron_diagnostics, install_nemotron_runtime, install_nemotron_model, register_nemotron_model ; les opérations communes diarize_subtitles, rename_speakers, edit_subtitles, read_subtitles et export restent disponibles.
