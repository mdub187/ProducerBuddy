from pygame import mixer
import os
import audioread
import simpleaudio
import io
import scipy.io.wavfile

import numpy as np
from pymediainfo import MediaInfo as minf

class ProducerBuddyAudioController():
    def __init__(self):
        mixer.init()
        ##TODO: Implement memory management for loaded audio.
        self.loaded_audio_objects = {}

    def load_audio(self, filepath):
        ##Don't try to load if we already have.
        if not self.is_file_loaded(filepath):
            self.loaded_audio_objects[filepath] = AudioObject(filepath)

    def play_audio(self, filepath):
        if not self.is_file_loaded(filepath):
            self.load_audio(filepath)
        audio_obj = self.loaded_audio_objects[filepath]
        audio_data = audio_obj._memory_buffer
        num_channels = audio_obj._channels
        samplerate = audio_obj._samplerate
        simpleaudio.play_buffer(audio_data, num_channels, 2, samplerate)

    def is_file_loaded(self, filepath):
        return filepath in self.loaded_audio_objects

class AudioObject():
    def __init__(self, filepath):
        self._filepath = filepath

        ##self._minfjson = json.loads(minf.parse(filepath))

        self._channels = 0
        self._duration = 0
        self._memory_buffer = None
        self.loadaudiobuffer()

    def loadaudiobuffer(self):
        ##audioread will do decoding magic sauce for us.
        with audioread.audio_open(self._filepath) as decode:
            self._samplerate = decode.samplerate
            self._channels = decode.channels
            buff = io.BytesIO()
            audio_arr = [x for x in decode]
            data_str = b''.join(audio_arr)
            numpy_arr = np.frombuffer(data_str, np.dtype('int16'))
            scipy.io.wavfile.write(buff, self._samplerate, numpy_arr)
            self._memory_buffer = buff.getbuffer()
