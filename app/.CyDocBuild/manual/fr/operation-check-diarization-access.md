---
id: operation-check-diarization-access
title: check_diarization_access
description: Vérifiez les informations de connexion protégées existantes du Hugging Face contre la révision officielle enclosée. Aucun paramètre token.
section: Référence
order: 200
parent: operations
sourceRevision: 21372a706cd52924
---

Vérifiez les informations de connexion protégées existantes du Hugging Face contre la révision officielle enclosée. Aucun paramètre token.

## Paramètres {#contract}

Aucun champ nommé n’est déclaré à ce niveau. Consultez le schéma avec `describe-operation` pour connaître sa forme exacte.
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `state` | `string` | Oui | Voir les paramètres de l’opération. `enum=["Accessible", "AccessRequired"]` |
| `source` | `string` | Oui | Voir les paramètres de l’opération.  |
| `message` | `string` | Non | Voir les paramètres de l’opération.  |
| `reason` | `string` | Non | Voir les paramètres de l’opération. `enum=["Authentication", "TokenPermissions", "Conditions"]` |

## Comportement et accès {#behaviour}

- Autorisations requises : `network`
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation check_diarization_access
```
