import os
import shutil
from subprocess import Popen

yagna_exe_path = r"yagna.exe"

source_yagna_directory = r"C:\golem\yagna\target\debug"
target_yagna_directory = r"."

def copy_file_local(srcDir, targetDir):
    if os.path.isfile(srcDir):
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        shutil.copy2(srcDir, targetDir)


copy_file_local(os.path.join(source_yagna_directory, "yagna.exe"), target_yagna_directory)

command = f"{yagna_exe_path} service run"
print(command)
p1 = Popen(command, shell=True)

