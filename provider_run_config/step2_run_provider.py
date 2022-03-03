import os
import subprocess
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


def create_yagna_appkey(yagna_exe):
    command = f".{os.path.sep}{yagna_exe} app-key create auto-provider-app-key"
    print(f"Executing command {command}")
    
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print(out)
    pass


def extract_yagna_appkey(yagna_exe):
    command = f".{os.path.sep}{yagna_exe} app-key list --json"
    print(f"Executing command {command}")
    
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    yagna_response = out.decode('utf-8').strip()
    yagna_error = err.decode('utf-8').strip()

    print(f"yagna_response: {yagna_response}")
    
    if yagna_error:
        print(f"yagna_error: {yagna_error}")

    if "Called service `/local/appkey/List` is unavailable" in yagna_error:
        raise Exception("Probably cannot connect to yagna service. Check if yagna service is running.")

    obj = json.loads(yagna_response)

    key_idx = obj["headers"].index("key")

    if len(obj["values"]) == 0:
        raise Exception("NO KEYS FOUND")

    if len(obj["values"]) > 1:
        print("MULTIPLE KEYS FOUND, RETURNING FIRST")

    yagna_appkey = obj["values"][0][key_idx]
    print(f"Your yagna appkey: {yagna_appkey}")
    return yagna_appkey

config_params = open_config()

yagna_exe = config_params["yagna_executable"]


create_app_key = False

tries = 0
while True:
    if tries > 3:
        raise Exception("Failed to obtain yagna key")
    try:
        yagna_app_key = extract_yagna_appkey(yagna_exe)
        break
    except Exception as ex:
        if str(ex) == "NO KEYS FOUND":
            create_app_key = True
        else:
            raise ex


    if create_app_key:
        create_yagna_appkey(yagna_exe)
        print("Yagna app-key created")

    tries += 1



ya_runtime_vm_directory = config_params["step2"]["ya_runtime_vm_directory"]

plugins_directory = "plugins"
target_runtime_directory = os.path.join("plugins", "ya-runtime-vm", "runtime")
target_runtime_exe_directory = os.path.join("plugins", "ya-runtime-vm")


def copy_file_local(srcDir, targetDir):
    # if os.path.isfile(srcDir):
    try:
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        shutil.copy2(srcDir, targetDir)
    except Exception as e:
        print(f"ERROR: while copying file {srcDir}, reason {e}")

qemu_executable = config_params["step2"]["qemu_executable"]

copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "bios-256k.bin"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "kvmvapic.bin"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", "linuxboot_dma.bin"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "poc", "runtime", qemu_executable), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "image", "self-test.gvmi"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "init-container", "initramfs.cpio.gz"), target_runtime_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "init-container", "vmlinuz-virt"), target_runtime_directory)

ya_runtime_vm_exe = config_params["ya_runtime_vm_executable"]

copy_file_local(os.path.join(ya_runtime_vm_directory, "runtime", "conf", "ya-runtime-vm.json"), plugins_directory)
copy_file_local(os.path.join(ya_runtime_vm_directory, "target", "debug", ya_runtime_vm_exe), target_runtime_exe_directory)

if platform.system() == "Windows":
    source_fileserver_directory = config_params["step2"]["source_fileserver_directory"]
    target_fileserver_directory = r"plugins\ya-runtime-vm\runtime"
    copy_file_local(os.path.join(source_fileserver_directory, "ya-vm-file-server.exe"), target_fileserver_directory)

yaprovider_exe = config_params["yaprovider_exe"]
exeunit_exe = config_params["exeunit_exe"]


source_yagna_directory = config_params["source_yagna_directory"]
target_yagna_directory = "."
copy_file_local(os.path.join(source_yagna_directory, exeunit_exe), plugins_directory)
copy_file_local(os.path.join(source_yagna_directory, yaprovider_exe), target_yagna_directory)


payment_init_command = f".{os.path.sep}{yagna_exe} payment init --receiver --network rinkeby"
print(f"Running command: {payment_init_command}")
payment_init = subprocess.Popen(payment_init_command, shell=True)

command = f".{os.path.sep}{yaprovider_exe} run --app-key {yagna_app_key}"
print(f"Running command {command}")

with subprocess.Popen(command, shell=True) as p1:
    pass

