import os
import audioread
import simpleaudio
import io
import scipy.io.wavfile
import numpy as np
import hashlib
import contextlib
import wave
from pygame import mixer

DEFAULT_CACHE_PATH = "/tmp/producerbuddy-wavecache"

class AudioController():
    def __init__(self):
        if not os.path.isdir(DEFAULT_CACHE_PATH):
                os.mkdir(DEFAULT_CACHE_PATH)
        ##TODO: Implement memory management for loaded audio.
        self.cache_dir = DEFAULT_CACHE_PATH
        self.loaded_audio_objects = {}

        mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512, devicename=None)
        mixer.init()

    def load_audio(self, filepath):
        ##Don't try to load if we already have.
        if not self.is_file_loaded(filepath):
            self.loaded_audio_objects[filepath] = AudioObject(filepath, self.cache_dir)

    def play_audio(self, filepath):
        if not self.is_file_loaded(filepath):
            self.load_audio(filepath)

        audio_object = self.loaded_audio_objects[filepath]
        if mixer.get_busy():
            self.stop_audio()
        mixer.music.load(audio_object._cache_path)
        mixer.music.play()

    def stop_audio(self):
        mixer.music.stop()


    def is_file_loaded(self, filepath):
        return filepath in self.loaded_audio_objects

class AudioObject():
    def __init__(self, filepath, cache_dir):
        self._filepath = filepath
        self._cache_hash = cache_hash(filepath)
        cache_basename = self._cache_hash
        self._cache_path = os.path.join(cache_dir, cache_basename)

        with audioread.audio_open(self._filepath) as decode:
            self._samplerate = decode.samplerate
            self._channels = decode.channels
            with contextlib.closing(wave.open(self._cache_path, 'w')) as of:
                of.setnchannels(decode.channels)
                of.setframerate(decode.samplerate)
                of.setsampwidth(2)

                for buf in decode:
                    of.writeframes(buf)
        print("Saved to {}".format(self._cache_path))


def cache_hash(file_path):
    hash_obj = hashlib.md5()
    hash_obj.update(file_path.encode('utf-8'))

    hash_digest_str = hash_obj.hexdigest()
    return hash_digest_str + ".wav"
