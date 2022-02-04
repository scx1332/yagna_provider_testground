import os
from subprocess import Popen

yagna_exe_path = r"yagna.exe"
command = f"{yagna_exe_path} service run"
print(command)
p1 = Popen(command, shell=True)

