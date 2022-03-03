import os
import random
import string

# run this script once to setup environment variables for provider


randname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

SUBNET_NAME = "localtest"
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








