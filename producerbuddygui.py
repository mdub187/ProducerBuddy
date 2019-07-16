import tkinter as tk
from tkinter import ttk
import helper
from pygame import mixer
import shutil
import os

class ProducerBuddyGUI():
    def __init__(self):
        self.unsorted_path = '/Users/dan/Production/Unsorted Samples/'
        self.target_path = '/Users/dan/Production/Downloaded Samples/'
        ##self.place()
        self.createwidgets()
        ##Start pygame audio:
        mixer.init()
        self.window.mainloop()

    def createwidgets(self):
        self.window = tk.Tk()
        self.window.config()

        self.unsorted_controls = tk.Frame(self.window)
        self.unsorted_controls.grid(column=0, row=0, ipadx=10, ipady=10)

        self.target_controls = tk.Frame(self.window)
        self.target_controls.grid(column=3, row=0, ipadx=10, ipady=10)

        self.unsorted_tree = self.createDirBrowser(self.unsorted_controls)
        self.target_tree = self.createDirBrowser(self.target_controls)

        button = tk.Button(self.window, text="Move", command=self.movebutton)
        button.grid(column=2,row=0)

        button = tk.Button(self.window, text="Play", command=self.playButton)
        button.grid(column=0,row=1)
        button = tk.Button(self.window, text="Stop", command=self.stopButton)
        button.grid(column=1,row=1)

        self.updatewidgets()

    def updatewidgets(self):
        self.updateUnsorted()
        self.updateDestination()

    def createDirBrowser(self, parent):
            vsb = ttk.Scrollbar(parent, orient="vertical")
            hsb = ttk.Scrollbar(parent, orient="horizontal")

            tree = ttk.Treeview(parent, columns=("fullpath", "type", "size"),
                displaycolumns="size", yscrollcommand=lambda f, l: helper.autoscroll(vsb, f, l),
                xscrollcommand=lambda f, l:helper.autoscroll(hsb, f, l))

            vsb['command'] = tree.yview
            hsb['command'] = tree.xview

            tree.heading("#0", text="Directory Structure", anchor='w')
            tree.column("#0", stretch=0,width=350)

            # Arrange the tree and its scrollbars in the toplevel
            tree.grid(column=0, row=0, sticky='e')
            vsb.grid(column=1, row=0, sticky='ns')
            hsb.grid(column=0, row=1, sticky='ew')

            return tree

    def stopButton(self):
        if mixer.music.get_busy():
            mixer.music.stop()
    ##Command to handle play button press.
    def playButton(self):
        selectedPath = os.path.realpath(self.get_sample_selection())
        if mixer.music.get_busy():
            mixer.music.stop()
        mixer.music.load(selectedPath)
        mixer.music.play()

    def updateUnsorted(self):
        ##Show the files, in the "unsorted", pane which can be
        ##sorted to the target pane.
        unsorted_dir = os.listdir(self.unsorted_path)
        for file_name in unsorted_dir:
            file_type = None
            full_path = os.path.join(self.unsorted_path, file_name).replace('\\', '/')
            if os.path.isdir(full_path): file_type = "directory"
            elif os.path.isfile(full_path):
                file_type = "file"
                self.unsorted_tree.insert("", 'end', text=file_name, values=[full_path] )

    def updateDestination(self, path=None, parent = ''):
        ##Show the directories, in the "target", pane where the
        ##samples from the "unsorted" pane can be moved to.
        ##This function is recursive.
        if path is None:
            path = self.target_path
        destination_dir = os.listdir(path)
        print(destination_dir)
        for file_name in destination_dir:
            file_type = None
            full_path = os.path.join(path, file_name)

            if os.path.isdir(full_path):
                id = self.target_tree.insert(parent,'end',text=file_name, values=[full_path])
                self.updateDestination(full_path, id)

    def movebutton(self):

        sample_path = self.get_sample_selection()
        target_path = self.gettargetselection() + "/"
        shutil.move(sample_path,target_path)
        self.updateUnsorted()

    def get_sample_selection(self):
        selected_sample_obj = self.unsorted_tree.item(self.unsorted_tree.selection())
        return selected_sample_obj['values'][0]
    def gettargetselection(self):
        selected_target_obj = self.target_tree.item(self.target_tree.selection())
        return selected_target_obj['values'][0]


    AUDIO_FORMATS = [
    "aiff",
    "wav",
    "mp3",
    "rex",
    "m4a",
    "ogg",
    "raw",
    "wma"
    ]

gui = ProducerBuddyGUI()
