---
id: guide-app-docs-runtimeinstallation
title: Optionnel PyTorch runtime — 0.3.0
description: Optionnel PyTorch runtime — 0.3.0
section: Guide
order: 40
parent: guide-lisez-moi
sourceRevision: 992775e280863e7f
---

## Optionnel PyTorch runtime {#optional-pytorch-runtime-0-3-0}

La base Windows ZIP inclut CPython et le runtime media/UI. Elle exclut PyTorch, SymPy, NetworkX et mpmath. La prévisualisation, l'édition des sous-titres et la réparation du timing fonctionnent sans ces paquets.

## Bureau {#desktop}

Ouvrir l'installation. Examiner la licence PyTorch, cocher sa case et cliquer sur Télécharger / réparer PyTorch. Observer l'état du travail et le Journal d'application. Les demandes de cancellation arrêtent le travailleur d'installation et ses descendants avant la libération des ressources. Après un importation réussie de CPU, le composant devient actif ; aucun redémarrage de l'application n'est nécessaire pour les travailleurs de génération ultérieurs. Ensuite, installez ou enregistrez le modèle Phonon souhaité.
