import os
from subprocess import Popen

yaprovider_exe_path = r"ya-provider.exe"

p1 = Popen(f"{yaprovider_exe_path} run", shell=True)

