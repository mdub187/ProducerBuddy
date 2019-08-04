import shutil, os, yaml, re

SUPPORTED_AUDIO_FORMATS = [
"aiff",
"wav",
"mp3",
"rex",
"m4a",
"ogg",
"raw",
"wma",
"aif"
]

SUPPORTED_SETTING_KEYS = [
"incoming_path",
"unsorted_path",
"sorted_path"
]

OPTIONAL_SETTING_KEYS = ["incoming_path"]

DEFAULT_CONFIG_PATH = "~/.producerbuddy.yml"

class ProducerBuddyController():
    ##Will throw exception if config file can't be loaded
    def __init__(self, yaml_path=DEFAULT_CONFIG_PATH):
        self.yaml_path = os.path.expanduser(yaml_path)
        if not os.path.isfile(self.yaml_path):
            writeconfigtoyaml(self.yaml_path)
        with open(self.yaml_path, "r") as read_handle:
            self.saved_config = yaml.safe_load(read_handle)

        self.incoming_path = self.saved_config.get('incoming_path')
        self.unsorted_path = self.saved_config.get('unsorted_path')
        self.sorted_path = self.saved_config.get('sorted_path')
        self.max_depth = 5

    def scandirectories(self):
        self.scanincoming()
        self.scanunsorted()
        self.scansorted()

    def scanincoming(self):
        ##Construct directory listing for the unsorted sample dir.
        if os.path.isdir(self.incoming_path):
            incoming_path = self.incoming_path
            incoming_path = os.path.expanduser(incoming_path)
            self.incoming_dir = self.scandir(incoming_path, recursive=False)

    def scanunsorted(self):
        if os.path.isdir(self.unsorted_path):
        ##Construct directory listing for the unsorted sample dir.
            unsorted_path = self.unsorted_path
            unsorted_path = os.path.expanduser(unsorted_path)
            self.unsorted_dir = self.scandir(unsorted_path)

    def scansorted(self):
        if os.path.isdir(self.sorted_path):
        ##Construct directory listing for the unsorted sample dir.
            sorted_path = self.sorted_path
            sorted_path = os.path.expanduser(sorted_path)
            self.sorted_dir = self.scandir(sorted_path)

    def scandir(self, path=None, recursive=True, current_depth=0):

        if path is None or not os.path.isdir(path):
            return None
        ##Default to five layers deep if not sepcified in configs.
        max_depth = self.max_depth

        dir_list = os.listdir(path)
        current_tree = {}

        for entry in dir_list:
            abs_path = os.path.join(path, entry)
            if os.path.isfile(abs_path):
                current_item = {
                    "type" : self.checksupportedformats(entry),
                    "abs_path" : abs_path
                }
                current_tree[entry] = current_item
            elif os.path.isdir(abs_path):
                ##If we have not scanned past are max depth and recursion is
                ##is enabled, recursively scan the directory.
                if current_depth <= max_depth and recursive:
                    current_item_dir_list = self.scandir(abs_path + "/", True, current_depth + 1)
                    current_item = {
                        "type" : "dir",
                        "abs_path" : abs_path,
                        "dir_list" : current_item_dir_list
                    }
                else:
                    current_item = {
                        "type" : "dir",
                        "abs_path" : abs_path,
                        "dir_list" : None
                    }
                current_tree[entry] = current_item

        return current_tree

    ##Return a list of abs_path for files that can be imported. Not recursive.
    def importlist(self,dir_node=None, refresh=False):
        if refresh:
            self.scanincoming()
        if dir_node is None:
            dir_node = self.incoming_dir

        import_list = []

        for n in dir_node:
            node = dir_node[n]
            n_type = node.get('type')
            if not n_type is None and not n_type == 'dir':
                abs_path = node.get('abs_path')
                import_list.append(abs_path)
        return import_list

    ##Returns false if there is a problem, returns 0 if the src file_name
    ##already exists in the dst dir. Returns 1 if successful move.
    def movesample(self, sample_src, sample_dst, clobber=False, rename=False):

        if os.path.isfile(sample_src) and os.path.isdir(sample_dst):
            src_base = os.path.basename(sample_src)
            target_dst = os.path.join(sample_dst, src_base)
            if os.path.isfile(target_dst):
                if clobber:
                    shutil.copy(sample_src, target_dst)
                    os.remove(sample_src)
                    self.scansorted()
                    self.scanunsorted()
                    return 1
                if rename:
                    src_base = incrementfilename(src_base)
                    ##Make sure our new file name does not exist, if it does
                    ##increment again.
                    target_dst = os.path.join(sample_dst, src_base)
                    shutil.move(sample_src, target_dst)
                    self.scansorted()
                    self.scanunsorted()
                    return 1
                else:
                    return 0
            else:
                shutil.move(sample_src, target_dst)
                self.scansorted()
                self.scanunsorted()
                return 1
        else:
            return False


    def importunsorted(self,import_list=None):
        if import_list is None:
            import_list = self.importlist(refresh=True)

        dst = self.unsorted_path
        for src in import_list:
            try:
                shutil.move(src, dst)
            except Exception as e:
                return

    def checksupportedformats(self, file_name):
        file_name, file_ext = os.path.splitext(file_name)
        for format in SUPPORTED_AUDIO_FORMATS:
            if format.lower() in file_ext.lower():
                return format.lower()

        ##Return none if our file type doesn't match a supported ext:
        return None

    def saveconfig(self, working_config=None):

        current_config = {}
        if not working_config is None:
            for k in working_config:
                if k in SUPPORTED_SETTING_KEYS:
                    current_config[k] = working_config[k]
                    setattr(self,k,current_config[k])


        for k in SUPPORTED_SETTING_KEYS:
            if not k in current_config.keys():
                current_config[k] = self.getsetting(k)
        writeconfigtoyaml(self.yaml_path, current_config)

    def getsetting(self, setting_name):
        if hasattr(self, setting_name):
            return getattr(self,setting_name)
        else:
            return None


def writeconfigtoyaml(yaml_path, config_options={}):
    yaml_path = os.path.expanduser(yaml_path)
    ##Make sure we have default options.
    for key in SUPPORTED_SETTING_KEYS:
        if not key in config_options.keys():
            config_options[key] = None

    ##Remove any extraneous, unsupported options:
    for key in config_options.keys():
        if not key in SUPPORTED_SETTING_KEYS:
            del config_options[key]

    ##Write to file
    yaml_path = os.path.expanduser(yaml_path)
    with open(yaml_path, "w") as write_handle:
        yaml.dump(config_options, write_handle, default_flow_style=False)

##Check the provided config dictionary and verify the settings are correct.
##Returns a list of invalid config settings, list is empty if all required
##settings are valid.
def validateconfig(config_options):
    provided_config_keys = config_options.keys()
    invalid_keys = []
    ##Don't try to validate extraneous, unsupported options:
    for key in provided_config_keys:

        if key not in SUPPORTED_SETTING_KEYS:
            del config_options[key]
            continue
        ##Begin validating supported settings.
        ##Check that the path actually exists.
        currentvalue = config_options[key]
        ##If the key doesn't exist in the optional settings, then
        ##it is invalid.
        if currentvalue is None and key not in OPTIONAL_SETTING_KEYS:
            invalid_keys.append(key)
            continue
        ##If the key is empty but not required we just skip it...
        elif currentvalue is None and key in OPTIONAL_SETTING_KEYS:
            continue
        elif "path" in key:
            path_to_validate = os.path.expanduser(currentvalue)


    ##Make sure all required settings are present:
        for key in SUPPORTED_SETTING_KEYS:
            ##If the key isn't already marked invalid and is not
            ##marked as optional and doesn't exist in our
            ##config option keys.
            if key not in invalid_keys and key not in OPTIONAL_SETTING_KEYS and key not in config_options.keys():
                invalid_keys.append(key)
    return invalid_keys

def incrementfilename(file_name):
    ##FIXME: placeholder functionality
    ##TODO: Check if filename ends with a number already. If it does, increment
    ##that number
    file_base, file_ext = os.path.splitext(file_name)

    return file_base + "renamed" + file_ext
