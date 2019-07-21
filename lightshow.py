import os
import numpy as np
import mss
import cv2
from cue_sdk import *
import colorsys
from time import time

Corsair = CUESDK(os.path.join(os.getcwd(), r"CUESDK.x64_2013.dll"))
pos_tup = Corsair.GetLedPositions(2).pLedPosition
boxes = {key: [t, l, t + h, w + l] for key, t, l, h, w in pos_tup}
boxes = {k: [int(i) for i in v] for k, v in boxes.items()}
arr = np.zeros((147, 520, 4), dtype=np.uint8)
for box in boxes.values():
    arr = cv2.rectangle(arr, (box[1], box[0]), (box[3], box[2]), (255, 255, 255, 255))


def main(show=False):
    with mss.mss() as sct:
        mon = sct.monitors[1]
        frame = 0
        start = time()
        while True:
            frame += 1
            if frame == 9:
                print(1 / (time() - start) * 10)
                start = time()
                frame = 0

            sc = sct.grab(mon)
            img = cv2.resize(np.asarray(sc), (520, 147))
            if show:
                cv2.imshow('test', cv2.bitwise_xor(img, arr))
            key_arr = {key: img[y1:y2, x1:x2] for key, (y1, x1, y2, x2) in boxes.items()}
            means = {key: np.mean(arr[..., -2::-1], axis=(1, 0)).astype(int).tolist() for key, arr in key_arr.items()}
            led_colors = [CorsairLedColor(key, *mean) for key, mean in means.items()]
            Corsair.SetLedsColors(led_colors)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


def rgb_to_data(rgb):
    data = {}
    h, s, v = colorsys.rgb_to_hsv(*(k / 255 for k in rgb))
    data['hue'] = int(h * 65535)
    data['sat'] = int(s * 255)
    data['bri'] = int(v * 255)
    return data


if __name__ == "__main__":
    main(True)