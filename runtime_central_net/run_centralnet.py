import os
import sys
from subprocess import Popen
import os, sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common.common import copy_file_local, open_config

config_params = open_config()

central_net_path = config_params["central_router_path"]
central_exe = config_params["central_router_exe"]

copy_file_local(os.path.join(central_net_path, central_exe), r".")

central_net_addr = config_params["central_net_addr"]
os.environ["GSB_URL"] = f"tcp://{central_net_addr}"

command = f".{os.path.sep}{central_exe}"
print(command)
with Popen(command, shell=True) as p1:
    pass

