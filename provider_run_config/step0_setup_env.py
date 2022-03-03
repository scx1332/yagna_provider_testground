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
GSB_PORT = 30401
API_PORT = 30402

with open(".env.template", "r") as f:
    template = f.read()
    template = template.replace("%%SUBNET%%", SUBNET_NAME)
    template = template.replace("%%NODE_NAME%%", NODE_NAME)
    template = template.replace("%%GSB_PORT%%", str(GSB_PORT))
    template = template.replace("%%API_PORT%%", str(API_PORT))
    with open(".env", "w") as f2:
        f2.write(template)








