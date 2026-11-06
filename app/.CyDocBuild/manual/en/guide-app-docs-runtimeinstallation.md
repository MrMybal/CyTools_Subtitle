---
id: guide-app-docs-runtimeinstallation
title: Optional PyTorch runtime — 0.3.0
description: Optional PyTorch runtime — 0.3.0
section: Guide
order: 40
parent: guide-lisez-moi
revision: 992775e280863e7f
---

## Optional PyTorch runtime {#optional-pytorch-runtime-0-3-0}

The Windows base ZIP includes CPython and the media/UI runtime. It excludes PyTorch, SymPy, NetworkX and mpmath. Preview, subtitle editing and timing repair work without those packages.

## Desktop {#desktop}

Open Installation. Review the PyTorch license, enable its checkbox and click **Download / repair PyTorch**. Watch the job status and Application log. Cancel requests stop the installer worker and descendants before resources are released. After a successful CPU import check the component becomes active; no application restart is needed for subsequent generation workers. Then install or register the desired Phonon model.
