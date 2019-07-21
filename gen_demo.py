import ffmpeg
import numpy as np
from videoprocess import process_video
from youtube_dl import YoutubeDL
import os

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

ydl_opts = {
    'format': "18",
    'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
    'outtmpl': '%(title)s.%(ext)s',
    "logger": MyLogger()}

def gen_video(url, song_db = None, song_lock = None):
    with YoutubeDL(ydl_opts) as ydl:
        title = ydl.extract_info(url)["title"]
        fname = "{}.mp4".format(title)

    if not os.path.exists(fname):
        raise ValueError("File not generated")

    demo = process_video(fname, 25)

    out, _ = (
        ffmpeg
        .input(fname)
        .output('pipe:', ac=1, ar=48000, format='wav')
        .run(capture_stdout=True)
    )
    wav = (
        np
        .frombuffer(out, np.int16)
    )
    demo.wav = wav
    demo.to_file("{}.npz".format(title))
    os.remove(fname)

    if song_db is not None:
        with song_lock:
            if "-" in title:
                artist, song = title.split("-")
                song = song.strip()
                artist = artist.strip()
            else:
                song = title.strip()
                artist = None
            song_db[(artist, song)] = "{}.npz".format(title)
