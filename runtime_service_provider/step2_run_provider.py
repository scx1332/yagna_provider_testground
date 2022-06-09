import os
import subprocess
import platform
import json
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common.common import copy_file_local, open_config, set_yagna_app_key_to_env

config_params = open_config()

yagna_exe = config_params["yagna_executable"]

set_yagna_app_key_to_env(f".{os.path.sep}{yagna_exe}")

ya_runtime_vm_directory = config_params["step2"]["ya_runtime_vm_directory"]

plugins_directory = "plugins"
target_runtime_directory = os.path.join("plugins", "ya-runtime-vm", "runtime")
target_runtime_exe_directory = os.path.join("plugins", "ya-runtime-vm")


qemu_executable = config_params["step2"]["qemu_executable"]

#copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "bios-256k.bin"), target_runtime_directory)
#copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "kvmvapic.bin"), target_runtime_directory)
#copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "linuxboot_dma.bin"), target_runtime_directory)
#copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", qemu_executable), target_runtime_directory)
#copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "image", "self-test.gvmi"), target_runtime_directory)
#copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "init-container", "initramfs.cpio.gz"), target_runtime_directory)
#copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "init-container", "vmlinuz-virt"), target_runtime_directory)

ya_runtime_service_path = config_params["service_plugin_path"]
ya_runtime_service_exe = config_params["service_plugin_exe"]
ya_runtime_proxy_exe = config_params["service_proxy_exe"]

bor_plugin_directory = os.path.join(plugins_directory, "ya-runtime-bor")

copy_file_local(os.path.join(ya_runtime_service_path, ya_runtime_service_exe), bor_plugin_directory)
copy_file_local(os.path.join(ya_runtime_service_path, ya_runtime_proxy_exe), bor_plugin_directory)


#fix config file on windows (adding .exe to executable is needed)
#if platform.system() == "Windows":
    #with open(os.path.join(plugins_directory, "ya-runtime-vm.json"), "r") as fixFile:
    #    text_to_fix = fixFile.read()

    #text_to_fix = text_to_fix.replace('"exe-unit"', '"exe-unit.exe"')
    #text_to_fix = text_to_fix.replace('"ya-runtime-vm/ya-runtime-vm"', '"ya-runtime-vm/ya-runtime-vm.exe"')

    #with open(os.path.join(plugins_directory, "ya-runtime-vm.json"), "w") as fixFile:
    #    fixFile.write(text_to_fix)


#copy_file_local(os.path.join(ya_runtime_vm_directory, "target", "release", ya_runtime_vm_exe), target_runtime_exe_directory)

#if platform.system() == "Windows":
#    source_fileserver_directory = config_params["step2"]["source_fileserver_directory"]
#    target_fileserver_directory = r"plugins\ya-runtime-vm\runtime"
#    copy_file_local(os.path.join(source_fileserver_directory, "ya-vm-file-server.exe"), target_fileserver_directory)

yaprovider_exe = config_params["yaprovider_exe"]
exeunit_exe = config_params["exeunit_exe"]


source_yagna_directory = config_params["source_yagna_directory"]
target_yagna_directory = "."
copy_file_local(os.path.join(source_yagna_directory, exeunit_exe), plugins_directory)
copy_file_local(os.path.join(source_yagna_directory, yaprovider_exe), target_yagna_directory)



payment_init_command = f".{os.path.sep}{yagna_exe} payment init --receiver --network rinkeby"
print(f"Running command: {payment_init_command}")
payment_init = subprocess.Popen(payment_init_command, shell=True)

command = f".{os.path.sep}{yaprovider_exe} run"
print(f"Running command {command}")

with subprocess.Popen(command, shell=True) as p1:
    pass

