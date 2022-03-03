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

with open(".env.template", "r") as f:
    template = f.read()
    template = template.replace("%%SUBNET%%", SUBNET_NAME)
    template = template.replace("%%NODE_NAME%%", NODE_NAME)
    with open(".env", "w") as f2:
        f2.write(template)








