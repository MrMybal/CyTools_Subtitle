---
id: operation-register-local-model
title: register_local_model
description: Vérifie et référence un répertoire de famille Phonon-2 local en place; aucuns poids ne sont copiés, pas de LoRA. Utilisé par localmodel dans transcribe.
section: Référence
order: 200
parent: operations
sourceRevision: 8e5fb184f875731f
---

Vérifie et référence un répertoire de famille Phonon-2 local en place; aucuns poids ne sont copiés, pas de LoRA. Utilisé par local_model dans transcribe.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `path` | `string` | Oui | Voir les paramètres de l’opération.  |
| `name` | `string` | Oui | Voir les paramètres de l’opération.  |
| `model` | `string` | Non | Voir les paramètres de l’opération. `default="phonon-2"`, `enum=["phonon-2", "phonon-2.5", "phonon-2.5-en"]` |
| `license` | `string` | Non | Voir les paramètres de l’opération. `default="Not declared"` |
| `source` | `string` | Non | Voir les paramètres de l’opération. `default=""` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | `string` | Oui | Voir les paramètres de l’opération.  |
| `path` | `string` | Oui | Voir les paramètres de l’opération.  |
| `sha256` | `object` | Oui | Voir les paramètres de l’opération.  |
| `format` | `value` | Oui | Voir les paramètres de l’opération.  |
| `name` | `string` | Oui | Voir les paramètres de l’opération.  |
| `model` | `string` | Oui | Voir les paramètres de l’opération.  |
| `license` | `string` | Oui | Voir les paramètres de l’opération.  |
| `source` | `string` | Oui | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation register_local_model
```
