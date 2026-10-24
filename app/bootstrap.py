"""Activation runs before importing desktop code; failures keep the last working app."""
import sys
from pathlib import Path
import updates
try: updates.apply()
except Exception as exc:
    path=Path(__file__).resolve().parents[1]/"data/logs/update-startup.log"
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(str(exc),"utf-8")
from desktop import main
main()
