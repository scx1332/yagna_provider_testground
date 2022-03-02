import os
from subprocess import Popen
import shutil

import json

def open_config():
    if platform.system() == "Linux":
        config_path="config_linux.json"
    else:
        config_path="config.json"

    with open(config_path, "r") as f:
        return json.loads(f.read())

config_params = open_config()

yagna_exe_path = r"yagna.exe"

source_runtime_directory = config_params["step2"]["source_runtime_directory"]
target_runtime_directory = config_params["step2"]["target_runtime_directory"]

source_runtime_exe_directory = config_params["step2"]["source_runtime_exe_directory"]
target_runtime_exe_directory = config_params["step2"]["target_runtime_exe_directory"]

source_fileserver_directory = config_params["step2"]["source_fileserver_directory"]
target_fileserver_directory = config_params["step2"]["target_fileserver_directory"]

def copy_file_local(srcDir, targetDir):
    if os.path.isfile(srcDir):
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        shutil.copy2(srcDir, targetDir)


copy_file_local(os.path.join(source_runtime_directory, "bios-256k.bin"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "init"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "initramfs.cpio.gz"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "kvmvapic.bin"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "linuxboot_dma.bin"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "self-test.gvmi"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "ubuntu.gvmi"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "qemu-system-x86_64.exe"), target_runtime_directory)
copy_file_local(os.path.join(source_runtime_directory, "vmlinuz-virt"), target_runtime_directory)

copy_file_local(os.path.join(source_runtime_exe_directory, "ya-runtime-vm.exe"), target_runtime_exe_directory)

copy_file_local(os.path.join(source_fileserver_directory, "ya-vm-file-server.exe"), target_fileserver_directory)

yaprovider_exe_path = r"ya-provider.exe"

payment_init = Popen(f"{yagna_exe_path} payment init --receiver --network rinkeby --account 0xc596aee002ebe98345ce3f967631aaf79cfbdf41", shell=True)

with Popen(f"{yaprovider_exe_path} run", shell=True) as p1:
    pass

