import os
from subprocess import Popen
import shutil

yagna_exe_path = r"yagna.exe"

source_runtime_directory = r"C:\golem\ya-runtime-vm\runtime\init-container"
target_runtime_directory = r"plugins\ya-runtime-vm\runtime"

source_runtime_exe_directory = r"C:\golem\ya-runtime-vm\target\debug"
target_runtime_exe_directory = r"plugins\ya-runtime-vm"


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

yaprovider_exe_path = r"ya-provider.exe"

payment_init = Popen(f"{yagna_exe_path} payment init --receiver --network mumbai --account 0xc596aee002ebe98345ce3f967631aaf79cfbdf41", shell=True)

p1 = Popen(f"{yaprovider_exe_path} run", shell=True)

