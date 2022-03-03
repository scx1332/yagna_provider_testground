import os
import shutil
import platform
import json

def open_config():
    if platform.system() == "Linux":
        config_path= os.path.join("..", "config_linux.json")
    else:
        config_path= os.path.join("..", "config.json")

    with open(config_path, "r") as f:
        return json.loads(f.read())

def copy_file_local(srcDir, targetDir):
    # if os.path.isfile(srcDir):
    try:
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        shutil.copy2(srcDir, targetDir)
    except Exception as e:
        print(f"ERROR: while copying file {srcDir}, reason {e}")
        raise Exception(f"ERROR: while copying file {srcDir}, reason {e}")