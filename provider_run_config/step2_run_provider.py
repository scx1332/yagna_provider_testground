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

yagna_exe_path = config_params["yagna_executable"]

ya_runtime_vm_directory = config_params["step2"]["ya_runtime_vm_directory"]
target_runtime_directory = r"plugins\ya-runtime-vm\runtime"

source_runtime_exe_directory = r"C:\golem\ya-runtime-vm\target\debug"
target_runtime_exe_directory = r"plugins\ya-runtime-vm"

source_fileserver_directory = r"C:\scx1332\FileServer9p\rust-9p\example\unpfs\target\release"
target_fileserver_directory = r"plugins\ya-runtime-vm\runtime"

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
    copy_file_local(os.path.join(source_fileserver_directory, "ya-vm-file-server.exe"), target_fileserver_directory)

yaprovider_exe_path = r"ya-provider.exe"



#payment_init = Popen(f"{yagna_exe_path} payment init --receiver --network rinkeby --account 0xc596aee002ebe98345ce3f967631aaf79cfbdf41", shell=True)


#with Popen(f"{yaprovider_exe_path} run", shell=True) as p1:
#    pass

