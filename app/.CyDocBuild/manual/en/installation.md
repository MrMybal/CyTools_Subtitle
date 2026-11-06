---
id: installation
title: Installation and models
description: Prepare the runtime, engines and optional models.
section: Guide
order: 5
parent: overview
revision: abea56074ac6006e
---

## Start the application {#start}

Open `CyTools_Subtitle.exe` on Windows. If the private runtime is missing, follow the installation steps in [Features and installation](doc:guide-readme). Launchers and engine requirements differ by application; do not assume that a copied source folder is a portable installation.

## Engines and models {#models}

Transcription and speaker diarization have distinct runtimes and weights. Check model_status and runtime_status for transcription; use the diarization status and access checks for the selected speaker backend. Accept gated model terms with the provider account before downloading.

Read the licence and source shown for each component before downloading. When access is restricted, open the official model page, obtain access with your account and authenticate locally. Do not paste credentials into generation settings.

## Storage {#storage}

Keep application data and model weights separate from the application files. Check the selected installation folder and available disk space before starting a large download. Changing a download-cache setting does not move existing models.
