"""One-shot optional diarization worker; stdout is one structured JSON result."""
import contextlib
import json
import os
import sys
import diarization
os.environ["PYANNOTE_METRICS_ENABLED"]="0"
os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"


def main(p):
    if p["task"]=="access":return diarization.access()
    if p["task"]=="install_model":return diarization.install_model(p["root"],p["destination"])
    if p["task"]=="install_runtime":return diarization.install_runtime(p["root"],p["destination"])
    if p["task"]=="infer":return diarization.infer(p["root"],p["audio"],p["options"],p["scratch"])
    raise ValueError("Unknown diarization task")


if __name__=="__main__":
    for stream in (sys.stdin,sys.stdout,sys.stderr):stream.reconfigure(encoding="utf-8",errors="replace")
    request=json.load(sys.stdin)
    try:
        with contextlib.redirect_stdout(sys.stderr):result=main(request["parameters"])
        json.dump({"ok":True,"result":result},sys.stdout,ensure_ascii=False,allow_nan=False)
    except Exception as exc:
        json.dump({"ok":False,"error":str(exc),"type":type(exc).__name__},sys.stdout,ensure_ascii=False)
