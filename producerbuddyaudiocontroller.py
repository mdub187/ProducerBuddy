import os
import hashlib
import ffmpeg
from pygame import mixer
import time
from timer import Timer
from datetime import timedelta

DEFAULT_CACHE_PATH = "/tmp/producerbuddy-wavecache"

class AudioController():
    def __init__(self):
        if not os.path.isdir(DEFAULT_CACHE_PATH):
                os.mkdir(DEFAULT_CACHE_PATH)
        ##TODO: Implement memory management for loaded audio.
        self.cache_dir = DEFAULT_CACHE_PATH
        self.loaded_audio_objects = {}
        self._playback_offset = 0
        self._currently_playing = None

        mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512, devicename=None)
        mixer.init()

    def load_audio(self, filepath):
        ##Don't try to load if we already have.
        if not self.is_file_loaded(filepath):
            self.loaded_audio_objects[filepath] = AudioObject(filepath, self.cache_dir)

    def play_audio(self, filepath, playback_offset = 0):
        if not self.is_file_loaded(filepath):
            self.load_audio(filepath)

        audio_object = self.loaded_audio_objects[filepath]
        self._playback_offset = playback_offset
        if self.is_playing():
            self.stop_audio()

        mixer.music.load(audio_object._cache_path)

        if self._playback_offset != 0:
            mixer.music.set_pos(self._playback_offset)

        mixer.music.play()
        self._currently_playing = audio_object

    def stop_audio(self):
        mixer.music.stop()
        self._currently_playing = None
        self._playback_offset = 0

    def is_playing(self):
        return mixer.music.get_busy()

    ##Return a tuple with elapsed seconds and total duration of currently playing
    ##track.
    def get_playhead(self):
        if not self._currently_playing is None and self.is_playing():
            ##Built in rate limit, if we call mixer.music.get_pos() too quickly
            ## it appears to return duplicate values. Slowing it down to once
            ##every half millisecond seems to alleviate that.
            time.sleep(0.005)
            duration = self._currently_playing._duration
            elapsed = mixer.music.get_pos() + self._playback_offset
            percentage = elapsed / duration * 0.1
            return (elapsed, duration, percentage )
        else:
            return (0,0,0)

    def is_file_loaded(self, filepath):
        return filepath in self.loaded_audio_objects

class AudioObject():
    def __init__(self, filepath, cache_dir):
        self._filepath = filepath
        self._cache_hash = cache_hash(filepath)
        cache_basename = self._cache_hash
        self._cache_path = os.path.join(cache_dir, cache_basename)

        ##FIXME: duration broke...
        self._duration = 1

        ffmpeg.input(self._filepath).output(self._cache_path).run()
        print("Saved to {}".format(self._cache_path))

class AudioTimer(Timer):
    def __init__(self, audiocontroller):
        super().__init__()
        self.audiocontroller = audiocontroller

    def get_elapsed(self):

        elapsed_ms, __, ___ = self.audiocontroller.get_playhead()
        if self.is_running():
            elapsed_sec = elapsed_ms / 1000
            self._time_elapsed = elapsed_sec
        date_time_str = str(timedelta(seconds=self._time_elapsed))
        return (self._time_elapsed, date_time_str)

    def is_running(self):
        return self.audiocontroller.is_playing()

def cache_hash(file_path):
    hash_obj = hashlib.md5()
    hash_obj.update(file_path.encode('utf-8'))

    hash_digest_str = hash_obj.hexdigest()
    return hash_digest_str + ".ogg"
