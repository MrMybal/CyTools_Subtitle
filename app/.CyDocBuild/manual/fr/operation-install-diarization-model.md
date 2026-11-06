---
id: operation-install-diarization-model
title: install_diarization_model
description: Téléchargez le modèle officiel enclos après la revue explicite des conditions/licence. Utilise des informations de connexion locales protégées; aucun paramètre token.
section: Référence
order: 200
parent: operations
sourceRevision: da5a095ec8b01629
---

Téléchargez le modèle officiel enclos après la revue explicite des conditions/licence. Utilise des informations de connexion locales protégées; aucun paramètre token.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
| `repair` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `model` | `string` | Oui | Voir les paramètres de l’opération.  |
| `revision` | `string` | Oui | Voir les paramètres de l’opération.  |
| `runtimeReady` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `modelReady` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `ready` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `runtimePath` | `string` | Oui | Voir les paramètres de l’opération.  |
| `modelPath` | `string` | Oui | Voir les paramètres de l’opération.  |
| `state` | `string` | Oui | Voir les paramètres de l’opération. `enum=["Installed", "Missing"]` |
| `credentialAvailable` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `source` | `string` | Oui | Voir les paramètres de l’opération.  |
| `license` | `string` | Oui | Voir les paramètres de l’opération.  |
| `device` | `string` | Oui | Voir les paramètres de l’opération. `enum=["cpu"]` |

## Comportement et accès {#behaviour}

- Autorisations requises : `network`
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_diarization_model
```
