import re
import time
import pyaudio
from matplotlib import pyplot as plt
from scipy.signal import fftconvolve
from videoprocess import process_video, play_at_time
from demo import Demo
import ffmpeg
import numpy as np

CHUNKSIZE = 512 # fixed chunk size

def read_stream(stream, frames):
    return np.mean(np.frombuffer(stream.read(frames), dtype=np.int16).reshape(-1, 2), axis=1)

if __name__ == '__main__':
    demo = Demo.from_file("Drunk.npz")



    out, err = (
        ffmpeg
        .input('Robotaki - Drunk.mp4')
        .output('pipe:', ac=1, ar=48000, format='wav')
        .run(capture_stdout=True, capture_stderr=True)
    )
    wavrate = int(re.search(r"([0-9]+) Hz", err.decode('utf-8')).group(1))
    wav = (
        np
        .frombuffer(out, np.int16)
    )


    # initialize portaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=48000,
                    input=True,
                    frames_per_buffer=512,
                    input_device_index=6,
                    as_loopback=True)


    # do this as long as you want fresh samples
    seconds = 4
    frames = 48000*seconds
    data = read_stream(stream, frames)
    start = time.time()
    xcorr = fftconvolve(wav, data[::-1])
    time_in_video = time.time()-start+xcorr.argmax()/48000
    # play_at_time(demo, time_in_video)
    # # plot data
    # plt.plot(numpydata)
    # plt.show()

    # close stream
    stream.stop_stream()
    stream.close()
    p.terminate()
