import os
import shutil
from subprocess import Popen
import sys 

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common.common import copy_file_local, open_config



config_params = open_config()

yagna_exe = config_params["yagna_executable"]
gftp_exe = config_params["gftp_exe"]

source_yagna_directory = config_params["source_yagna_directory"]
target_yagna_directory = r"."


copy_file_local(os.path.join(source_yagna_directory, yagna_exe), target_yagna_directory)
copy_file_local(os.path.join(source_yagna_directory, gftp_exe), target_yagna_directory)

if config_params["requestor_data_limiter"]:
    data_limiter_path = config_params["data_limiter_path"]
    data_limiter_executable = config_params["data_limiter_executable"]
    copy_file_local(os.path.join(data_limiter_path, data_limiter_executable), ".")
    command_data_limiter = f".{os.path.sep}{data_limiter_executable}"
    print(command_data_limiter)



command = f".{os.path.sep}{yagna_exe} service run"
print(command)

with Popen(command, shell=True) as p1:
    pass

