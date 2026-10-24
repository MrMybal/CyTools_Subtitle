"""Launch Phonon using the active private optional runtime."""
from pathlib import Path
import runtime_components
runtime_components.activate(Path(__file__).resolve().parents[1])
from fermion.cli import main
if __name__ == "__main__":
    main()
