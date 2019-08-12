import tkinter as tk
from time import time, sleep
from datetime import timedelta
import threading

class Timer():
    def __init__(self):
        ##Set up instance variables
        self._timer_epoch = 0
        self._countdown_epoch = 0
        self._time_paused = 0
        self._time_added = 0
        self._time_elapsed = 0
        self._running = False


    def start_timer(self):
        ##Don't start a new thread if we're already running.
        if not self.is_running():
            self._running = True
            self._timer_epoch = time()
            thread = threading.Thread(target=self.run_timer)
            thread.start()

    def start_countdown(self, countdown_seconds):
        if not self.is_running():
            self._running = True
            self.reset()
            self._countdown_epoch = time() + countdown_seconds
            thread = threading.Thread(target=self.run_countdown)
            thread.start()

    def update_timer(self):
        self._time_elapsed = time() - self._timer_epoch + self._time_paused + self._time_added

    def update_countdown(self):
        #countdown_epoch is in the future, we are counting towards it.
        new_countdown = self._countdown_epoch - time() + self._time_paused + self._time_added

        ##Never go lower than 0 and stop once we reach/pass it.
        if new_countdown <= 0:
            self._time_elapsed = 0
            self._running = False
        else:
            self._time_elapsed = new_countdown


    def stop(self):
        self._time_paused = self._time_elapsed
        self._running = False

    def reset(self):
        self._time_elapsed = 0
        self._time_paused = 0
        self._time_added = 0

    def add_seconds(self, seconds_to_add):
        self._time_added += seconds_to_add

    def subtract_seconds(self, seconds_to_subtract):
        self._timer_added -= seconds_to_subtract

    def set_elapsed(self, time_in_seconds ):
        self.reset_timer()
        self._timer_epoch = time() - time_in_seconds
        self.update_timer()

    def is_running(self):
        return self._running

    def get_elapsed(self):
        date_time_str = str(timedelta(seconds=self._time_elapsed))
        return (self._time_elapsed, date_time_str)

    def run_timer(self, update_rate = 0.009):
        while self.is_running():
            self.update_timer()
            sleep(update_rate)

    def run_countdown(self, update_rate = 0.009):
        while self.is_running():
            self.update_countdown()
            sleep(update_rate)
