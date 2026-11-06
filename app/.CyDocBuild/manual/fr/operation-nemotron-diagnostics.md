---
id: operation-nemotron-diagnostics
title: nemotron_diagnostics
description: Évaluer le runtime natif sélectionné et signaler la compatibilité réelle du dispositif et du pilote.
section: Référence
order: 200
parent: operations
sourceRevision: 02ccb20e1981643a
---

Évaluer le runtime natif sélectionné et signaler la compatibilité réelle du dispositif et du pilote.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `backend` | `string` | Non | Voir les paramètres de l’opération. `default="cpu"`, `enum=["cpu", "cuda"]` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `version` | `string` | Oui | Voir les paramètres de l’opération.  |
| `cudaAvailable` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `devices` | `array` | Oui | Voir les paramètres de l’opération.  |
| `warnings` | `array` | Oui | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : aucune déclarée.
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation nemotron_diagnostics
```
