---
id: guide-app-docs-diarization
title: Diaryseur de communauté-1 facultatif
description: Diaryseur de communauté-1 facultatif
section: Guide
order: 40
parent: guide-lisez-moi
sourceRevision: 1a321103eec12eb4
---

## Diaryseur de communauté-1 facultatif {#optional-community-1-speaker-diarization}

NVIDIA Nemotron 3 est une alternative facultative à CPU/CUDA : voir [NvidiaDiarization.md](doc:guide-app-docs-nvidiadiarization). Cette page décrit la communauté-1.

La communauté-1 fournit des lignes de temps globales régulières et exclusives des locuteurs. Phonon reste le moteur de transcription. Modèle : `pyannote/speaker-diarization-community-1`, édition fixée `3533c8cf8e369892e6b79ff1bf80f7b0286a54ee`, CC-BY-4.0. Source : https://huggingface.co/pyannote/speaker-diarization-community-1.

## Installation et identifiants {#installation-and-credentials}

L'archive de base Windows ne contient pas de poids ou de runtime de diarisation. L'installation télécharge des piliers spécifiés, hachés, dans un nouveau `runtime/components/diarization` candidat, vérifie les imports dans un nouveau CPU processus, puis active atomiquement ce dernier. Les candidats échoués ou annulés ne remplacent pas un composant plus ancien fonctionnel. Les dépendances privées Phonon restent inchangées. Les emballages complets et les URL officielles sont dans `diarization-runtime-lock.json` ; les piliers installés conservent leurs propres mentions de licence.

Ouvrez la page du modèle, acceptez ses conditions avec votre propre compte, puis téléchargez via l'Installation. L'Outil ne prend jamais ces conditions automatiquement. Sa credentielle de lecture Windows protégée a la priorité sur un Hugging Face login existant. Le jeton n'est jamais un paramètre d'entreprise, un argument de commande, un champ de génération sauvegardé ou une entrée de métadonnées du modèle. La télémétrie de la Communauté-1 est désactivée pour cet Outil.

La localisation de l'enregistrement se réfère au répertoire du modèle en place, vérifie la classe de pipeline de la Communauté-1 fixe et les `$model` actifs contenus, et stocke les hachages de fichiers dans le registre de l'Outil. Les classes Python personnalisées et les références d'actifs externes sont rejetées. Les fichiers ne sont pas déplacés.

## Exécution et sorties {#execution-and-outputs}

Le worker optionnel CPU utilise un chemin de dépendances séparé avec Pyannote 4.0.7, torch 2.8.0+cpu et torchaudio 2.8.0+cpu. Il convertit les audio mono PCM16 propres à la tâche en un onglet de forme flottante d'un minute à la fois. Pyannote analyse lui-même la transcription avec des analyses glissantes et des tailles de lots bornées, en tenant compte de la globalisation de l'agglomération des locuteurs ; les fenêtres Phonon indépendantes ne redémarrent jamais le numérotage des locuteurs. Une politique de durée explicite refuse les audio plus longs que quatre heures au maximum. Le comportement en mémoire/temps natif sur de longues fichiers reste dépendant du travail et n'a pas été certifié à ce seuil.

Les mots originaux textes/timestamps restent immuables. La génération/reflow peut diviser le discours aux changements de locuteur en utilisant des copies temporaires d'attributs de mots. L'analyse d'un document existant conserve par défaut les textes/times de cotes manuelles. Les attributions de locuteurs manuelles persistent sauf si une remplacement est demandé. Un écart de durée, ou un changement de hachage de source après une analyse précédente, est rejeté. Cela ne prouve pas que un document JSON non analysé correspond à un fichier média de la même longueur arbitraire ; l'utilisateur doit sélectionner le enregistrement correspondant.

JSON schemaVersion 1 gagne des options `speakers`, `diarization`, `speakerLabels`, et par-cue `speaker`, `speakerManual`, `speakerCandidates`, `speakerOverlapFraction`. La fraction mesure l'overlap temporel avec une région de locuteur exclusive, pas une calibration de la confiance du modèle. Le discours non couvert reste non attribué. Un cote couvrant plusieurs voix conserve des candidats examinables ; une reconstruction explicite peut la diviser en utilisant les mots originaux. Les descriptions sonores ne sont jamais traitées comme du discours.

SRT/VTT peuvent afficher un préfixe plain `[Name]`. Les textes de cotes bruts restent séparés. Les noms visibles comptent pour les vérifications de vitesse de lecture et la réparation de timing bornée, qui ne fusionnent pas les cotes appartenant à différents locuteurs. Le renommage ne change pas les mots ou les timings. Les étiquettes de locuteurs sont des identités anonymes par enregistrement, pas de reconnaissance de personnage à travers les fichiers.

## Opérations publiques {#public-operations}

- `diarization_status`: prêts locaux sans importer l'engine neuronal.
- `check_diarization_access`: accès structuré Accessible/AccessRequired; autorisation réseau authentifiée.
- `install_diarization_runtime`, `install_diarization_model`: examen explicite du contrat de licence et de l'autorisation réseau; activation du candidat, verrou privé et diagnostics conservés.
- `register_diarization_model`: référence de répertoire local compatible avec les hachages.
- `diarize_subtitles`: média original plus document, limites, threads, durée, tailles de lots, étiquettes et drapeaux explicites de réconstruire/remplacement manuel.
- `rename_speakers`: carte de noms et préférence d'affichage des étiquettes; crée un nouveau bundle.
- `edit_subtitles`: interprète optionnel ID ou null sur chaque patch de piste.

Tous les champs de fichiers de médias/document participent à l'importation automatique des tâches privées. Les espaces de travail et les intermédiaires utilisent JobContext.path ; les travailleurs s'arrêtent avant la libération des réservations et la suppression des fichiers de tampon. Exportez les bundles souhaités avant FinishTask. L'application autonome utilise des sessions conservées. Toutes les paramètres d'affaires natifs sont exposés par le biais de la configuration de génération ou des opérations avancées.

## Réparation de la limite de sous-titrage {#caption-boundary-repair-0-5-1}

La ponctuation finale est regroupée avec le mot précédent avant le positionnement, en respectant le pause configurée. L'allignement mot/voix peut utiliser une région la plus proche uniquement dans un délai de 250 ms lorsque la superposition directe n'existe pas ; les longues lacunes non couvertes restent non attribuées. Une limite de mélange faible (sous 60% de couverture dominante du mot) peut conserver le voix précédent lorsque ce voix encore superpose au moins 25% du mot. Un remplacement proche sans superposition directe peut suivre un mot bien couvert suivant dans la même phrase non terminée. Les réponses courtes complètement couvertes conservent leur propre interlocuteur.

Ces règles affectent les copies temporaires de positionnement, jamais les mots originaux ou les lignes de temps régulières/exclusives du modèle. Elles empêchent le jitter de l'heure d'étiquette et la ponctuation séparément temporelle de fragmenter les sous-titres. Elles ne peuvent pas réparer une mauvaise décision de regroupement d'interlocuteurs neural ou récupérer des transcriptions manquées/erronées. L'analyse de document existant conserve toujours le texte et la timing des marques de temps manuelles à moins que la reconstruction ne soit demandée.
