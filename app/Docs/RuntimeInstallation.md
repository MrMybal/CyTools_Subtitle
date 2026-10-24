# Optional PyTorch runtime — 0.3.0

The Windows base ZIP includes CPython and the media/UI runtime. It excludes PyTorch, SymPy, NetworkX and mpmath. Preview, subtitle editing and timing repair work without those packages.

## Desktop

Open Installation. Review the PyTorch license, enable its checkbox and click **Download / repair PyTorch**. Watch the job status and Application log. Cancel requests stop the installer worker and descendants before resources are released. After a successful CPU import check the component becomes active; no application restart is needed for subsequent generation workers. Then install or register the desired Phonon model.

## MCP / CLI

- `runtime_status {}` returns Installed/Missing, readiness, exact expected/detected package versions, source/license links and verification information.
- `install_runtime {"license_accepted":true,"repair":false}` downloads pinned CPU packages when missing. The transport identity must have `network` permission. Use `repair:true` to build a new candidate even when the current component is installed.
- Poll the job through its terminal state. A cancellation request is not confirmation that the worker has stopped. A failed download leaves the old activation record intact; retry creates another candidate and can use the normal pip download cache.

The installer only targets private directories under runtime/components/pytorch. It never replaces Python, edits a system installation, moves existing models, changes drivers or swaps CUDA libraries. Package names, versions and the HTTPS package index are fixed by the Tool; no arbitrary package names or commands are accepted.

Candidate directories and cached downloads are persistent installation state, not temporary AI task outputs. FinishTask does not uninstall a completed component. Base release packaging excludes these directories, so building a ZIP after local installation still does not bundle PyTorch.

The guided installer currently supports Windows CPython 3.11 CPU. Other platforms remain unvalidated. Model weights retain their own licenses and installation flow. Source development environments may install the full requirements.txt directly.
