from sys import argv, exit
import os
import shutil


##Static variables
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

##Directory locations
cl_arg_list = argv

if len(cl_arg_list) < 3:
    script_name = cl_arg_list[0]
    print ("Usage: '{} /path/to/incoming /path/to/destination".format(script_name))
    exit(1)

incoming = cl_arg_list[1]
destination = cl_arg_list[2]

incoming_files = os.listdir(incoming)

for file in incoming_files:
    file_name, file_ext = os.path.splitext(file)
    for format_ext in AUDIO_FORMATS:
        if format_ext in file_ext:
            old_path = incoming + file
            new_path = destination + file
            print(" Moving file '"+ old_path +"' to ' "+ new_path +"'.")
            shutil.move(old_path, new_path)
