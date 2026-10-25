"""Regression coverage for padded video rows and asynchronous preview publication."""
import time
import av
import numpy as np
import pytest
from preview import Player, preview_rgb


@pytest.mark.parametrize("width,height",[(641,361),(854,480),(1676,992),(1921,1081)])
def test_padded_rgb_is_converted_to_bounded_packed_image(width,height):
    pixels=np.full((height,width,3),[12,80,220],dtype=np.uint8)
    frame=av.VideoFrame.from_ndarray(pixels,format="rgb24")
    raw=frame.to_ndarray(format="rgb24")
    assert not raw.flags.c_contiguous
    result=preview_rgb(frame)
    assert result.flags.c_contiguous and result.dtype==np.uint8
    assert result.shape[1]<=1280 and result.shape[2]==3
    assert result.shape[:2]==(height,width) if width<=1280 else result.shape[:2]==(round(height*1280/width),1280)
    np.testing.assert_array_equal(result[result.shape[0]//2,result.shape[1]//2],[12,80,220])


def wait_for(condition,timeout=8):
    deadline=time.monotonic()+timeout
    while not condition() and time.monotonic()<deadline:time.sleep(.01)
    assert condition()


def test_open_and_seek_publish_packed_first_and_subsequent_frames(tmp_path):
    path=tmp_path/"odd width é.mkv"
    with av.open(str(path),"w") as output:
        stream=output.add_stream("ffv1",rate=10)
        stream.width=641;stream.height=361;stream.pix_fmt="yuv444p"
        for index in range(8):
            frame=av.VideoFrame.from_ndarray(np.full((361,641,3),index*20,dtype=np.uint8),format="rgb24")
            for packet in stream.encode(frame):output.mux(packet)
        for packet in stream.encode():output.mux(packet)
    player=Player()
    try:
        player.open(path)
        wait_for(lambda:player.frame is not None or bool(player.error))
        assert not player.error
        first=player.frame
        assert first.shape==(361,641,3) and first.flags.c_contiguous
        assert (player.width,player.height)==(641,361)
        player.seek(.4,play=False)
        wait_for(lambda:player.frame is not first or bool(player.error))
        assert not player.error and player.frame.flags.c_contiguous
        assert player.current_time()==pytest.approx(.4)
    finally:player.stop()
    assert not player._threads


def test_invalid_video_is_reported_without_raising_on_the_ui_thread(tmp_path):
    path=tmp_path/"broken.mp4";path.write_bytes(b"not video")
    player=Player()
    try:
        player.open(path)
        wait_for(lambda:bool(player.error))
        assert player.frame is None
    finally:player.stop()
