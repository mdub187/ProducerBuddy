import tkinter as tk
from timer import Timer

class TkTimer(object):
    """docstring for TkTimer."""

    def __init__(self, root=None, timer=None, buttons=False, pack_widget = False):
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        ##Set up instance variables
        if timer is None:
            self.timer = Timer()
        else:
            self.timer = timer
        ##Set up tkinter widgets:
        self.widget = tk.Frame(self.root)
        self._timer_stringvar = tk.StringVar()
        self._timer_stringvar.set("00:00:00.00")
        self._timer_label = tk.Label(self.widget, textvariable=self._timer_stringvar)
        self._timer_label.pack()

        if buttons:
            start_btn = tk.Button(self.widget, text="Start Timer", command=self.start_timer)
            start_btn.pack()
            stop_btn = tk.Button(self.widget, text="Stop", command=self.stop)
            stop_btn.pack()
            reset_btn = tk.Button(self.widget, text="Reset", command=self.reset)
            reset_btn.pack()

            countdown_entry = tk.Entry(self.widget, width=3)
            countdown_entry.pack()
            countdown_seconds = lambda: self.start_countdown(int(countdown_entry.get()))
            countdown_start_btn = tk.Button(self.widget, text="Start Countdown", command=countdown_seconds)
            countdown_start_btn.pack()

        ##Most of the time, we probably want to let whatever is calling this handle
        ##placing in tkinter.
        if pack_widget:
            self.widget.pack()
        self.reset()
        
    def start_timer(self):
        if not self.timer.is_running():
            self.timer.start_timer()
            self.run_loop()

    def start_countdown(self, countdown_seconds):
        if not self.timer.is_running():
            self.timer.start_countdown(countdown_seconds)
            self.run_loop()

    def stop(self):
        self.timer.stop()

    def reset(self):
        self.timer.reset()
        self.update_widget(True)

    def update_widget(self, force_update = False):
        if self.timer.is_running() or force_update:
            __, elapsed_str = self.timer.get_elapsed()
            self._timer_stringvar.set(elapsed_str)

    def set_elapsed(self, time_in_seconds):
        self.timer.set_elapsed(time_in_seconds)
        self.update_widget(force_update=True)

    def add_seconds(self, seconds_to_add):
        self.timer.add_seconds(seconds_to_add)
        self.update_widget(force_update=True)

    def subtract_seconds(self, seconds_to_subtract):
        self.timer.subtract_seconds(seconds_to_subtract)
        self.update_widget(force_update=True)

    def run_loop(self):
        if self.timer.is_running():
            self.update_widget()
            self.root.after(1, self.run_loop)
        self.update_widget(True)
