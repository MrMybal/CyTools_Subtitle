# CyTools_Subtitle

Lancez **CyTools_Subtitle.exe**. Pour une nouvelle installation, exécutez app/install.ps1 puis téléchargez les modèles dans l’onglet Installation.

1. Ouvrez votre audio ou vidéo dans **Media & generation**.
2. Choisissez **phonon-2** pour l’anglais ou **phonon-2.5** pour le français et le multilingue.
3. Cliquez **Generate subtitles**. Les fenêtres audio sont traitées une par une.
4. Contrôlez avec lecture/pause et la timeline. **Subtitle editor** permet de modifier textes, débuts/fins et descriptions sonores.
5. Choisissez un dossier d’export puis **Export SRT / VTT / JSON**.

**Options** : français/anglais, thème, taille du texte, licences, configurations JSON et autosave facultative. Charger une configuration ne lance aucun traitement.

**Installation** : télécharger, reprendre, réparer et référencer des modèles locaux compatibles. Le filtre vocal réduit le bruit ; il ne sépare pas les voix de la musique. Les descriptions de sons sont ajoutées par l’utilisateur ou l’IA après écoute.

**IA/MCP** : consultez [app/README.md](app/README.md) et app/mcp-config.example.json. Les chemins absolus sont acceptés sans copie manuelle. Exportez les résultats souhaités avant la fin d’une tâche IA temporaire.

Windows x64 et calcul CPU testés. Linux/macOS non validés. Le runtime privé dépend d’un Python 3.11 installé ; ce n’est pas un interpréteur portable. Sur une autre machine : app/install.ps1 ou app/install.sh.

Le dépôt GitHub se configure dans **Updates** ; aucun dépôt public présumé. Les mises à jour app/ s’activent au redémarrage avec restauration, en préservant data/ et runtime/.

Preuves : data/reports/. Sources, licences et guides : app/.


Version 0.2.0 : la correction des durées et chevauchements est automatique pour les nouvelles générations. Dans Subtitle editor, le bouton **Repair reading time and overlaps** corrige aussi un ancien résultat sans relancer Phonon. Les limites se règlent dans Segmentation & layout ; les cas trop rapides restent signalés pour préserver la synchronisation et le texte complet.

Version 0.2.1 : l’application est sous GNU Affero General Public License version 3 uniquement (AGPL-3.0-only), copyright (c) 2026 Cyberalien. Voir LICENSE. Le SDK CyToolsCore reste MIT ; les bibliothèques et modèles conservent leurs licences respectives.
