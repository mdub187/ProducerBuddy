# ProducerBuddy
Python program to help organize audio samples.
Developed and tested on macos 10.14, but code should be portable with minimal
hassle.

Basic functionality is provided right now, with a GUI interface that allows
the user to select an "Unsorted" directory with unsorted samples, and then a
"Target" directory showing a folder structure that the samples can be moved to.

The Unsorted selection pane only shows audio files in the selected Unsorted
directory, it is not recursive. This programs assumes all your unsorted samples
will be chucked in a single folder, but clicking the file path at the top of the
pane allows another directory to be selected.

The Target selection pane shows ONLY the directories within the Target directory,
and IS recursive. A different top level Target folder can be selected by clicking
the directory path at the top of the pane also.

Right now, all of the program to speak of is contained within
producerbuddygui.py so run that with python3 and the packages below installed.
producerbuddy.py will eventually be a daemonized script to keep the program
running in the system tray.




Current issues:
=It's ugly.
-Barebones functionality.
-Audio format support is relatively limited due to using only pygame for audio
  play back(eg: 32-bit wavs are not supported.) This should be remedied by leveraging
  a system call to ffmpeg and streaming/reading the audio back to pygame as
  PCM audio. ffmpeg should provide all necessary format support.
-UIX is decidedly "janky" at the moment. Did I mention it's ugly?

Planned features:
Pitch/Tuning detection
BPM detection
Waveform image of selected file.
Ability to rename before moving.
Daemonized/system tray app to launch GUI

Requirements so far:
rumps
pygame
tkinter
