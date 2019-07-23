import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import helper
from pygame import mixer
import shutil
import os
import yaml
from producerbuddycontroller import ProducerBuddyController, writeconfigtoyaml, validateconfig, SUPPORTED_SETTING_KEYS

#TODO: Move all non-GUI logic to producerbuddycontroller
class ProducerBuddyGUI():
    def __init__(self, pb_controller = None, config_file ='~/.producerbuddy.yml'):
        ##TODO: Add runtime options to specify alt config file.

        self.temp_settings = {}

        self.createwidgets()
        self.pb_controller = None
        self.config_file=os.path.expanduser('~/.producerbuddy.yml')

        ##Keep trying to load a controller until we get a config that loads...
        while self.pb_controller is None:
            try:
                self.pb_controller = ProducerBuddyController(self.config_file)
            except Exception as e:
                self.window.update()
                ##askyesnoquestion returns the following:
                ## yes: 1 (attempt to generate new config)
                ## no : 0 (prompt to broswe for new config)
                ##cancel: None (quit program)
                dialog_response =  messagebox.askyesnocancel("Can't load config...", "Can't load a config file, run set up? (No to select an existing config, Cancel to quit.)")

                if dialog_response == 1:
                    ##TODO: create interactive set up.
                    self.config_file='~/.producerbuddy.yml'
                    self.pb_controller = self.optiondialog()
                if dialog_response == 0:
                    user_selected_path = filedialog.askopenfilename()
                    if os.path.isfile(user_selected_path):
                        self.config_file=user_selected_path
                if dialog_response is None:
                    exit()
            if not self.pb_controller is None and not self.pb_controller.isconfigvalid():
                self.pb_controller = None
        self
        ##Start pygame audio:
        mixer.init()
        self.window.mainloop()

    def createwidgets(self):
        self.window = tk.Tk()
        self.window.config(padx=20,pady=20)
        self.window.title("ProducerBuddy")
        self.window.grid_columnconfigure(0,weight=1)
        self.window.grid_rowconfigure(0,weight=2)
        self.window.grid_columnconfigure(1,weight=0)
        self.window.grid_columnconfigure(2,weight=1)
        self.window.grid_rowconfigure(1,weight=0)

        self.unsorted_controls = tk.Frame(self.window, background="green")
        self.unsorted_controls.grid(column=0, row=0, sticky="NW")


        self.unsorted_select_button = tk.Button(self.unsorted_controls, text="self.unsorted_path", command=self.selectunsortedpath)
        self.unsorted_select_button.grid(column=0,row=0)


        self.target_controls = tk.Frame(self.window, background="blue")
        self.target_controls.grid(column=3, row=0, sticky="NE")


        self.unsorted_tree = self.createDirBrowser(self.unsorted_controls)
        self.target_tree = self.createDirBrowser(self.target_controls)
        target_select_button = tk.Button(self.target_controls, text="self.target_path", command=self.selecttargetpath)
        target_select_button.grid(column=0,row=0)


        button = tk.Button(self.window, text="Move", command=self.movebutton)
        button.grid(column=1,row=0)
        self.transport_controls = tk.Frame(self.window)
        self.transport_controls.grid(column=0, row=1, sticky="SW")
        button = tk.Button(self.transport_controls, text="Play", command=self.playButton)
        button.grid(column=0,row=1)
        button = tk.Button(self.transport_controls, text="Stop", command=self.stopButton)
        button.grid(column=1,row=1)

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
        selectedPath = os.path.expanduser(self.getsampleselection())
        if mixer.music.get_busy():
            mixer.music.stop()
        mixer.music.load(selectedPath)
        mixer.music.play()

    def populateUnsorted(self):
    #     ##Show the unsorted sample files, in the "unsorted" treeview, which can be
    #     ##sorted to the target pane.
    #     unsorted_dir = os.listdir(self.unsorted_path)
    #     for file_name in unsorted_dir:
    #         file_type = None
    #         full_path = os.path.join(self.unsorted_path, file_name).replace('\\', '/')
    #
    #         ##We only want to add files (not dirs) in supported audio formats to the list:
    #         if os.path.isfile(full_path):
    #
    #             file_base, file_ext = os.path.splitext(file_name)
    #             for supported_ext in self.AUDIO_FORMATS:
    #                 if supported_ext in file_ext:
    #                     self.unsorted_tree.insert("", 'end', text=file_name, values=[full_path] )
    #
        return None

    def populateDestination(self, path=None, parent = ''):
    #     ##Show the directories, in the "target", pane where the
    #     ##samples from the "unsorted" pane can be moved to.
    #     ##This function is recursive.
    #     if path is None:
    #         path = self.target_path
    #     destination_dir = os.listdir(path)
    #     for file_name in destination_dir:
    #         file_type = None
    #         full_path = os.path.join(path, file_name)
    #
    #         if os.path.isdir(full_path):
    #             id = self.target_tree.insert(parent,'end',text=file_name, values=[full_path])
    #             self.updateDestination(full_path, id)
        return None

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

    def newdirbutton():
        self.window.update()
        ##Add a new dir to the target directory.
        messagebox.showwarning("TODO")

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

    def selectincomingpath(self, initialdir=None):
        if initialdir is None:
            ##See if the typical downloads folder exists...
            download = os.path.expanduser("~/Downloads")
            if os.path.isdir(download):
                init_dir = download
            else:
                init_dir = None
            new_dir = filedialog.askdirectory(title="Select directory to move samples to:", initialdir=initialdir)
        return os.path.expanduser(new_dir)

    def selecttargetpath(self, initialdir=None, option_dialog=False):
        if initialdir is None:
            initialdir = os.path.expanduser("~/Music")
        new_dir = filedialog.askdirectory(title="Select directory to move samples to:", initialdir=initialdir)
        new_dir = os.path.expanduser(new_dir)
        if not option_dialog:
            return new_dir
        else:
            self.temp_settings['incoming_path'] = new_dir
    def selectunsortedpath(self, initialdir=None):
        if initialdir is None:
            new_dir = filedialog.askdirectory(title="Select directory to move samples to:", initialdir=initialdir)
        return os.path.realpath(new_dir)

    ##Runs config set up and returns a controller object.
    def optiondialog(self):
        if not os.path.isfile()
        writeconfigtoyaml(self.config_file)
        self.optiondialog = tk.Toplevel()
        self.optiondialog.config(padx=20,pady=20)
        self.optiondialog.title("ProducerBuddy")
        target_select_button = tk.Button(self.optiondialog, text="Select incoming dir...", command=self.selecttargetpath)
        target_select_button.grid(column=0,row=0)
        target_select_button = tk.Button(self.optiondialog, text="self.target_path", command=self.selecttargetpath)
        target_select_button.grid(column=0,row=2)
        target_select_button = tk.Button(self.optiondialog, text="self.target_path", command=self.selecttargetpath)
        target_select_button.grid(column=0,row=4)


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
