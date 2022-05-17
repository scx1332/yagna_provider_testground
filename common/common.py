import os
import shutil
import platform
import json
import subprocess


def open_config():
    if platform.system() == "Linux":
        config_path= os.path.join("..", "config_linux.json")
    else:
        config_path= os.path.join("..", "config.json")

    with open(config_path, "r") as f:
        return json.loads(f.read())


def copy_file_local(srcDir, targetDir):
    # if os.path.isfile(srcDir):
    try:
        print("Copying and overwriting file: {} => {}".format(srcDir, targetDir))
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        shutil.copy2(srcDir, targetDir)
    except Exception as e:
        print(f"ERROR: while copying file {srcDir}, reason {e}")
        raise Exception(f"ERROR: while copying file {srcDir}, reason {e}")


def _create_yagna_appkey(yagna_exe):
    command = f"{yagna_exe} app-key create auto-provider-app-key"
    print(f"Executing command {command}")

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print(out)
    pass


def _extract_yagna_appkey(yagna_exe):
    command = f"{yagna_exe} app-key list --json"
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


    if len(obj) == 0:
        raise Exception("NO KEYS FOUND")

    if len(obj) > 1:
        print("MULTIPLE KEYS FOUND, RETURNING FIRST")

    yagna_appkey = obj[0]["key"]
    print(f"Your yagna appkey: {yagna_appkey}")
    return yagna_appkey


def set_yagna_app_key_to_env(yagna_exe):
    tries = 0
    while True:
        create_app_key = False
        if tries > 3:
            raise Exception("Failed to obtain yagna key")
        try:
            yagna_app_key = _extract_yagna_appkey(yagna_exe)
            os.environ["YAGNA_APPKEY"] = yagna_app_key
            break
        except Exception as ex:
            if str(ex) == "NO KEYS FOUND":
                create_app_key = True
            else:
                raise ex

        if create_app_key:
            _create_yagna_appkey(yagna_exe)
            print("Yagna app-key created")

        tries += 1






