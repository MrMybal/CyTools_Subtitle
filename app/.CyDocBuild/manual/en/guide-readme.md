---
id: guide-readme
title: Features and installation
description: Choose the right workflow and prepare the application.
section: Guide
order: 20
parent: overview
revision: 0c5364bcfc9d7233
---

Transcribe local audio or video into timed subtitles, inspect media, edit the document and adjust line breaks. Optional diarization backends add speaker labels; inspect their availability before use.

## Main workflow {#workflow}

1. Install the transcription runtime and a compatible model. Select the source media and transcription settings.
2. Run transcription, then inspect subtitle timing and text against the media preview.
3. Edit or reflow the subtitles and export the document. If speakers are needed, configure a diarization backend separately and review its labels.

## Requirements and installation {#requirements}

Transcription and speaker diarization have distinct runtimes and weights. Check model_status and runtime_status for transcription; use the diarization status and access checks for the selected speaker backend. Accept gated model terms with the provider account before downloading.

Read [Installation and models](doc:installation) for setup, the [User guide](doc:guide-lisez-moi) for detailed controls, and [Automation and API](doc:operations) for the public operation contracts.
