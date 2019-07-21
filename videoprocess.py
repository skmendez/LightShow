import cv2
import time
from cue_sdk import CUESDK, CorsairLedColor
import os
import numpy as np

from demo import Demo


def cap_at_speed(cap, fps):
    step = 1000/fps
    current = 0
    while True:
        cap.set(cv2.CAP_PROP_POS_MSEC, int(current))
        ret, image = cap.read()
        if not ret:
            return
        yield image
        current += step


Corsair = CUESDK(os.path.join(os.getcwd(), r"CUESDK.x64_2013.dll"))
pos_tup = Corsair.GetLedPositions(2).pLedPosition
boxes = {key: [t, l, t + h, w + l] for key, t, l, h, w in pos_tup}
boxes = {k: [int(i) for i in v] for k, v in boxes.items()}


def gen_update_kmeans(frame):
    img = cv2.resize(np.asarray(frame), (520, 147))
    key_arr = {key: img[y1:y2, x1:x2] for key, (y1, x1, y2, x2) in boxes.items()}
    means = {}
    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    for key, arr in key_arr.items():
        rms, labels, palette = cv2.kmeans(np.float32(arr.reshape(-1, 3)), n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)
        dominant = palette[np.argmax(counts)]
        means[key] = dominant[::-1]
    return [CorsairLedColor(key, *mean) for key, mean in means.items()]

def gen_update(frame):
    img = cv2.resize(np.asarray(frame), (520, 147))
    key_arr = {key: img[y1:y2, x1:x2] for key, (y1, x1, y2, x2) in boxes.items()}
    means = {}
    for key, arr in key_arr.items():
        means[key] = np.mean(arr[..., ::-1], axis=(1, 0)).astype(int).tolist()
    return [CorsairLedColor(key, *mean) for key, mean in means.items()]


def process_video(name, fps=None):
    cap =cv2.VideoCapture(name)
    if fps is None:
        fps = cap.get(cv2.CAP_PROP_FPS)
    d = Demo(fps)
    for frame in cap_at_speed(cap, fps):
        d.data.append(gen_update(frame))
    return d


def play_at_time(demo, seconds=0):
    start = time.time()
    while True:
        delta = time.time()-start
        try:
            frame = demo.get_frame(seconds+delta)
        except IndexError:
            break
        Corsair.SetLedsColorsAsync(frame)
        time.sleep(1/demo.fps)


if __name__ == '__main__':
    out = process_video("Robotaki - Drunk.mp4")