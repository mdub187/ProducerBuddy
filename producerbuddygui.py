import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import helper
from pygame import mixer
import shutil
import os
import yaml

class ProducerBuddyGUI():
    def __init__(self):

        with open('./settings.yml', "r") as yaml_file:
            self.yaml_settings = yaml.safe_load(yaml_file)

        self.unsorted_path = os.path.expanduser(self.yaml_settings.get('unsorted_path'))
        self.target_path = os.path.expanduser(self.yaml_settings.get('target_path'))

        self.createwidgets()
        ##Start pygame audio:
        mixer.init()
        self.window.mainloop()

    def createwidgets(self):
        self.window = tk.Tk()
        self.window.config()

        self.unsorted_controls = tk.Frame(self.window)
        self.unsorted_controls.grid(column=0, row=0, ipadx=10, ipady=10)
        self.unsorted_select_button = tk.Button(self.unsorted_controls, text=self.unsorted_path, command=self.selectunsortedpath)
        self.unsorted_select_button.grid(column=0,row=0)


        self.target_controls = tk.Frame(self.window)
        self.target_controls.grid(column=3, row=0, ipadx=10, ipady=10)

        self.unsorted_tree = self.createDirBrowser(self.unsorted_controls)
        self.target_tree = self.createDirBrowser(self.target_controls)
        self.target_select_button = tk.Button(self.target_controls, text=self.target_path, command=self.selecttargetpath)
        self.target_select_button.grid(column=0,row=0)


        button = tk.Button(self.window, text="Move", command=self.movebutton)
        button.grid(column=2,row=0)
        self.transport_controls = tk.Frame(self.window)
        self.transport_controls.grid(column=0, row=1)
        button = tk.Button(self.transport_controls, text="Play", command=self.playButton)
        button.grid(column=0,row=1)
        button = tk.Button(self.transport_controls, text="Stop", command=self.stopButton)
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
            tree.grid(column=0, row=1, sticky='e')
            vsb.grid(column=1, row=1, sticky='ns')
            hsb.grid(column=0, row=2, sticky='ew')

            return tree

    def stopButton(self):
        if mixer.music.get_busy():
            mixer.music.stop()
    ##Command to handle play button press.
    def playButton(self):
        selectedPath = os.path.realpath(self.getsampleselection())
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
        for file_name in destination_dir:
            file_type = None
            full_path = os.path.join(path, file_name)

            if os.path.isdir(full_path):
                id = self.target_tree.insert(parent,'end',text=file_name, values=[full_path])
                self.updateDestination(full_path, id)

    def movebutton(self):
        sample_path = self.getsampleselection()
        target_path = self.gettargetselection()
        if not sample_path is None and not target_path is None:
            target_path += '/'
            shutil.move(sample_path,target_path)
            self.unsorted_tree.delete(*self.unsorted_tree.get_children())
            self.updateUnsorted()
        else:
            messagebox.showwarning("ProducerBuddy", "You must select a sample AND a destination!")

    def getsampleselection(self):
        selected = self.unsorted_tree.selection()
        ##If our selection was empty, we return none.
        if not selected:
            return None
        else:
            selected_sample_obj = self.unsorted_tree.item(selected)
            return selected_sample_obj['values'][0]

    def gettargetselection(self):
        selected = self.target_tree.selection()
        ##If our selection was empty, we return none.
        if not selected:
            return None
        else:
            selected_target_obj = self.target_tree.item()
            return selected_target_obj['values'][0]

    def selectunsortedpath(self, new_dir=None):
        if new_dir is None:
            new_dir = filedialog.askdirectory()
        self.unsorted_path = os.path.realpath(new_dir)
        self.unsorted_select_button["text"] = self.unsorted_path
        self.unsorted_tree.delete(*self.unsorted_tree.get_children())
        self.updateUnsorted()

    def selecttargetpath(self, new_dir=None):
        if new_dir is None:
            new_dir = filedialog.askdirectory()

        self.target_path = os.path.realpath(new_dir)
        self.target_select_button["text"] = self.target_path
        self.target_tree.delete(*self.target_tree.get_children())
        self.updateDestination()

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
