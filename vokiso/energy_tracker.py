import numpy as np
from sonopy import mel_spec


class EnergyTracker:
    """Decides whether audio chunks should be sent"""

    def __init__(self, rate: int, threshold: float = 1.5):
        self.rate = rate
        self.threshold = threshold
        self.level = 0.
        self.frame = 0
        self.av_mel = 0.  # type: np.ndarray

    def update(self, audio: np.ndarray) -> bool:
        mel = mel_spec(audio, self.rate, (len(audio), len(audio)))[0]

        self.frame += 1
        weight = max(5.733 / self.rate, 1 / self.frame)
        self.av_mel -= weight * (self.av_mel - mel)

        cur_level = (mel - self.av_mel)[2:10].max()
        diff = cur_level - self.level
        self.level += (0.2 if diff > 0 else 0.05) * diff
        level = max(cur_level, self.level)

        print_level = max(0, int(30 * (level - self.threshold)))
        print('=' * print_level + '-' * (100 - print_level))

        return level > self.threshold
