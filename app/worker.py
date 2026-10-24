"""Isolated media/Phonon worker. stdout is exactly one JSON value."""
import contextlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import wave
import runtime_components
runtime_components.activate(Path(__file__).resolve().parents[1])


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def command(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", creationflags=0x08000000 if os.name=="nt" else 0)
    if result.returncode:
        raise RuntimeError(result.stderr[-6000:])
    return result.stdout


def main(p):
    task=p["task"]
    if task=="install_runtime":
        return runtime_components.install(p["root"],p["destination"])
    if task=="repair":
        from timing import repair
        return repair(p["document"],**p["options"])
    if task=="probe":
        import av
        with av.open(p["source"], options={"protocol_whitelist":"file,pipe,crypto"}) as media:
            streams=[{"index":s.index,"type":s.type,"codec":s.codec_context.name,
                      **({"width":s.codec_context.width,"height":s.codec_context.height} if s.type=="video" else {}),
                      **({"sampleRate":s.codec_context.sample_rate,"channels":s.codec_context.channels} if s.type=="audio" else {})} for s in media.streams if s.type in ("video","audio")]
            duration=float(media.duration/av.time_base) if media.duration is not None else max((float(s.duration*s.time_base) for s in media.streams if s.duration is not None), default=0)
            return {"durationSeconds":duration,"streams":streams}
    if task=="extract":
        filters={"none":"anull", "voice":"highpass=f=80,lowpass=f=8000,afftdn=nf=-25", "denoise":"afftdn=nf=-25"}
        args=[ffmpeg(),"-nostdin","-hide_banner","-loglevel","error","-protocol_whitelist","file,pipe,crypto","-i",p["source"],"-map",f'0:a:{p.get("audio_stream",0)}',"-vn"]
        if p.get("start",0): args += ["-ss",str(p["start"])]
        if p.get("duration"): args += ["-t",str(p["duration"])]
        args += ["-af",filters[p.get("filter","none")],"-ac","1","-ar","16000","-c:a","pcm_s16le","-y",p["destination"]]
        command(args)
        return {"audio":p["destination"]}
    if task=="infer":
        # CLI isolates native CPU kernels; a local directory prevents implicit downloads.
        args=[sys.executable,str(Path(__file__).with_name("phonon_cli.py")),"transcribe",p["model_path"],p["audio"],"--json","--threads",str(p["threads"])]
        if p.get("hotwords"):
            args += ["--hotwords",", ".join(p["hotwords"]),"--hotword-lambda",str(p["hotword_lambda"])]
        result=json.loads(command(args))
        if result.get("truncated"): raise RuntimeError("Phonon token budget exhausted: reduce chunk_seconds and retry")
        if result.get("text", "").strip() and not result.get("words"):
            raise RuntimeError("Phonon did not provide word timestamps; refusing estimated timing")
        return result
    if task=="install":
        result=command([sys.executable,str(Path(__file__).with_name("phonon_cli.py")),"transcribe",p["model"],"--download-only"])
        path=Path(result.strip().splitlines()[-1]).resolve()
        if not path.is_dir(): raise RuntimeError("Phonon did not return a verified model directory")
        return {"path":str(path),"model":p["model"]}
    raise ValueError("Unknown worker task")


if __name__=="__main__":
    for stream in (sys.stdin,sys.stdout,sys.stderr): stream.reconfigure(encoding="utf-8",errors="replace")
    os.environ["PYTHONIOENCODING"]="utf-8"
    os.environ["PYTHONUTF8"]="1"
    request=json.load(sys.stdin)
    try:
        with contextlib.redirect_stdout(sys.stderr): result=main(request["parameters"])
        json.dump({"ok":True,"result":result},sys.stdout,ensure_ascii=False,allow_nan=False)
    except Exception as exc:
        json.dump({"ok":False,"error":str(exc),"type":type(exc).__name__},sys.stdout,ensure_ascii=False)
