import os
import random
import string
import sys 

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common.common import open_config

# run this script once to setup environment variables for provider

config = open_config()
SUBNET_NAME = config["subnet"]

randname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
NODE_NAME = f"req_node_{randname}"

GSB_PORT = config["requestor_port_gsb"]
API_PORT = config["requestor_port_yagna"]


if config["requestor_data_limiter"]:
    DATA_LIMITER_PORT = config["requestor_data_limiter_port"]
    CENTRAL_NET_HOST = f"127.0.0.1:{DATA_LIMITER_PORT}"
else:
    if config["use_own_central_net"]:
        CENTRAL_NET_HOST = config["central_net_addr"]
    else:
        CENTRAL_NET_HOST = "3.249.139.167:7464"


with open(".env", "w") as f2:
    if config["use_own_central_net"]:
        f2.write("CENTRAL_NET_HOST=" + config["central_net_addr"] + "\n")
    f2.write("YAGNA_DATADIR=yagna_dir\n")
    f2.write(f"SUBNET={SUBNET_NAME}\n")
    f2.write(f"NODE_NAME={NODE_NAME}\n")
    f2.write(f"GSB_URL=tcp://127.0.0.1:{GSB_PORT}\n")
    f2.write(f"YAGNA_API_URL=http://127.0.0.1:{API_PORT}\n")
    f2.write(f"YAGNA_MARKET_URL=http://127.0.0.1:{API_PORT}/market-api/v1/\n")
    f2.write(f"YAGNA_ACTIVITY_URL=http://127.0.0.1:{API_PORT}/activity-api/v1/\n")
    f2.write(f"YAGNA_PAYMENT_URL=http://127.0.0.1:{API_PORT}/payment-api/v1/\n")

if 0:
    with open(".env.template", "r") as f:
        template = f.read()
        template = template.replace("%%SUBNET%%", SUBNET_NAME)
        template = template.replace("%%NODE_NAME%%", NODE_NAME)
        template = template.replace("%%GSB_PORT%%", str(GSB_PORT))
        template = template.replace("%%API_PORT%%", str(API_PORT))
        template = template.replace("%%CENTRAL_NET_HOST%%", CENTRAL_NET_HOST)
        with open(".env", "w") as f2:
            f2.write(template)








