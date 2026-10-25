"""Bounded native audio/video preview; decoding stays off the ImGui thread."""
import threading
import time
from pathlib import Path


def preview_rgb(frame):
    """Publish a bounded packed RGB image, including for padded FFmpeg rows."""
    import numpy as np
    if frame.width>1280:
        frame=frame.reformat(width=1280,height=max(2,round(frame.height*1280/frame.width)),format="rgb24")
    # PyAV can return a view with row padding (e.g. 1676px capture). ImGui's
    # ndarray binding requires a C-contiguous image; never publish that view.
    return np.ascontiguousarray(frame.to_ndarray(format="rgb24"))


class Player:
    def __init__(self):
        self.path=""; self.duration=0.; self.position=0.; self.frame=None
        self.width=0; self.height=0; self.playing=False; self.error=""; self.audio_stream=0
        self._stop=threading.Event(); self._threads=[]; self._clock=None; self._origin=0.
        self._lock=threading.Lock(); self._stream=None

    def current_time(self):
        with self._lock:
            return min(self.duration,self._origin+max(0,time.monotonic()-self._clock)) if self._clock is not None else self.position

    def stop(self):
        position=self.current_time()
        self._stop.set()
        if self._stream is not None:
            try: self._stream.abort()
            except Exception: pass
        for thread in self._threads: thread.join(timeout=5)
        if any(t.is_alive() for t in self._threads):
            raise RuntimeError("Preview decoder has not stopped")
        self._threads=[]
        with self._lock: self.position=position; self._clock=None
        self.playing=False

    def open(self,path,audio_stream=0):
        self.stop(); self.path=str(Path(path).resolve()); self.audio_stream=audio_stream
        self.position=0.;self.frame=None;self.error="";self.duration=0.
        self._stop=threading.Event()
        thread=threading.Thread(target=self._probe,daemon=True);self._threads=[thread];thread.start()

    def _probe(self):
        try:
            import av
            with av.open(self.path,options={"protocol_whitelist":"file,pipe,crypto"}) as media:
                self.duration=float(media.duration/av.time_base) if media.duration is not None else max((float(s.duration*s.time_base) for s in media.streams if s.duration is not None),default=0)
                if media.streams.video:
                    stream=media.streams.video[0]; self.width=stream.codec_context.width;self.height=stream.codec_context.height
                    self.frame=preview_rgb(next(media.decode(stream)))
                else: self.width=self.height=0
        except Exception as exc: self.error=str(exc)

    def seek(self,position,play=None):
        resume=self.playing if play is None else play
        self.stop();self.position=max(0,min(position,self.duration));self._origin=self.position
        self._stop=threading.Event();self.error=""
        if resume:
            self.playing=True
            self._threads=[threading.Thread(target=self._audio,daemon=True),threading.Thread(target=self._video,daemon=True)]
        else: self._threads=[threading.Thread(target=lambda:self._video(single=True),daemon=True)]
        for thread in self._threads: thread.start()

    def toggle(self):
        if self.playing: self.stop()
        elif self.path: self.seek(0 if self.position>=self.duration else self.position,play=True)

    def _audio(self):
        try:
            import av
            import numpy as np
            import sounddevice as sd
            with av.open(self.path,options={"protocol_whitelist":"file,pipe,crypto"}) as media:
                if len(media.streams.audio)<=self.audio_stream:
                    with self._lock: self._clock=time.monotonic()
                    return
                stream=media.streams.audio[self.audio_stream]
                media.seek(int(self._origin*av.time_base),backward=True)
                resampler=av.AudioResampler(format="flt",layout="stereo",rate=48000)
                with sd.OutputStream(samplerate=48000,channels=2,dtype="float32",blocksize=1024) as output:
                    self._stream=output
                    first=True
                    for frame in media.decode(stream):
                        if self._stop.is_set():break
                        for audio in resampler.resample(frame):
                            pts=float(audio.pts*audio.time_base) if audio.pts is not None else self._origin
                            samples=audio.to_ndarray().reshape(-1,2)
                            skip=max(0,round((self._origin-pts)*48000))
                            samples=samples[skip:]
                            if not len(samples):continue
                            if first:
                                with self._lock:
                                    self._clock=time.monotonic()+float(output.latency)
                                first=False
                            # Bounded blocks make pause and close responsive.
                            for pos in range(0,len(samples),1024):
                                if self._stop.is_set():break
                                output.write(np.ascontiguousarray(samples[pos:pos+1024]))
                    if not self._stop.is_set():
                        self.position=self.duration
                        with self._lock: self._clock=None
                        self.playing=False
        except Exception as exc:
            if not self._stop.is_set(): self.error=str(exc);self.playing=False
        finally:self._stream=None

    def _video(self,single=False):
        try:
            import av
            with av.open(self.path,options={"protocol_whitelist":"file,pipe,crypto"}) as media:
                if not media.streams.video:return
                stream=media.streams.video[0]
                media.seek(int(self._origin*av.time_base),backward=True)
                for frame in media.decode(stream):
                    if self._stop.is_set():break
                    pts=float(frame.pts*frame.time_base) if frame.pts is not None else self._origin
                    if pts<self._origin-.04:continue
                    if not single:
                        if not self.playing: break
                        while not self._stop.is_set() and (self.playing and (self._clock is None or pts>self.current_time()+.02)):
                            self._stop.wait(.005)
                        if self._stop.is_set():break
                        if pts<self.current_time()-.15:continue
                    self.frame=preview_rgb(frame)
                    if single:break
        except Exception as exc:
            if not self._stop.is_set():self.error=str(exc)
