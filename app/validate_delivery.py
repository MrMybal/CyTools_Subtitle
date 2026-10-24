"""Explicit real delivery checks; requires installed model and sound output."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

APP=Path(__file__).resolve().parent;ROOT=APP.parent
sys.path.insert(0,str(APP))


def build_sample():
    import imageio_ffmpeg
    source=ROOT/"data/validation-source/Voice sample.wav"
    target=source.with_suffix(".mp4")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-nostdin","-hide_banner","-loglevel","error","-f","lavfi","-i","testsrc2=size=640x360:rate=25","-i",str(source),"-map","0:v","-map","1:a","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-shortest","-y",str(target)],check=True)
    return target


def preview_check(video):
    from preview import Player
    player=Player()
    try:
        player.open(video)
        deadline=time.monotonic()+10
        while player.frame is None and not player.error and time.monotonic()<deadline:time.sleep(.02)
        assert player.frame is not None and not player.error,player.error
        assert (player.width,player.height)==(640,360)
        player.toggle()
        deadline=time.monotonic()+10
        while player._clock is None and not player.error and time.monotonic()<deadline:time.sleep(.02)
        assert not player.error and player._clock is not None,player.error
        time.sleep(1.)
        before=player.current_time();player.stop();assert .2<before<2, before
        player.seek(5.,play=True)
        deadline=time.monotonic()+10
        while player._clock is None and not player.error and time.monotonic()<deadline:time.sleep(.02)
        assert not player.error and player._clock is not None,player.error
        time.sleep(.9)
        after=player.current_time();player.stop();assert 5.1<after<7,after
        assert not player.error,player.error
        return {"audioOutputOpened":True,"videoPixels":[player.width,player.height],"playSeconds":before,"seekSeconds":after}
    finally:player.stop()


async def mcp_check(video):
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    data=ROOT/"data/mcp-validation"/uuid.uuid4().hex
    params=StdioServerParameters(command=sys.executable,args=[str(APP/"tool.py"),"--data-dir",str(data),"mcp"],env={**os.environ,"PYTHONIOENCODING":"utf-8","PYTHONUTF8":"1"})
    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize()
            listing=await session.list_tools();names={t.name for t in listing.tools}
            assert {"op_transcribe","op_edit_subtitles","op_inspect_media","op_read_subtitles","op_reflow_subtitles"}<=names
            async def call(name,p):
                response=await session.call_tool(name,p)
                assert not response.isError,(name,response)
                return json.loads(response.content[0].text)
            async def job(name,p):
                submitted=await call(name,{"parameters":p})
                deadline=time.monotonic()+180
                while time.monotonic()<deadline:
                    result=await call("cy_get_job",{"jobId":submitted["jobId"]})
                    if result["state"] in ("Completed","Cancelled","Failed"):break
                    await asyncio.sleep(.1)
                assert result["state"]=="Completed",result
                return result
            inspect=await job("op_inspect_media",{"media":str(video),"start":2,"duration":3,"excerpt":True})
            assert any(s.get("width")==640 for s in inspect["outputs"]["streams"])
            generated=await job("op_transcribe",{"media":str(video),"threads":2,"filter":"denoise","hotwords":["captions"],"max_chars":38})
            output=generated["outputs"]
            doc=json.loads(Path(output["document"]).read_text("utf-8"))
            assert doc["words"] and len(doc["cues"])>=3
            assert doc.get("timingPolicy",{}).get("max_cps")==22
            assert "timingRepair" in doc
            original_first=dict(doc["cues"][0])
            edited=await job("op_edit_subtitles",{"document":output["document"],"edits":[{"id":original_first["id"],"start":original_first["start"]+.04,"end":original_first["end"]+.04},{"id":"sound-demo","start":4.5,"end":5.5,"text":"[sound description supplied by the reviewer]","kind":"sound"}]})
            read=await job("op_read_subtitles",{"document":edited["outputs"]["document"],"start":0,"end":6,"limit":20})
            assert any(c["kind"]=="sound" for c in read["outputs"]["cues"])
            await job("op_reflow_subtitles",{"document":edited["outputs"]["document"],"max_chars":30,"max_duration":3.})
            exported=await call("cy_export_job",{"jobId":edited["jobId"],"destination":str(ROOT/"data/reports/mcp-export")})
            exported_doc=Path(exported["outputs"]["document"])
            assert exported_doc.exists()
            temporary_doc=Path(edited["outputs"]["document"])
            await call("cy_finish_task",{})
            assert not temporary_doc.exists() and exported_doc.exists()
            return {"toolCount":len(names),"realVideoTranscription":True,"cues":len(doc["cues"]),"words":len(doc["words"]),"correctedExport":str(exported_doc),"taskPurged":True}


def real_cancel(video):
    from tool import create_runtime
    with create_runtime(ROOT/"data/cancel-validation") as r:
        a=r.authenticate(r.create_client("Cancel validation")["token"]);s=r.create_session(a)["sessionId"]
        j=r.submit(a,s,"transcribe",{"media":str(video),"chunk_seconds":5,"threads":2})
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            current=r.get_job(a,j["jobId"])
            if "Transcribing window" in (current.get("progress") or {}).get("currentStep","") and r._workers:break
            if current["state"]=="Failed":raise AssertionError(current)
            time.sleep(.03)
        time.sleep(.15)
        workers=list(r._workers.values());assert workers
        r.cancel(a,j["jobId"]);result=r.wait(a,j["jobId"],timeout=15)
        assert result["state"]=="Cancelled" and not r._running
        assert all(not w.health()["alive"] for w in workers)
        r.finish_task(a,s)
        return {"state":result["state"],"workersStopped":True,"runningReservationsReleasedAfterStop":True}


if __name__=="__main__":
    video=build_sample()
    report={"video":str(video),"preview":preview_check(video),"mcp":asyncio.run(mcp_check(video)),"cancellation":real_cancel(video)}
    (ROOT/"data/reports/delivery-integration.json").write_text(json.dumps(report,indent=2),"utf-8")
    print(json.dumps(report,indent=2))
