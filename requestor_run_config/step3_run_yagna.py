import os
import shutil
from subprocess import Popen
import platform
import json

def open_config():
    if platform.system() == "Linux":
        config_path= os.path.join("..", "config_linux.json")
    else:
        config_path= os.path.join("..", "config.json")

    with open(config_path, "r") as f:
        return json.loads(f.read())


config_params = open_config()

yagna_exe = config_params["yagna_executable"]
source_yagna_directory = config_params["source_yagna_directory"]
target_yagna_directory = r"."

def copy_file_local(srcDir, targetDir):
    if os.path.isfile(srcDir):
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        shutil.copy2(srcDir, targetDir)


copy_file_local(os.path.join(source_yagna_directory, yagna_exe), target_yagna_directory)

command = f".{os.path.sep}{yagna_exe} service run"
print(command)

with Popen(command, shell=True) as p1:
    pass

