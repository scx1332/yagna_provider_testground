import os
from subprocess import Popen

yagna_exe_path = r"yagna.exe"
command = f"{yagna_exe_path} service run", shell=True
print(command)
p1 = Popen(command)

