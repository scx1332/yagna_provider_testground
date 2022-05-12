import os
import random
import string
import sys 

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common.common import open_config
# run this script once to setup environment variables for provider


randname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

config = open_config()

SUBNET_NAME = config["subnet"]
NODE_NAME = f"prov_node_{randname}"
GSB_PORT = config["provider_port_gsb"]
API_PORT = config["provider_port_yagna"]

if config["provider_data_limiter"]:
    DATA_LIMITER_PORT = config["provider_data_limiter_port"]
    CENTRAL_NET_HOST = f"127.0.0.1:{DATA_LIMITER_PORT}"
else:
    if config["use_own_central_net"]:
        CENTRAL_NET_HOST = config["central_net_addr"]
    else:
        CENTRAL_NET_HOST = config["3.249.139.167:7464"]


with open(".env.template", "r") as f:
    template = f.read()
    template = template.replace("%%SUBNET%%", SUBNET_NAME)
    template = template.replace("%%NODE_NAME%%", NODE_NAME)
    template = template.replace("%%GSB_PORT%%", str(GSB_PORT))
    template = template.replace("%%API_PORT%%", str(API_PORT))
    template = template.replace("%%CENTRAL_NET_HOST%%", CENTRAL_NET_HOST)
    with open(".env", "w") as f2:
        f2.write(template)








