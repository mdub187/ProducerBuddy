import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import helper
import shutil
import os
import yaml
from producerbuddycontroller import ProducerBuddyController
from producerbuddyaudiocontroller import AudioController, AudioTimer
from tktimerwidget import TkTimer
from time import sleep
#TODO: Move all non-GUI logic to producerbuddycontroller
class ProducerBuddyGUI():
    def __init__(self, pb_controller = None, config_path ='~/.producerbuddy.yml'):
        ##TODO: Add runtime options to specify alt config file.


        self.pb_controller = None
        self.config_path = os.path.expanduser('~/.producerbuddy.yml')

        self.pb_controller = ProducerBuddyController(self.config_path)
        self.working_config = {}

        self.audio_controller = AudioController()
        self.audio_timer = AudioTimer(self.audio_controller)
        self.createwidgets()
        self.updatewidgets()
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

        ##Create stringVars for various things...
        self.incoming_path_stringVar = tk.StringVar()
        self.unsorted_path_stringVar = tk.StringVar()
        self.sorted_path_stringVar = tk.StringVar()

        self.unsorted_controls = tk.Frame(self.window, background="green")
        self.unsorted_controls.grid(column=0, row=0, sticky="NW")

        buttontextvar = tk.StringVar()

        self.unsorted_select_button = tk.Button(self.unsorted_controls, textvariable=self.unsorted_path_stringVar, command=self.selectunsortedpath)
        self.unsorted_select_button.grid(column=0,row=0)

        self.sorted_controls = tk.Frame(self.window, background="blue")
        self.sorted_controls.grid(column=2, row=0, sticky="NE")
        self.file_controls = tk.Frame(self.window, background="red")
        self.file_controls.grid(column=1, row=0, sticky="N")

        self.unsorted_tree = self.createDirBrowser(self.unsorted_controls)
        self.sorted_tree = self.createDirBrowser(self.sorted_controls)
        sorted_select_button = tk.Button(self.sorted_controls,  textvariable=self.sorted_path_stringVar, command=self.selectsortedpath)
        sorted_select_button.grid(column=0,row=0)


        button = tk.Button(self.file_controls, text=">> Move >>", command=self.movebutton)
        button.grid(row=1)
        button = tk.Button(self.file_controls, text="Configuration", command=self.optiondialog)

        button.grid(row=0)
        button = tk.Button(self.file_controls, text="Import Samples", command=self.importunsorted)
        button.grid(row=2)
        self.transport_controls = tk.Frame(self.window)
        self.transport_controls.grid(column=0, row=1, sticky="SW")
        button = tk.Button(self.transport_controls, text="Play", command=self.playButton)
        button.grid(column=0,row=1)
        button = tk.Button(self.transport_controls, text="Stop", command=self.stopButton)
        button.grid(column=1,row=1)

        self._elapsed_time_display = TkTimer(self.transport_controls, self.audio_timer)
        self._elapsed_time_display.widget.grid(column=1,row=0)
        ##Start loop to update timer:
        self.update_audio_timer_loop()

    def updatewidgets(self):
        self.populateUnsorted(refresh=True)
        self.populateSorted(refresh=True)
        self.unsorted_path_stringVar.set(self.pb_controller.unsorted_path)
        self.sorted_path_stringVar.set(self.pb_controller.sorted_path)
        self.incoming_path_stringVar.set(self.pb_controller.incoming_path)

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
        self.audio_controller.stop_audio()

    ##Command to handle play button press.
    def playButton(self):
        selectedPath = os.path.expanduser(self.getsampleselection())
        self.audio_controller.stop_audio()
        self.audio_controller.load_audio(selectedPath)
        self.audio_controller.play_audio(selectedPath)


    def populateUnsorted(self,parent='', dir_node=None, refresh=False):
        if refresh:
            self.pb_controller.scanunsorted()
        if dir_node == None:
            ##Clear existing nodes
            for child in self.unsorted_tree.get_children():
                self.unsorted_tree.delete(child)

            dir_node = self.pb_controller.unsorted_dir.copy()
        for n in dir_node:
            node = dir_node[n]
            n_type = node.get('type')
            if n_type == 'dir':
                id=self.unsorted_tree.insert(parent,'end',text=n)
                self.populateUnsorted(id,node.get("dir_list", False))
            elif not n_type is None:
                abs_path = node.get('abs_path')
                id = self.unsorted_tree.insert(parent,'end',text=n)
                self.unsorted_tree.set(id, 0, abs_path)

    def populateSorted(self,parent='', dir_node=None, refresh=False):
        ##Show the directories, in the "sorted", pane where the
        ##samples from the "unsorted" pane can be moved to.
        ##This function is recursive.
        if refresh:
            self.pb_controller.scansorted()
        if dir_node == None:
            for item_id in self.sorted_tree.get_children():
                self.sorted_tree.delete(item_id)
            dir_node = self.pb_controller.sorted_dir.copy()
        for n in dir_node:
            node = dir_node[n]
            if node.get('type') == 'dir':
                abs_path = node.get('abs_path')
                id = self.sorted_tree.insert(parent,'end',text=n)
                self.sorted_tree.set(id, 0, abs_path)
                self.populateSorted(id,node.get("dir_list", False))

    def importunsorted(self):

        ##Import destination.
        dst=self.pb_controller.unsorted_path
        incoming=self.pb_controller.incoming_path
        title="ProducerBuddy - Import Samples from {}".format(incoming)
        message_string = " Importing Samples from\r\n {}\r\n".format(incoming)
        import_list = self.pb_controller.importlist(refresh=True)
        count = len(import_list)

        if count == 0:
            message_string += "No new samples to move!"
            messagebox.showinfo(title, message_string)

        elif count > 0:
            message_string += "Found the following: \r\n"

            for l in import_list:
                path, filename = os.path.split(l)
                message_string += "{}\r\n".format(filename)

            message_string += "\r\nTotal count: {}\r\n".format(count)
            message_string += "\r\nProceed with moving samples to destination?:\r\n{}".format(dst)
            user_confirm_move = messagebox.askyesno(title, message_string)
            confirm_for_all_checked = False

            if user_confirm_move:
                for src in import_list:
                    path, filename = os.path.split(src)

                    try:
                        shutil.move(src,dst)
                    except Exception as e:
                        error = e.args[0]
                        if 'already exists' in error:
                            error_message_string = "{} already exists in unsorted directory, overwrite?".format(filename)
                            confirm_clobber = messagebox.askyesno(title, error_message_string)
                            if confirm_clobber:
                                try:
                                    shutil.copy(src,dst)
                                    os.remove(src)
                                except Exception as e:
                                    messagebox.showwarning("FATAL ERR0R", e)
            self.populateUnsorted(refresh=True)

    def movebutton(self):
        sample_path = self.getsampleselection()
        sorted_path = self.getsortedselection()

        if sample_path is None or sorted_path is None:
            messagebox.showwarning("ProducerBuddy", "You must select a source sample (left pane), AND a target folder (right pane).")
        elif not os.path.isdir(sorted_path):
            ##Will add the ability to make existing sorted samples visible
            messagebox.showwarning("ProducerBuddy", "Target selection (right pane) MUST be a directory.")
        else:
        ##sorted path is a directory, add a trailing slash
            sorted_path = os.path.join(sorted_path, "")

            move_result = self.pb_controller.movesample(sample_path, sorted_path)

            if not move_result == 1 :
                ##FIXME: Add rename/clobber/createDirBrowser handling.
                sample_base = os.path.basename(sample_path)
                messagebox.showwarning("ProducerBuddy", "There was an issue moving {}".format(sample_base))
            self.populateUnsorted()

    def newdirbutton():
        self.window.update()
        ##Add a new dir to the sorted directory.
        messagebox.showwarning("TODO")

    def getsampleselection(self):
        selected = self.unsorted_tree.selection()
        ##If our selection was empty, we return none.
        if not selected:
            return None
        else:
            selected_sorted_obj = self.unsorted_tree.item(selected)
            return selected_sorted_obj['values'][0]

    def getsortedselection(self):
        selected = self.sorted_tree.selection()
        ##If our selection was empty, we return none.
        if not selected:
            return None
        else:
            selected_sorted_obj = self.sorted_tree.item(selected)
            return selected_sorted_obj['values'][0]

    def selectincomingpath(self, initialdir=None, targetStringVar=None, updatecontroller=True):
        if initialdir is None:
            if not self.pb_controller.getsetting("incoming_path") is None:
                initialdir = self.pb_controller.getsetting("incoming_path")
            else:
                ##See if the typical downloads folder exists...
                music_path = os.path.expanduser("~/Downloads")
                if os.path.isdir(music_path):
                    initialdir = music_path
                else:
                    initialdir = None
        new_dir = filedialog.askdirectory(title="Select directory to move samples to:", initialdir=initialdir)
        if not targetStringVar is None:
            targetStringVar.set(new_dir)
        self.working_config['incoming_path'] = new_dir

    def selectunsortedpath(self, initialdir=None, targetStringVar=None, updatecontroller=True):
        if initialdir is None:
            ##See if the typical downloads folder exists...
            music_path = os.path.expanduser("~/Music")
            if os.path.isdir(music_path):
                initialdir = music_path
            else:
                initialdir = None
        new_dir = filedialog.askdirectory(title="Select directory to move samples to:", initialdir=initialdir)
        if not targetStringVar is None:
            targetStringVar.set(new_dir)
        self.working_config['unsorted_path'] = new_dir

    def selectsortedpath(self, initialdir=None, targetStringVar=None, updatecontroller=True):
        if initialdir is None:
            ##See if the typical downloads folder exists...
            music_path = os.path.expanduser("~/Music")
            music_path = os.path.join(music_path, "")
            if os.path.isdir(music_path):
                initialdir = music_path
            else:
                initialdir = None
        new_dir = filedialog.askdirectory(title="Select directory to move samples to:", initialdir=initialdir)
        if not targetStringVar is None:
            targetStringVar.set(new_dir)
        self.working_config['sorted_path'] = new_dir

    ##Runs config set up and returns a controller object.
    def optiondialog(self):
        optiondialog = tk.Toplevel()
        optiondialog.config(padx=20,pady=20)
        optiondialog.title("ProducerBuddy")

        stringVars = {}
        original_settings = {}
        working_settings = {}
        for k in ["incoming_path","unsorted_path","sorted_path"]:
            stringVars[k] = tk.StringVar()
            original_settings[k] = self.pb_controller.getsetting(k)
            stringVars[k].set(original_settings[k])
            working_settings[k] = stringVars[k].get()
        ##Copy our original settings to a working copy...
        working_settings = original_settings.copy()

        button = tk.Button(optiondialog, text="Select Incoming/Download directory (Optional)", command=lambda: self.selectincomingpath(targetStringVar=stringVars['incoming_path']))
        button.grid(column=1,row=0)
        label  = tk.Label(optiondialog, textvariable=stringVars["incoming_path"], width=40)
        label.grid(column=2,row=0)
        button = tk.Button(optiondialog, text="Select Unosrted Sample directory.", command=lambda: self.selectunsortedpath(targetStringVar=stringVars['unsorted_path']))
        button.grid(column=1,row=2)
        label  = tk.Label(optiondialog, textvariable=stringVars["unsorted_path"], width=40)
        label.grid(column=2,row=2)
        button = tk.Button(optiondialog, text="Choose Sorted Sample directory.", command=lambda: self.selectsortedpath(targetStringVar=stringVars['sorted_path']))
        button.grid(column=1,row=3)
        label  = tk.Label(optiondialog, textvariable=stringVars["sorted_path"], width=40)
        label.grid(column=2,row=3)
        button = tk.Button(optiondialog, text="Cancel", command=optiondialog.destroy)
        button.grid(column=0, row=5)
        button = tk.Button(optiondialog, text="Apply", command=lambda: self.applyconfig(optiondialog))
        button.grid(column=3, row=5)

    def applyconfig(self,  frame=None):

        self.pb_controller.saveconfig(self.working_config)
        self.working_config.clear()
        if not frame is None:
            if isinstance(frame, tk.Toplevel):
                frame.destroy()
        self.updatewidgets()

    def update_audio_timer_loop(self):
        if self.audio_controller.is_playing():
            self._elapsed_time_display.update_widget()

        self.window.after(1,self.update_audio_timer_loop)
gui = ProducerBuddyGUI()
