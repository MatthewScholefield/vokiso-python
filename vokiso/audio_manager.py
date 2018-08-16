import atexit

import json
import numpy as np
from base64 import b64encode, b64decode
from openal.audio import SoundSink, SoundSource, SoundData
from pyaudio import PyAudio, paContinue, paInt16
from pyaudio import Stream
from queue import Queue
from random import random
from threading import Thread

from vokiso.connection_manager import DirectConnection
from vokiso.energy_tracker import EnergyTracker


class AudioManager:
    format = paInt16
    chunk_size = 1024
    rate = 44100

    audio_scale = 10.

    def __init__(self, conn: DirectConnection):
        self.p = PyAudio()
        atexit.register(self.p.terminate)
        self.stream = None  # type: Stream

        self.sink = SoundSink()
        self.sink.activate()

        self.source = SoundSource()

        def close():
            del self.sink

        atexit.register(close)

        self.source.gain = 1.0
        self.pos = self._pos = (random(), random())
        self.sink.play(self.source)

        self.conn = conn
        self.mic_data = Queue()
        self.speaker_data = Queue()
        self.energy_tracker = EnergyTracker(self.rate)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self.source.position = (self.audio_scale * pos[0], 0, self.audio_scale * pos[1])
        self._pos = pos

    def create_stream(self):
        if self.stream:
            raise RuntimeError('Already created stream!')
        stream = self.p.open(
            format=self.format, channels=1, rate=self.rate, input=True,
            output=False, stream_callback=self.callback, frames_per_buffer=self.chunk_size
        )
        atexit.register(stream.close)
        atexit.register(stream.stop_stream)
        stream.start_stream()
        self.stream = stream
        Thread(target=self._stream_thread, daemon=True).start()

    def _stream_thread(self):
        while True:
            new_chunk = self.mic_data.get()
            audio = np.fromstring(new_chunk, dtype=np.int16)
            audio = audio.astype(np.float32) / float(np.iinfo(audio.dtype).max)
            if not self.energy_tracker.update(audio):
                continue

            self.conn.send(json.dumps({
                'type': 'audio',
                'audio': b64encode(new_chunk).decode('ascii')
            }))

    def update(self):
        self.sink.update()

    def process_audio_message(self, message):
        new_chunk = b64decode(message['audio'])
        print('Add', len(new_chunk))
        self.source.queue(SoundData(new_chunk, 1, 16, len(new_chunk), self.rate))

    def callback(self, in_data, frame_count, time_info, status):
        self.mic_data.put(in_data)
        return None, paContinue
