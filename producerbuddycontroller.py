import shutil
import os
import yaml

SUPPORTED_AUDIO_FORMATS = [
"aiff",
"wav",
"mp3",
"rex",
"m4a",
"ogg",
"raw",
"wma"
]

SUPPORTED_SETTING_KEYS = [
"incoming_path",
"unsorted_path",
"sorted_path"
]

OPTIONAL_SETTING_KEYS = []

DEFAULT_CONFIG_PATH = "~/.producerbuddy.yml"

class ProducerBuddyController():
    ##Will throw exception if config file can't be loaded
    def __init__(self, yaml_path=DEFAULT_CONFIG_PATH):
        yaml_path = os.path.expanduser(yaml_path)
        if not os.path.isfile(yaml_path):
            writeconfigtoyaml(yaml_path)
        self.config_options = yaml.safe_load(yaml_path)
        self.valid_config = self.isconfigvalid()
        self.updatedirtrees()


    def scandirectories(self):
        if self.valid_config:
            self.scanincoming()
            self.scanunsorted()
            self.scansorted()

    def scanincoming(self):
        ##Construct directory listing for the unsorted sample dir.
        incoming_path = self.config_options.get("incoming_path")
        incoming_path = os.path.expanduser(incoming_path)
        self.incoming_dir = self.scanDir(unsorted_path)

    def scanunsorted(self):
        ##Construct directory listing for the unsorted sample dir.
        unsorted_path = self.config_options.get("unsorted_path")
        unsorted_path = os.path.expanduser(unsorted_path)
        self.unsorted_dir = self.scanDir(unsorted_path)

    def scansorted(self):
        ##Construct directory listing for the unsorted sample dir.
        sorted_path = self.config_options.get("sorted_path")
        sorted_path = os.path.expanduser(sorted_path)
        self.sorted_dir = self.scanDir(sorted_path)

    def scandir(self, path=None, recursive=True, current_depth=0):

        if path is None or not os.path.isdir(path):
            return None
        ##Default to five layers deep if not sepcified in configs.
        max_depth = self.config_options.get("max_depth", 5)

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
                    current_item_dir_list = self.scanDir(abs_path + "/", True, current_depth + 1)
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

    def checksupportedformats(self, file_name):
        file_name, file_ext = os.path.splitext(file_name)
        for format in SUPPORTED_AUDIO_FORMATS:
            if format.lower() in file_ext.lower():
                return format.lower()

        ##Return none if our file type doesn't match a supported ext:
        return None

    ##If our validateconfig function returns an empty array, it means
    ##there are no invalid config options and the required config options
    ##are valid.
    def isconfigvalid(self):
        if len(validateconfig(self.config_options)) == 0:
            return True
        else:
            return False

def writeconfigtoyaml(yaml_path, config_options={}):
    yaml_path = os.path.expanduser(yaml_path)
    print("Path is " + yaml_path)
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
##Returns a list of invalid config settings.
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
        elif "path" in key:
            path_to_validate = config_options[key]
            path_to_validate = os.path.expanduser(path_to_validate)

    ##Make sure all required settings are present:
        for key in SUPPORTED_SETTING_KEYS:
            ##If the key isn't already marked invalid and is not
            ##marked as optional and doesn't existing in our
            ##config option keys.
            if key not in invalid_keys and key not in OPTIONAL_SETTING_KEYS and key not in config_options.keys():
                invalid_keys.append(key)
    return invalid_keys
