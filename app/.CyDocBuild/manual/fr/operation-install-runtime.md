---
id: operation-install-runtime
title: install_runtime
description: Téléchargez la version corrigée CPU PyTorch et ses dépendances optionnelles dans un nouveau répertoire privé; vérifiez avant l'activation atomique. Aucun modèles, pilotes ou bibliothèques CUDA ne sont déplacés.
section: Référence
order: 200
parent: operations
sourceRevision: 9dd4260cd87b08aa
---

Téléchargez la version corrigée CPU PyTorch et ses dépendances optionnelles dans un nouveau répertoire privé; vérifiez avant l'activation atomique. Aucun modèles, pilotes ou bibliothèques CUDA ne sont déplacés.

## Paramètres {#contract}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `license_accepted` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
| `repair` | `boolean` | Non | Voir les paramètres de l’opération. `default=false` |
## Retours {#returns}

| Nom | Type | Obligatoire | Description |
|---|---|---|---|
| `component` | `value` | Oui | Voir les paramètres de l’opération.  |
| `state` | `value` | Oui | Voir les paramètres de l’opération. `enum=["Installed", "Missing"]` |
| `ready` | `boolean` | Oui | Voir les paramètres de l’opération.  |
| `expectedVersion` | `string` | Oui | Voir les paramètres de l’opération.  |
| `version` | `string` | Oui | Voir les paramètres de l’opération.  |
| `packages` | `array` | Oui | Voir les paramètres de l’opération.  |
| `path` | `string` | Oui | Voir les paramètres de l’opération.  |
| `source` | `string` | Oui | Voir les paramètres de l’opération.  |
| `license` | `string` | Oui | Voir les paramètres de l’opération.  |
| `licenseUrl` | `string` | Oui | Voir les paramètres de l’opération.  |
| `probeVerified` | `boolean` | Oui | Voir les paramètres de l’opération.  |

## Comportement et accès {#behaviour}

- Autorisations requises : `network`
- Moteurs : aucun déclaré.
- Annulation : prise en charge.

```powershell
runtime\python\Scripts\python.exe app\tool.py describe-operation install_runtime
```
