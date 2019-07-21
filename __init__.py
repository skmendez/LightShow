import threading
import time
import pyaudio
from scipy.signal import fftconvolve
from demo import Demo
from gen_demo import gen_video
from now_playing import get_song_info, get_url
from stream import read_stream
from timer import RepeatedTimer
from videoprocess import play_at_time
from distutils.util import strtobool

CURRENT_SONGS = {}
SONG_LOCK = threading.Lock()
SONG_DB = {("Robotaki", 'Drunk feat. Reece (Official Video)'): "Drunk.npz",
           ("Mat Zo & Porter Robinson", "Easy (Official Video)"): "Mat Zo & Porter Robinson - Easy (Official Video).npz",
           ("Madeon", "All My Friends (Official Audio)"): "Madeon - All My Friends (Official Audio).npz"}

def update_songs():
    info = get_song_info()
    with SONG_LOCK:
        for opt in ("chrome", "spotify"):
            if opt in info:
                CURRENT_SONGS[opt] = info[opt]
            elif opt in CURRENT_SONGS:
                del CURRENT_SONGS[opt]
timer = RepeatedTimer(3, update_songs)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                input=True,
                frames_per_buffer=512,
                input_device_index=9,
                as_loopback=True)


print("Ready")
while True:
    with SONG_LOCK:
        current_song = CURRENT_SONGS.get("spotify")
        if current_song is None:
            current_song = CURRENT_SONGS.get("chrome")
    if current_song is None or current_song not in SONG_DB:
        if current_song is not None:
            download = strtobool(input("Would you like to download and process {} by {}?".format(current_song[1], current_song[0])))
            if download:
                if current_song[0] is not None:
                    search = " - ".join(current_song)
                else:
                    search = current_song[1]
                url = get_url(search)
                print(url)
                gen_video(url, SONG_DB, SONG_LOCK)
                print(SONG_DB)
        else:
            print("Sleeping...", current_song)
            time.sleep(5)
            continue
    demo = Demo.from_file(SONG_DB[current_song])
    print(len(demo.data), len(demo.wav))
    seconds = 4
    frames = 48000 * seconds
    data = read_stream(stream, frames)
    start = time.time()
    xcorr = fftconvolve(demo.wav, data[::-1])
    time_in_video = time.time() - start + xcorr.argmax() / 48000
    play_at_time(demo, time_in_video)
