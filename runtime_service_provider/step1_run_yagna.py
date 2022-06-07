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

if config_params["provider_data_limiter"]:
    data_limiter_path = config_params["data_limiter_path"]
    data_limiter_executable = config_params["data_limiter_executable"]
    copy_file_local(os.path.join(data_limiter_path, data_limiter_executable), ".")
    limiter_port = config_params["provider_data_limiter_port"]
    listen_addr = f"127.0.0.1:{limiter_port}"
    central_net_addr = config_params["central_net_addr"]
    command_data_limiter = f".{os.path.sep}{data_limiter_executable} --listen-addr={listen_addr} --target-addr={central_net_addr}"
    print(command_data_limiter)
    p2 = Popen(command_data_limiter, shell=True);

command = f".{os.path.sep}{yagna_exe} service run"
print(command)
with Popen(command, shell=True) as p1:
    pass

