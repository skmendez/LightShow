from cue_sdk.structures import CorsairLedColor
import numpy as np
from typing import List


class Demo:
    def __init__(self, fps):
        self.fps = fps
        self.data: List[List[CorsairLedColor]] = []
        self.wav = None

    def to_array(self):
        rows = []
        for frame in self.data:
            row = np.array([[led.ledId, led.r, led.g, led.b] for led in frame], dtype=np.uint8)
            rows.append(row)
        return np.array(rows, dtype=np.uint8)

    def to_file(self, fname):
        if self.wav is not None:
            np.savez_compressed(fname, data=self.to_array(), fps=self.fps, wav=self.wav)
        else:
            np.savez_compressed(fname, data=self.to_array(), fps=self.fps)

    def to_dict(self):
        pass

    @classmethod
    def from_file(cls, fname):
        f = np.load(fname)
        arr = f["data"]
        fps = f["fps"].item()
        wav = f.get("wav")
        return cls.from_array(arr, fps, wav)

    @classmethod
    def from_array(cls, arr, fps, wav=None):
        obj = cls(fps)
        for frame in arr:
            obj.data.append([CorsairLedColor(*led) for led in frame])
        obj.wav = wav
        return obj

    def get_frame(self, seconds):
        index = seconds * self.fps
        return self.data[int(index)]
