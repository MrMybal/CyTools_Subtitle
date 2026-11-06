---
id: operation-model-status
title: model_status
description: Signale les références de modèle Phonon installées, les dépendances et le support de transcription CPU vérifié.
section: Référence
order: 200
parent: operations
sourceRevision: ba6c12b6f492bd22
---

Signale les références de modèle Phonon installées, les dépendances et le support de transcription CPU vérifié.

## Paramètres {#contract}

Aucun champ nommé n’est déclaré à ce niveau. Consultez le schéma avec `describe-operation` pour connaître sa forme exacte.
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `device` | `value` | Oui | Voir les paramètres de l’opération.  |
| `models` | `array` | Oui | Voir les paramètres de l’opération.  |
| `fermionVersion` | `string` | Oui | Voir les paramètres de l’opération.  |
| `loraSupported` | `value` | Oui | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation model_status
```
