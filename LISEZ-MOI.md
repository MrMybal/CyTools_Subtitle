# CyTools_Subtitle

Archive Windows portable : extrayez tout le ZIP dans un dossier accessible en écriture, puis lancez **CyTools_Subtitle.exe**. Python et les bibliothèques du lecteur et de l’interface sont inclus. Dans Installation, consultez la licence de PyTorch et cliquez **Download / repair PyTorch**, puis téléchargez les modèles dans l’onglet Installation après consultation de leur licence. Pour une installation depuis les sources, exécutez d’abord app/install.ps1.

1. Ouvrez votre audio ou vidéo dans **Media & generation**.
2. Choisissez **phonon-2** pour l’anglais ou **phonon-2.5** pour le français et le multilingue.
3. Cliquez **Generate subtitles**. Les fenêtres audio sont traitées une par une.
4. Contrôlez avec lecture/pause et la timeline. **Subtitle editor** permet de modifier textes, débuts/fins et descriptions sonores.
5. Choisissez un dossier d’export puis **Export SRT / VTT / JSON**.

**Options** : français/anglais, thème, taille du texte, licences, configurations JSON et autosave facultative. Charger une configuration ne lance aucun traitement.

**Installation** : télécharger, reprendre, réparer et référencer des modèles locaux compatibles. Le filtre vocal réduit le bruit ; il ne sépare pas les voix de la musique. Les descriptions de sons sont ajoutées par l’utilisateur ou l’IA après écoute.

**IA/MCP** : consultez [app/README.md](app/README.md) et app/mcp-config.example.json. Les chemins absolus sont acceptés sans copie manuelle. Exportez les résultats souhaités avant la fin d’une tâche IA temporaire.

Windows x64 et calcul CPU testés. Linux/macOS non validés. Le paquet Windows portable 0.2.2 inclut son propre Python 3.11.9. L’installation depuis les sources requiert Python 3.11 et app/install.ps1 ou app/install.sh.

Le dépôt GitHub se configure dans **Updates** ; aucun dépôt public présumé. Les mises à jour app/ s’activent au redémarrage avec restauration, en préservant data/ et runtime/.

Preuves : data/reports/. Sources, licences et guides : app/.


Version 0.2.0 : la correction des durées et chevauchements est automatique pour les nouvelles générations. Dans Subtitle editor, le bouton **Repair reading time and overlaps** corrige aussi un ancien résultat sans relancer Phonon. Les limites se règlent dans Segmentation & layout ; les cas trop rapides restent signalés pour préserver la synchronisation et le texte complet.

Version 0.2.1 : l’application est sous GNU Affero General Public License version 3 uniquement (AGPL-3.0-only), copyright (c) 2026 Cyberalien. Voir LICENSE. Le SDK CyToolsCore reste MIT ; les bibliothèques et modèles conservent leurs licences respectives.

Version 0.2.2 : paquet Windows portable avec runtime privé inclus. Les modèles se téléchargent séparément. Les releases privées se téléchargent dans le navigateur avec un compte autorisé ; l’updater intégré nécessite actuellement une release publique.

Version 0.3.0 : PyTorch, SymPy, NetworkX et mpmath ne sont plus inclus dans le ZIP de base. Installation propose leur téléchargement privé, leur vérification et leur réparation. Le lecteur et l’éditeur fonctionnent sans PyTorch. Pour migrer depuis 0.2.x, extrayez le nouveau paquet dans un dossier séparé et référencez les modèles existants sans les déplacer.

Version 0.4.0 : interface CyUI avec navigation latérale, lecteur synchronisé, recherche dans les répliques et édition des timings. Cinq thèmes, deux densités et taille du texte dans Options. Anglais par défaut, français sélectionnable. PyTorch et modèles restent téléchargés séparément.

Version 0.4.1 : correction du crash de prévisualisation avec certaines largeurs de capture. Déposez un fichier audio/vidéo ou un document JSON de sous-titres depuis l’Explorateur dans la fenêtre pour l’ouvrir.

Version 0.5.0 : identification facultative des locuteurs avec Community-1, noms modifiables, attribution par réplique et exports avec noms. Installez séparément le moteur CPU et les poids dans Installation après acceptation des conditions Hugging Face. Aucun jeton dans les configurations ou paramètres MCP.

0.5.1 : correction des sous-titres réduits à de la ponctuation et des coupures parasites en bord de mot. Les mots et les détections brutes du modèle sont conservés ; les erreurs de transcription et de locuteur doivent toujours être relues.
