import os
import shutil
import sys
from subprocess import Popen
import json

config_params = {}
with open("config.json", "r") as f:
    config_params = json.loads(f.read())

source_yagna_directory = config_params["source_yagna_directory"]
target_yagna_directory = r"."

print(config_params)

def copy_file_local(srcDir, targetDir):
    if os.path.isfile(srcDir):
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        shutil.copy2(srcDir, targetDir)
    else:
	    print("Yagna.exe not found, alter config.json")
	    sys.exit()


yagna_exe = config_params["yagna_executable"]
copy_file_local(os.path.join(source_yagna_directory, yagna_exe), target_yagna_directory)

command = f"{yagna_exe} service run"
print(command)
p1 = Popen(command, shell=True)

