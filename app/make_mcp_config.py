"""Print MCP configuration for this installation; no file is written."""
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
python=ROOT/("runtime/python/Scripts/python.exe" if os.name=="nt" else "runtime/python/bin/python")
if __name__=="__main__":
    print(json.dumps({"mcpServers":{"CyTools_Subtitle":{"command":str(python),"args":[str(ROOT/"app/tool.py"),"--data-dir",str(ROOT/"data/mcp"),"mcp"]}}},indent=2))
