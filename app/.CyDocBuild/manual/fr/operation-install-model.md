---
id: operation-install-model
title: install_model
description: Télécharge, vérifie et enregistre une référence à un modèle public CC-BY-4.0 explicite en utilisant Fermion fixé. Aucun identifiant de connexion dans les paramètres.
section: Référence
order: 200
parent: operations
sourceRevision: 293ea7fb9a55b2b4
---

Télécharge, vérifie et enregistre une référence à un modèle public CC-BY-4.0 explicite en utilisant Fermion fixé. Aucun identifiant de connexion dans les paramètres.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `model` | `string` | Non | Phonon-2 et 2.5-en : anglais uniquement. Phonon-2.5 : multilingue, y compris le français. `default="phonon-2"`, `enum=["phonon-2", "phonon-2.5", "phonon-2.5-en"]` |
| `license_accepted` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `path` | `string` | Oui | Voir les paramètres de l’opération.  |
| `sha256` | `object` | Oui | Voir les paramètres de l’opération.  |
| `format` | `value` | Oui | Voir les paramètres de l’opération.  |
| `verifiedBy` | `string` | Oui | Voir les paramètres de l’opération.  |
| `license` | `string` | Oui | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : `network`
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_model
```
