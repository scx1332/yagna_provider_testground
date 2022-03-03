import os
import sys
from subprocess import Popen
import os, sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common.common import copy_file_local, open_config

config_params = open_config()

source_yagna_directory = config_params["source_yagna_directory"]
target_yagna_directory = r"."


yagna_exe = config_params["yagna_executable"]
copy_file_local(os.path.join(source_yagna_directory, yagna_exe), target_yagna_directory)

command = f".{os.path.sep}{yagna_exe} service run"
print(command)
with Popen(command, shell=True) as p1:
    pass

