import os
from subprocess import Popen
import shutil
import platform
import json

def open_config():
    if platform.system() == "Linux":
        config_path="config_linux.json"
    else:
        config_path="config.json"

    with open(config_path, "r") as f:
        return json.loads(f.read())

config_params = open_config()

yagna_exe = config_params["yagna_executable"]

ya_runtime_vm_directory = config_params["step2"]["ya_runtime_vm_directory"]
target_runtime_directory = r"plugins\ya-runtime-vm\runtime"

target_runtime_exe_directory = r"plugins\ya-runtime-vm"


def copy_file_local(srcDir, targetDir):
    if os.path.isfile(srcDir):
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        shutil.copy2(srcDir, targetDir)

qemu_executable = config_params["step2"]["qemu_executable"]

copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "bios-256k.bin"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "kvmvapic.bin"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "linuxboot_dma.bin"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", qemu_executable), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "image", "self-test.gvmi"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "init-container", "initramfs.cpio.gz"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "init-container", "vmlinuz-virt"), target_runtime_directory)

copy_file_local(os.path.join(ya_runtime_vm_directory, "target", "debug", "ya-runtime-vm.exe"), target_runtime_exe_directory)

if platform.system() == "Windows":
    source_fileserver_directory = config_params["step2"]["source_fileserver_directory"]
    target_fileserver_directory = r"plugins\ya-runtime-vm\runtime"
    copy_file_local(os.path.join(source_fileserver_directory, "ya-vm-file-server.exe"), target_fileserver_directory)

if platform.system() == "Windows":
    yaprovider_exe = r"ya-provider.exe"
else:
    yaprovider_exe = r"ya-provider"



payment_init_command = f".{os.path.sep}{yagna_exe} payment init --receiver --network rinkeby"
print(payment_init_command)
payment_init = Popen(payment_init_command, shell=True)


with Popen(f".{os.path.sep}{yaprovider_exe} run", shell=True) as p1:
    pass

